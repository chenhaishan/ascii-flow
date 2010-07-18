from asc import *
from gaphs import Box, Line

def get_direction(pt1, pt2):
    if pt2[0] > pt1[0]:
        return DIR_EAST
    elif pt2[0] < pt1[0]:
        return DIR_WEST
    elif pt2[1] > pt1[1]:
        return DIR_SOUTH
    elif pt2[1] < pt1[1]:
        return DIR_NORTH

def choose_corner(dir1, dir2, curve):
    if curve:
        if dir1 == DIR_EAST:
            if dir2 == DIR_SOUTH:
                return CORNER_CURVE_NE_SW
            else:
                return CORNER_CURVE_NW_SE
        elif dir1 == DIR_WEST:
            if dir2 == DIR_SOUTH:
                return CORNER_CURVE_NW_SE
            else:
                return CORNER_CURVE_NE_SW
        elif dir1 == DIR_SOUTH:
            if dir2 == DIR_EAST:
                return CORNER_CURVE_NE_SW
            else:
                return CORNER_CURVE_NW_SE
        elif dir1 == DIR_NORTH:
            if dir2 == DIR_EAST:
                return CORNER_CURVE_NW_SE
            else:
                return CORNER_CURVE_NE_SW
    return CORNER

def choose_arrow(dir):
    if dir == DIR_EAST:
        return LINE_WEST
    if dir == DIR_WEST:
        return LINE_EAST
    if dir == DIR_SOUTH:
        return LINE_NORTH
    if dir == DIR_NORTH:
        return LINE_SOUTH

def reverse_dir(dir):
    if dir == DIR_EAST:
        return DIR_WEST
    if dir == DIR_WEST:
        return DIR_EAST
    if dir == DIR_SOUTH:
        return DIR_NORTH
    if dir == DIR_NORTH:
        return DIR_SOUTH

def fill_char(ascii, dir, pt1, pt2, corner2, line_char, line_char_dash, dashed, do_initial_char = False, do_corner_char = True):
    x, y = pt1
    xmod = ymod = 0
    if dir == DIR_WEST:
        xmod = -1
    elif dir == DIR_EAST:
        xmod = 1
    if dir == DIR_NORTH:
        ymod = -1
    elif dir == DIR_SOUTH:
        ymod = 1
    while x != pt2[0] or y != pt2[1]:
        # write initial side char
        if do_initial_char:
            if dashed:
                ascii[y][x] = line_char_dash
                dashed = False
            else:
                ascii[y][x] = line_char
        # increment coord
        x += xmod
        y += ymod
        # write side char
        if dashed:
            ascii[y][x] = line_char_dash
            dashed = False
        else:
            ascii[y][x] = line_char
    # write corner char
    if do_corner_char:
        x, y = pt2
        ascii[y][x] = corner2

def serialise_box(ascii, g):
    l = len(g.pts)
    for i in range(l):
        # initialise points
        pt1 = g.pts[i]
        if i < l - 1:
            pt2 = g.pts[i+1]
            curve = g.curves[i+1]
        else:
            pt2 = g.pts[0] 
            curve = g.curves[0]
        if i < l - 2:
            pt3 = g.pts[i+2]
        elif i < l - 1:
            pt3 = g.pts[0]
        else:
            pt3 = g.pts[1]
        # normalise to char positions
        pt1 = int(pt1[0] + g.matrix[4]) / CHAR_X, int(pt1[1] + g.matrix[5]) / CHAR_Y
        pt2 = int(pt2[0] + g.matrix[4]) / CHAR_X, int(pt2[1] + g.matrix[5]) / CHAR_Y
        pt3 = int(pt3[0] + g.matrix[4]) / CHAR_X, int(pt3[1] + g.matrix[5]) / CHAR_Y
        # write box side
        dir = get_direction(pt1, pt2)
        dir2 = get_direction(pt2, pt3)
        if dir == DIR_WEST or dir == DIR_EAST:
            fill_char(ascii, dir, pt1, pt2, choose_corner(dir, dir2, curve), HORT, HORT_DASH, g.dashed)
        else:
            fill_char(ascii, dir, pt1, pt2, choose_corner(dir, dir2, curve), VERT, VERT_DASH, g.dashed)

def serialise_line(ascii, g):
    l = len(g.pts)
    for i in range(l - 1):
        # initialise points
        pt1 = g.pts[i]
        pt2 = g.pts[i+1]
        pt3 = None
        if i < l - 2:
            pt3 = g.pts[i+2]
        curve = g.curves[i+1]
        # normalise to char positions
        pt1 = int(pt1[0] + g.matrix[4]) / CHAR_X, int(pt1[1] + g.matrix[5]) / CHAR_Y
        pt2 = int(pt2[0] + g.matrix[4]) / CHAR_X, int(pt2[1] + g.matrix[5]) / CHAR_Y
        if pt3:
            pt3 = int(pt3[0] + g.matrix[4]) / CHAR_X, int(pt3[1] + g.matrix[5]) / CHAR_Y
        # write line segment
        dir = get_direction(pt1, pt2)
        dir2 = 0
        if pt3:
            dir2 = get_direction(pt2, pt3)
        if dir == DIR_WEST or dir == DIR_EAST:
            fill_char(ascii, dir, pt1, pt2, choose_corner(dir, dir2, curve), HORT, HORT_DASH, g.dashed, i == 0, i != l-2)
        else:
            fill_char(ascii, dir, pt1, pt2, choose_corner(dir, dir2, curve), VERT, VERT_DASH, g.dashed, i == 0, i != l-2)
        # write line arrow heads
        if i == 0 and g.start_arrow:
            char = choose_arrow(dir)
            x, y = pt1
            ascii[y][x] = char
        if i == l - 2 and g.end_arrow:
            char = choose_arrow(reverse_dir(dir))
            x, y = pt2
            ascii[y][x] = char

def serialize(gaphs):
    ascii = []
    # find extents of canvas items
    max_x, max_y = 0, 0
    for g in gaphs:
        x, y = g.matrix[4], g.matrix[5]
        w, h = g.width, g.height
        x2 = x + w
        y2 = y + h
        if x2 > max_x:
            max_x = x2
        if y2 > max_y:
            max_y = y2
    # build base char canvas
    for i in range(int(max_y) / CHAR_Y):
        line = [' '] * (int(max_x) / CHAR_X)
        ascii.append(line)
    # overlay the canvas items
    for g in gaphs:
        if isinstance(g, Box):
            serialise_box(ascii, g)
        if isinstance(g, Line):
            serialise_line(ascii, g)
    # convert line char arrays to strings
    for i in range(len(ascii)):
        ascii[i] = "".join(ascii[i])
    return ascii

