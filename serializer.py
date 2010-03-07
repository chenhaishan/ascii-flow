from asc import CORNER, VIRT, HORT, CORNER_CURVE_NW_SE, CORNER_CURVE_NE_SW, CHAR_X, CHAR_Y

def make_length(width, top, curves):
    if top:
        return (curves[0] and [CORNER_CURVE_NW_SE] or [CORNER])[0] + (width - 2) * HORT + (curves[1] and [CORNER_CURVE_NE_SW] or [CORNER])[0]
    else:
        return (curves[3] and [CORNER_CURVE_NE_SW] or [CORNER])[0] + (width - 2) * HORT + (curves[2] and [CORNER_CURVE_NW_SE] or [CORNER])[0]

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
    line = '#' * (int(max_x) / CHAR_X + 1)
    for i in range(int(max_y) / CHAR_Y + 1):
        ascii.append(line)
    # overlay the canvas items
    for g in gaphs:
        x, y = g.matrix[4], g.matrix[5]
        w, h = g.width, g.height
        x = int(round(x / CHAR_X))
        y = int(round(y / CHAR_Y))
        w = int(round(w / CHAR_X))
        h = int(round(h / CHAR_Y))
        c = g.curves
        # top
        length = make_length(w, True, c)
        line = ascii[y]
        line = line[0:x] + length + line[x+w:]
        ascii[y] = line
        # sides
        for i in range(y + 1, y + h - 1):
            width = '#' * (w - 2)
            line = ascii[i]
            line = line[0:x] + VIRT + width + VIRT  + line[x+w:]
            ascii[i] = line
        # bottom
        length = make_length(w, False, c)
        line = ascii[y+h-1]
        line = line[0:x] + length + line[x+w:]
        ascii[y+h-1] = line



    return ascii

