# python standard libs
import sys

# 3rd party libs
import gaphas

# dit libs
import options
import preprocess
import aparser
import serializer
import gaphs
import ui

char_x = 8
char_y = 16

options = options.Options()

filename = sys.argv[1]
data = open(filename, 'r').read()
ascii = preprocess.preprocess(options, data)
figures = aparser.parse(ascii)

def save(canvas):
    global char_x, char_y
    ascii = serializer.serialize(canvas.get_all_items(), char_x, char_y)
    text = ''
    print '**********'
    print ''
    for line in ascii:
        print line
        text = text + line + '\n'
    open('testout.txt', 'w').write(text)

def setup_canvas(figures, char_x, char_y):
    canvas = gaphas.Canvas()

    for f in figures:
        b = gaphs.Box()
        b.matrix = (1.0, 0.0, 0.0, 1.0, f.x * char_x, f.y * char_y)
        canvas.add(b)
        b.width = f.width * char_x
        b.height = f.height * char_y

    return canvas

canvas = setup_canvas(figures, char_x, char_y)
ui = ui.UI(canvas, save, char_x, char_y)
ui.main()


