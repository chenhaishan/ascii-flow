from asc import *

def get_direction(pt1, pt2):
    if pt2[0] > pt1[0]:
        return DIR_EAST
    elif pt2[0] < pt1[0]:
        return DIR_WEST
    elif pt2[1] > pt1[1]:
        return DIR_SOUTH
    elif pt2[1] < pt1[1]:
        return DIR_NORTH

def choose_corner(dir, pt1, pt2, curve):
    if curve:
        dir2 = get_direction(pt1, pt2)
        if dir == DIR_EAST:
            if dir2 == DIR_SOUTH:
                return CORNER_CURVE_NE_SW
            else:
                return CORNER_CURVE_NW_SE
        elif dir == DIR_WEST:
            if dir2 == DIR_SOUTH:
                return CORNER_CURVE_NW_SE
            else:
                return CORNER_CURVE_NE_SW
        elif dir == DIR_SOUTH:
            if dir2 == DIR_EAST:
                return CORNER_CURVE_NE_SW
            else:
                return CORNER_CURVE_NW_SE
        elif dir == DIR_NORTH:
            if dir2 == DIR_EAST:
                return CORNER_CURVE_NE_SW
            else:
                return CORNER_CURVE_NW_SE
    return CORNER

def fill_char(ascii, dir, pt1, pt2, corner2, line_char):
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
        x += xmod
        y += ymod
        # write box side char
        ascii[y][x] = line_char
    # write box corner char
    x, y = pt2
    ascii[y][x] = corner2

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
        line = ['#'] * (int(max_x) / CHAR_X)
        ascii.append(line)
    # overlay the canvas items
    for g in gaphs:
        # initialise loops vars
        x, y = g.matrix[4], g.matrix[5]
        w, h = g.width, g.height
        x = int(round(x / CHAR_X))
        y = int(round(y / CHAR_Y))
        w = int(round(w / CHAR_X))
        h = int(round(h / CHAR_Y))
        c = g.curves
        l = len(g.pts)
        for i in range(l):
            # initialise loop vars
            pt1 = g.pts[i]
            if i < l - 1:
                pt2 = g.pts[i+1]
                curve = g.curves[i+1]
            else:
                pt2 = g.pts[0] 
                curve = g.curves[0]
            if i < l - 2:
                pt3 = g.pts[i+2]
            else:
                pt3 = g.pts[l-i-1]
            # normalise to char positions
            pt1 = int(pt1[0] + g.matrix[4]) / CHAR_X, int(pt1[1] + g.matrix[5]) / CHAR_Y
            pt2 = int(pt2[0] + g.matrix[4]) / CHAR_X, int(pt2[1] + g.matrix[5]) / CHAR_Y
            pt3 = int(pt3[0] + g.matrix[4]) / CHAR_X, int(pt3[1] + g.matrix[5]) / CHAR_Y
            # write box side
            dir = get_direction(pt1, pt2)
            if dir == DIR_WEST or dir == DIR_EAST:
                fill_char(ascii, dir, pt1, pt2, choose_corner(dir, pt2, pt3, curve), HORT)
            else:
                fill_char(ascii, dir, pt1, pt2, choose_corner(dir, pt2, pt3, curve), VIRT)
    # convert line char arrays to strings
    for i in range(len(ascii)):
        ascii[i] = "".join(ascii[i])
    return ascii

