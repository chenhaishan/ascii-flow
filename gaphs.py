from gaphas.item import Element, Item, NW, NE,SW, SE
import math

from asc import CHAR_X, CHAR_Y

class Box(Element):
    """ A Box has 4 handles (for a start):
     NW +---+ NE
     SW +---+ SE
    """

    def __init__(self, width=10, height=10, curves=None):
        super(Box, self).__init__(width, height)
        if curves:
            self.curves = curves
        else:
            self.curves = [0, 0, 0, 0]

    def draw(self, context):
        cr = context.cairo
        nw = self._handles[NW]
        x = nw.x + CHAR_X / 2
        y = nw.y + CHAR_Y / 2
        w = self.width - CHAR_X
        h = self.height - CHAR_Y
        # create path
        angle = 90.0  * (math.pi/180.0)
        radius = 5
        c = self.curves
        if c[0]:
            cr.arc(x + radius, y + radius, radius, angle * 2, angle * 3)
        else:
            cr.move_to(x, y)
        cr.line_to(x + w + (c[1] and [-radius] or [0])[0], y)
        if c[1]:
            cr.arc(x + w - radius, y + radius, radius, angle * 3, angle * 4)
        cr.line_to(x + w, y + h + (c[2] and [-radius] or [0])[0])
        if c[2]:
            cr.arc(x + w - radius, y + h - radius, radius, 0, angle)
        cr.line_to(x + (c[3] and [radius] or [0])[0], y + h)
        if c[3]:
            cr.arc(x + radius, y + h - radius, radius, angle, angle * 2)
        cr.line_to(x, y + (c[0] and [radius] or [0])[0])
        # fill and stoke path
        if context.hovered:
            cr.set_source_rgba(.8, .8, 1, .8)
        else:
            cr.set_source_rgba(1, 1, 1, .8)
        cr.fill_preserve()
        cr.set_source_rgb(0, 0, 0.8)
        cr.stroke()

        
