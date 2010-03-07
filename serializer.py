from asc import CORNER, VIRT, HORT, CORNER_CURVE_NW_SE, CORNER_CURVE_NE_SW

def make_length(width, top, curves):
    if top:
        return (curves[0] and [CORNER_CURVE_NW_SE] or [CORNER])[0] + (width - 1) * HORT + (curves[1] and [CORNER_CURVE_NE_SW] or [CORNER])[0]
    else:
        return (curves[3] and [CORNER_CURVE_NE_SW] or [CORNER])[0] + (width - 1) * HORT + (curves[2] and [CORNER_CURVE_NW_SE] or [CORNER])[0]

def serialize(gaphs, char_x, char_y):
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
    line = '#' * (int(max_x) / char_x + 1)
    for i in range(int(max_y) / char_y + 1):
        ascii.append(line)
    # overlay the canvas items
    for g in gaphs:
        x, y = g.matrix[4], g.matrix[5]
        w, h = g.width, g.height
        x = int(round(x / char_x))
        y = int(round(y / char_y))
        w = int(round(w / char_x))
        h = int(round(h / char_y))
        c = g.curves
        print x, y, w, h
        # top
        length = make_length(w, True, c)
        line = ascii[y]
        line = line[0:x] + length + line[x+w:-1]
        ascii[y] = line
        # sides
        for i in range(y + 1, y + h):
            width = '#' * (w - 1)
            line = ascii[i]
            line = line[0:x] + VIRT + width + VIRT  + line[x+w:-1]
            ascii[i] = line
        # bottom
        length = make_length(w, False, c)
        line = ascii[y+h]
        line = line[0:x] + length + line[x+w:-1]
        ascii[y+h] = line



    return ascii

