
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
    line = '.' * (int(max_x) / char_x + 1)
    for i in range(int(max_y) / char_y + 1):
        ascii.append(line)
    # overlay the canvas items
    for g in gaphs:
        x, y = g.matrix[4], g.matrix[5]
        w, h = g.width, g.height
        x = int(x) / char_x
        y = int(y) / char_y
        w = int(w) / char_x
        h = int(h) / char_y
        # top
        length = '+' + (w - 1) * '-' + '+'
        line = ascii[y]
        line = line[0:x] + length + line[x+w:-1]
        ascii[y] = line
        # sides
        for i in range(y + 1, y + h):
            width = '.' * (w - 1)
            line = ascii[i]
            line = line[0:x] + '|' + width + '|'  + line[x+w:-1]
            ascii[i] = line
        # bottom
        line = ascii[y+h]
        line = line[0:x] + length + line[x+w:-1]
        ascii[y+h] = line



    return ascii

