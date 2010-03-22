import figure
from asc import *

#
# Helper functions
#

def increment_position(pos, dir):
    x, y = pos
    if dir == DIR_EAST:
        x += 1
    elif dir == DIR_SOUTH:
        y += 1
    elif dir == DIR_WEST:
        x -= 1
    elif dir == DIR_NORTH:
        y -= 1
    return (x, y)

def check_position_valid(ascii, pos):
    x, y = pos
    if x < 0 or y < 0:
        return False
    if y >= len(ascii):
        return False
    if x >= len(ascii[y]):
        return False
    return True

def get_next_char(ascii, pos, dir):
    pos = increment_position(pos, dir)
    if check_position_valid(ascii, pos):
        x, y = pos
        char = ascii[y][x]
        return pos, char
    return pos, None

def is_corner(char):
    return char == CORNER or char == CORNER_CURVE_NW_SE or char == CORNER_CURVE_NE_SW

def is_curved_corner(char):
    return char == CORNER_CURVE_NE_SW or char == CORNER_CURVE_NW_SE

def is_hort(char):
    return char == HORT or char == HORT_DASH

def is_vert(char):
    return char == VERT or char == VERT_DASH

def is_dashed(char):
    return char == HORT_DASH or char == VERT_DASH

def is_line_end(char):
    return char == LINE_EAST or char == LINE_WEST or char == LINE_SOUTH or char == LINE_SOUTH2 or char == LINE_NORTH

#
# Recursive box search methods
#

def box_search_another_corner(ascii, pos, char, positions, curves, prev_dir, dashed, candidate_stack):
    # check if we have visited this position before
    if pos in positions:
        # check if we have finished the box
        if pos == positions[0]:
            return [positions, curves, dashed]
        # otherwise back up 
        if candidate_stack:
            # rewind candidate stack
            candidates = candidate_stack[-1:][0]
            pos, dir, new_pos, char = candidates.pop()
            if len(candidates) == 0:
                candidate_stack.pop()
            # rewind positions & curves
            while pos != positions[-1:][0]:
                positions.pop()
                curves.pop()
            # retry traval
            return box_search_side_travel(ascii, new_pos, char, positions, curves, dir, dashed, candidate_stack)
        return None
    # add new position to the mix
    positions.append(pos)
    curves.append(is_curved_corner(char))
    # try relevant directions
    if prev_dir == DIR_EAST: directions = [DIR_SOUTH, DIR_EAST, DIR_NORTH]
    if prev_dir == DIR_WEST: directions = [DIR_NORTH, DIR_WEST, DIR_SOUTH]
    if prev_dir == DIR_NORTH: directions = [DIR_EAST, DIR_NORTH, DIR_WEST]
    if prev_dir == DIR_SOUTH: directions = [DIR_WEST, DIR_SOUTH, DIR_EAST]
    candidates = []
    for dir in directions:
        new_pos, char = get_next_char(ascii, pos, dir)
        if ((dir == DIR_EAST or dir == DIR_WEST) and is_hort(char)) or \
           ((dir == DIR_SOUTH or dir == DIR_NORTH) and is_vert(char)) or \
           is_corner(char):
            candidates.append((pos, dir, new_pos, char))
    if candidates:
        pos, dir, new_pos, char = candidates[0]
        del candidates[0]
        if candidates:
            candidate_stack.append(candidates)
        return box_search_side_travel(ascii, new_pos, char, positions, curves, dir, dashed, candidate_stack)
    return None

def box_search_side_travel(ascii, pos, char, positions, curves, dir, dashed, candidate_stack):
    new_pos = pos
    if (dir == DIR_EAST or dir == DIR_WEST) and is_hort(char):
        while is_hort(char):
            dashed = dashed or is_dashed(char)
            new_pos, char = get_next_char(ascii, new_pos, dir)
        if is_corner(char):
            return box_search_another_corner(ascii, new_pos, char, positions, curves, dir, dashed, candidate_stack)
    elif (dir == DIR_NORTH or dir == DIR_SOUTH) and is_vert(char):
        while is_vert(char):
            dashed = dashed or is_dashed(char)
            new_pos, char = get_next_char(ascii, new_pos, dir)
        if is_corner(char):
            return box_search_another_corner(ascii, new_pos, char, positions, curves, dir, dashed, candidate_stack)
    elif is_corner(char):
        return box_search_another_corner(ascii, new_pos, char, positions, curves, dir, dashed, candidate_stack)
    return None

def box_search_start_corner(ascii, pos, char):
    boxes = []
    # search in all directions
    for dir in (DIR_EAST, DIR_SOUTH, DIR_WEST, DIR_NORTH):
        box = box_search_another_corner(ascii, pos, char, [], [], dir, False, [])
        if box:
            boxes.append(box)
    # reorient
    orient_boxes(boxes)
    return boxes

#
# box orientation
#

def orient_to_top_left(box):
    # find top left position
    topleft_pos = box[0][0]
    for pos in box[0]:
        if pos[1] < topleft_pos[1]:
            topleft_pos = pos
        elif pos[0] < topleft_pos[0]:
            topleft_pos = pos
    # orient to top left
    i = box[0].index(topleft_pos)
    box[0] = box[0][i:] + box[0][:i]
    box[1] = box[1][i:] + box[1][:i]

def orient_boxes(boxes):
    for i in range(len(boxes)):
        orient_to_top_left(boxes[i])

#
# find boxes
#

def find_boxes(ascii, pos):
    boxes = []
    x, y = pos
    char = ascii[y][x]
    # check if current position is the start of a box
    if is_corner(char):
        boxes = box_search_start_corner(ascii, pos, char)
    return boxes


#
# line search functions
#

def line_search_another_corner(ascii, pos, char, positions, curves, prev_dir, dashed, candidate_stack):
    # check if we have visited this position before
    if pos in positions:
        # check if we have finished the box
        if pos == positions[0]:
            return [positions, curves, dashed]
        # otherwise back up 
        if candidate_stack:
            # rewind candidate stack
            candidates = candidate_stack[-1:][0]
            pos, dir, new_pos, char = candidates.pop()
            if len(candidates) == 0:
                candidate_stack.pop()
            # rewind positions & curves
            while pos != positions[-1:][0]:
                positions.pop()
                curves.pop()
            # retry traval
            return line_search_side_travel(ascii, new_pos, char, positions, curves, dir, dashed, candidate_stack)
        return None
    # add new position to the mix
    positions.append(pos)
    curves.append(is_curved_corner(char))
    # try relevant directions
    if prev_dir == DIR_EAST: directions = [DIR_SOUTH, DIR_EAST, DIR_NORTH]
    if prev_dir == DIR_WEST: directions = [DIR_NORTH, DIR_WEST, DIR_SOUTH]
    if prev_dir == DIR_NORTH: directions = [DIR_EAST, DIR_NORTH, DIR_WEST]
    if prev_dir == DIR_SOUTH: directions = [DIR_WEST, DIR_SOUTH, DIR_EAST]
    candidates = []
    for dir in directions:
        new_pos, char = get_next_char(ascii, pos, dir)
        if ((dir == DIR_EAST or dir == DIR_WEST) and is_hort(char)) or \
           ((dir == DIR_SOUTH or dir == DIR_NORTH) and is_vert(char)) or \
           is_corner(char):
            candidates.append((pos, dir, new_pos, char))
    if candidates:
        pos, dir, new_pos, char = candidates[0]
        del candidates[0]
        if candidates:
            candidate_stack.append(candidates)
        return line_search_side_travel(ascii, new_pos, char, positions, curves, dir, dashed, candidate_stack)
    return None

def line_search_side_travel(ascii, pos, char, positions, curves, dir, dashed, candidate_stack):
    new_pos = pos
    last_pos = pos
    if (dir == DIR_EAST or dir == DIR_WEST) and is_hort(char):
        while is_hort(char):
            dashed = dashed or is_dashed(char)
            last_pos = new_pos
            new_pos, char = get_next_char(ascii, new_pos, dir)
        if is_corner(char):
            return line_search_another_corner(ascii, new_pos, char, positions, curves, dir, dashed, candidate_stack)
    elif (dir == DIR_NORTH or dir == DIR_SOUTH) and is_vert(char):
        while is_vert(char):
            dashed = dashed or is_dashed(char)
            last_pos = new_pos
            new_pos, char = get_next_char(ascii, new_pos, dir)
        if is_corner(char):
            return line_search_another_corner(ascii, new_pos, char, positions, curves, dir, dashed, candidate_stack)
    elif is_corner(char):
        return line_search_another_corner(ascii, new_pos, char, positions, curves, dir, dashed, candidate_stack)
    # return line as is
    positions.append(last_pos)
    curves.append(False)
    return [positions, curves, dashed]

def line_start(ascii, pos, char):
    lines = []
    # search north/south
    if is_vert(char):
        for dir in (DIR_NORTH, DIR_SOUTH):
            line = line_search_side_travel(ascii, pos, char, [pos], [False], dir, False, [])
            if line:
                lines.append(line)
    # search east/west
    elif is_hort(char):
        for dir in (DIR_EAST, DIR_WEST):
            line = line_search_side_travel(ascii, pos, char, [pos], [False], dir, False, [])
            if line:
                lines.append(line)
    # search all directions
    elif is_line_end(char):
        for dir in (DIR_EAST, DIR_SOUTH, DIR_WEST, DIR_NORTH):
            line = line_search_another_corner(ascii, pos, char, [pos], [False], dir, False, [])
            if line:
                lines.append(line)
    return lines

#
# find lines
#

def find_lines(ascii, pos):
    lines = []
    x, y = pos
    char = ascii[y][x]
    # check if current position is the start of a line
    if is_vert(char) or is_hort(char) or is_line_end(char):
        lines = line_start(ascii, pos, char)
    return lines

#
# box duplicate removal
#
        
def remove_dupes(boxes):
    for i in range(len(boxes)-1, 0, -1):
        box = boxes[i]
        for j in range(i):
            box_compare = boxes[j]
            if len(box[0]) != len(box_compare[0]):
                continue
            remove = True
            for pos in box[0]:
                if not pos in box_compare[0]:
                    remove = False
                    break
            if remove:
                boxes.remove(box)
                break

#
# redundant super boxes removal
#

def pos_in_box_a(box, pos):
    # if the point is shared with the box then it is deemed inside
    if pos in box:
       return 1 
    return False

def pos_in_box_b(box, pos):
    #
    # We try a basic crossing number algo
    # (for our basic right angled boxes)
    #

    # crossing number counter
    cn = 0
    # x & y
    x, y = pos
    #
    # We dont want to use concurrent vertical sections if the first one was used
    # for example the point (*) below would hit the two vertical wall sections
    # ruining the result
    #
    #           +
    #           |
    #  pt -> *  +
    #           |
    #           +
    #
    crossed_last_time = 0 
    # We also want to ignore the second cross in cases like so:
    #
    #           +
    #           |
    #  pt -> *  +--+
    #              |
    #              +
    #
    # But trigger a cross twice in cases like so:
    #
    #           +  +
    #           |  |
    #  pt -> *  +--+
    #              
    crossed_vertex_last_time = 0
    crossed_vertex_dir = 0
    # start the crossing number method
    for i in range(len(box)):
        # find next box edge (x1,y1 <--> x2,y2)
        x1, y1 = box[i]
        if i < len(box)-1:
            x2, y2 = box[i+1]
        else:
            x2, y2 = box[0]
        # check if ray cast from x,y and heading east will cross the edge
        if y2 != y1 and not crossed_last_time:
            if y >= y1 and y <= y2 or y <= y1 and y >= y2:
                if x < x1: # x1 & x2 are the same here
                    if y == y1 or y == y2:
                        if crossed_vertex_last_time:
                            if crossed_vertex_dir == y2 > y1:
                                crossed_vertex_last_time = False
                                continue
                        crossed_vertex_last_time = True
                        crossed_vertex_dir = y2 > y1
                    crossed_last_time = True
                    cn += 1
            else:
                last_cross_y = -1
        else:
            crossed_last_time = False
    # return true if the crossing number counter is odd
    return cn % 2

def box_contains(box1, box2):
    # does box1 contain box2
    for pos in box2:
        if not pos_in_box_a(box1, pos) and not pos_in_box_b(box1, pos):
            return False
    return True

def box_shares_a_border(box1, box2):
    # does box1 share at least one border with box2
    for i in range(len(box1)):
        # iterate through box1 borders
        b1pt1 = box1[i]
        if i < len(box1)-1:
            b1pt2 = box1[i+1]
        else:
            b1pt2 = box1[0]
        # iterate through box2 borders
        for j in range(len(box2)):
            b2pt1 = box2[j]
            if j < len(box2)-1:
                b2pt2 = box2[j+1]
            else:
                b2pt2 = box2[0]
            # check if the borders match
            if b1pt1 == b2pt1 and b1pt2 == b2pt2 or b1pt1 == b2pt2 and b1pt2 == b2pt1:
                return True
    return False

def remove_redundant_boxes(boxes):
    # redundant boxes are those that contain smaller boxes and also share at least one border with them
    redo = True
    while redo:
        redo = False
        for i in range(len(boxes)-1, 0, -1):
            box = boxes[i]
            for j in range(i):
                box_compare = boxes[j]
                if box_contains(box[0], box_compare[0]):
                    if box_shares_a_border(box[0], box_compare[0]):
                        boxes.remove(box)
                        break
                elif box_contains(box_compare[0], box[0]):
                    if box_shares_a_border(box_compare[0], box[0]):
                        boxes.remove(box_compare)
                        # now we must start from the beginning because we have changed the array order
                        redo = True;
                        break
            if redo:
                break

#
# redunant lines removal
#

def pos_in_line(line, pos):
    for i in range(len(line)-1):
        pos_a = line[i]
        pos_b = line[i+1]
        if pos_a[0] == pos_b[0]:
            # vertical line segment
            if pos[0] == pos_a[0] and pos[0] == pos_b[0]:
                # pos x == line segment x
                if pos_b[1] > pos_a[1]:
                    # heading south
                    if pos[1] >= pos_a[1] and pos[1] <= pos_b[1]:
                        return True
                else:
                    # heading north
                    if pos[1] <= pos_a[1] and pos[1] >= pos_b[1]:
                        return True
        else:
            # hortizontal line segment
            if pos[1] == pos_a[1] and pos[1] == pos_b[1]:
                # pos y == line segment y
                if pos_b[0] > pos_a[0]:
                    # heading east
                    if pos[0] >= pos_a[0] and pos[0] <= pos_b[0]:
                        return True
                else:
                    # heading west
                    if pos[0] <= pos_a[0] and pos[0] >= pos_b[0]:
                        return True
    return False

def line_contains(line1, line2):
    for pos in line2:
        if not pos in line1 and not pos_in_line(line1, pos):
            return False
    return True

def remove_redundant_lines(lines):
    # redundant lines are those that overlap with larger lines
    redo = True
    while redo:
        redo = False
        for i in range(len(lines)-1, 0, -1):
            line = lines[i]
            for j in range(i):
                line_compare = lines[j]
                if line_contains(line_compare[0], line[0]):
                    lines.remove(line)
                    break
                elif line_contains(line[0], line_compare[0]):
                    lines.remove(line_compare)
                    # now we must start from the beginning because we have changed the array order
                    redo = True;
                    break
            if redo:
                break

#
# box simplification
#

def simplify(boxes):
    # here we want to get rid of redundant vertexes
    for box in boxes:
        for i in range(len(box[0])-1, 0, -1):
            pos = box[0][i]
            remove = False
            if i > 0:
                prev_pos = box[0][i-1]
            else:
                prev_pos = box[0][len(box[0])-1]
            if i < len(box[0])-1:
                next_pos = box[0][i+1]
            else:
                next_pos = box[0][0]
            if prev_pos[0] == pos[0] and pos[0] == next_pos[0]:
                remove = True
            elif prev_pos[1] == pos[1] and pos[1] == next_pos[1]:
                remove = True
            if remove:
                del box[0][i]
                del box[1][i]
    pass
    
## Search for boxes using a left to right, top to bottom method
#  @param ascii A list of text lines 
#  @return A list of boxes
def parse(ascii):
    figures = []
    #
    # boxes
    #
    boxes = []
    for i in range(len(ascii)):
        line = ascii[i]
        for j in range(len(line)):
            new_boxes = find_boxes(ascii, (j, i))
            for box in new_boxes:
                boxes.append(box)
    # remove dupes
    remove_dupes(boxes)
    # remove redundants
    remove_redundant_boxes(boxes)
    # simplify boxes
    simplify(boxes)
    # create figures
    for box in boxes:
        figures.append(figure.Box(box[0], box[1], box[2]))
    #
    # lines
    #
    lines = []
    for i in range(len(ascii)):
        line = ascii[i]
        for j in range(len(line)):
            new_lines = find_lines(ascii, (j, i))
            for line in new_lines:
                lines.append(line)
    # remove dupes
    remove_dupes(lines)
    # remove redundants
    remove_redundant_lines(lines)
    # simplify boxes
    #simplify(lines)
    # create figures
    for line in lines:
        figures.append(figure.Line(line[0], line[1], line[2]))
        print line
    return figures
