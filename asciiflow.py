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
from asc import CHAR_X, CHAR_Y

options = options.Options()

filename = sys.argv[1]
data = open(filename, 'r').read()
ascii = preprocess.preprocess(options, data)
figures = aparser.parse(ascii)

def save(canvas):
    ascii = serializer.serialize(canvas.get_all_items())
    text = ''
    print '**********'
    print ''
    for line in ascii:
        print line
        text = text + line + '\n'
    open('testout.txt', 'w').write(text)

def setup_canvas(figures):
    canvas = gaphas.Canvas()

    for f in figures:
        b = gaphs.Box(f, canvas)

    return canvas

canvas = setup_canvas(figures)
ui = ui.UI(canvas, save)
ui.main()


