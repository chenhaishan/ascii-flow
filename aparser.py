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

def is_virt(char):
    return char == VIRT or char == VIRT_DASH

def is_dashed(char):
    return char == HORT_DASH or char == VIRT_DASH

#
# Recursive box search methods
#

def another_corner(ascii, pos, char, positions, curves, prev_dir, dashed, candidate_stack):
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
            return travel(positions, curves, dir, ascii, new_pos, char, dashed, candidate_stack)
        return None
    # add new position to the mix
    positions.append(pos)
    curves.append(is_curved_corner(char))
    # try relevant directions
    directions = [DIR_EAST, DIR_WEST, DIR_NORTH, DIR_SOUTH]
    if prev_dir == DIR_EAST: directions.remove(DIR_WEST)
    if prev_dir == DIR_WEST: directions.remove(DIR_EAST)
    if prev_dir == DIR_NORTH: directions.remove(DIR_SOUTH)
    if prev_dir == DIR_SOUTH: directions.remove(DIR_NORTH)
    candidates = []
    for dir in directions:
        new_pos, char = get_next_char(ascii, pos, dir)
        if ((dir == DIR_EAST or dir == DIR_WEST) and is_hort(char)) or \
           ((dir == DIR_SOUTH or dir == DIR_NORTH) and is_virt(char)) or \
           is_corner(char):
            candidates.append((pos, dir, new_pos, char))
    if candidates:
        pos, dir, new_pos, char = candidates[0]
        del candidates[0]
        if candidates:
            candidate_stack.append(candidates)
        return travel(positions, curves, dir, ascii, new_pos, char, dashed, candidate_stack)
    return None

def travel(positions, curves, dir, ascii, pos, char, dashed, candidate_stack):
    new_pos = pos
    if (dir == DIR_EAST or dir == DIR_WEST) and is_hort(char):
        while is_hort(char):
            dashed = dashed or is_dashed(char)
            new_pos, char = get_next_char(ascii, new_pos, dir)
        if is_corner(char):
            return another_corner(ascii, new_pos, char, positions, curves, dir, dashed, candidate_stack)
    elif (dir == DIR_NORTH or dir == DIR_SOUTH) and is_virt(char):
        while is_virt(char):
            dashed = dashed or is_dashed(char)
            new_pos, char = get_next_char(ascii, new_pos, dir)
        if is_corner(char):
            return another_corner(ascii, new_pos, char, positions, curves, dir, dashed, candidate_stack)
    elif is_corner(char):
        return another_corner(ascii, new_pos, char, positions, curves, dir, dashed, candidate_stack)
    return None

def start_corner(ascii, pos, char):
    boxes = []
    # try all directions
    for dir in [DIR_EAST, DIR_SOUTH, DIR_WEST, DIR_NORTH]:
        positions = [pos]
        curves = [is_curved_corner(char)]
        new_pos, new_char = get_next_char(ascii, pos, dir)
        if new_char:
            box = travel(positions, curves, dir, ascii, new_pos, new_char, False, [])
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

def find_boxes(ascii, pos):
    boxes = []
    x, y = pos
    line = ascii[y]
    char = line[x]
    # check if current position is the start of a box
    if is_corner(char):
        boxes = start_corner(ascii, pos, char)
    return boxes

#
# box duplicate removal
#
        
def remove_dupes(boxes):
    for i in range(len(boxes)-1, 0, -1):
        box = boxes[i]
        for j in range(i):
            box_compare = boxes[j]
            remove = True
            for pos in box[0]:
                if not pos in box_compare[0]:
                    remove = False
                    break;
            if remove:
                boxes.remove(box)
                break
    
## Search for boxes using a left to right, top to bottom method
#  @param ascii A list of text lines 
#  @return A list of boxes
def parse(ascii):
    boxes = []
    for i in range(len(ascii)):
        line = ascii[i]
        for j in range(len(line)):
            new_boxes = find_boxes(ascii, (j, i))
            for box in new_boxes:
                boxes.append(box)

    # remove dupes
    remove_dupes(boxes)
    # create figures
    figures = []
    for box in boxes:
        figures.append(figure.Box(box[0], box[1], box[2]))
    return figures
