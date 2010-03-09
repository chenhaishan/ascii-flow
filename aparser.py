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

#
# Recursive search methods
#

def another_corner(ascii, pos, char, positions, curves, prev_dir):
    positions.append(pos)
    curves.append(is_curved_corner(char))
    # check if we have finished the box
    pos_start, pos_end = positions[0], positions[-1:][0]
    if pos_start[0] == pos_end[0] and pos_start[1] == pos_end[1]:
        return [positions[:-1], curves[:-1]]
    # try relevant directions
    directions = []
    if prev_dir == DIR_EAST or prev_dir == DIR_WEST:
        directions = [DIR_NORTH, DIR_SOUTH]
    else:
        directions = [DIR_EAST, DIR_WEST]
    for dir in directions:
        new_pos, char = get_next_char(ascii, pos, dir)
        if char == VIRT or char == HORT:
           return travel(positions, curves, dir, ascii, new_pos, char)
    return None

def travel(positions, curves, dir, ascii, pos, char):
    new_pos = pos
    if (dir == DIR_EAST or dir == DIR_WEST) and char == HORT:
        while char == HORT:
            new_pos, char = get_next_char(ascii, new_pos, dir)
        if is_corner(char):
            return another_corner(ascii, new_pos, char, positions, curves, dir)
    elif (dir == DIR_NORTH or dir == DIR_SOUTH) and char == VIRT:
        while char == VIRT:
            new_pos, char = get_next_char(ascii, new_pos, dir)
        if is_corner(char):
            return another_corner(ascii, new_pos, char, positions, curves, dir)
    return None

def start_corner(ascii, pos, char):
    boxes = []
    # try all directions
    for dir in [DIR_EAST, DIR_SOUTH, DIR_WEST, DIR_NORTH]:
        positions = [pos]
        curves = [is_curved_corner(char)]
        new_pos, new_char = get_next_char(ascii, pos, dir)
        if new_char:
            box = travel(positions, curves, dir, ascii, new_pos, new_char)
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
                #del boxes[i]
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
        figures.append(figure.Box(box[0], box[1]))
    return figures
