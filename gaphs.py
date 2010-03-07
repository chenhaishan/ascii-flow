from gaphas.item import Element, Item, NW, NE,SW, SE
import math

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
        # create path
        angle = 90.0  * (math.pi/180.0)
        radius = 5
        c = self.curves
        if c[0]:
            cr.arc(nw.x + radius, nw.y + radius, radius, angle * 2, angle * 3)
        else:
            cr.move_to(nw.x, nw.y)
        cr.line_to(nw.x + self.width + (c[1] and [-radius] or [0])[0], nw.y)
        if c[1]:
            cr.arc(nw.x + self.width - radius, nw.y + radius, radius, angle * 3, angle * 4)
        cr.line_to(nw.x + self.width, nw.y + self.height + (c[2] and [-radius] or [0])[0])
        if c[2]:
            cr.arc(nw.x + self.width - radius, nw.y + self.height - radius, radius, 0, angle)
        cr.line_to(nw.x + (c[3] and [radius] or [0])[0], nw.y + self.height)
        if c[3]:
            cr.arc(nw.x + radius, nw.y + self.height - radius, radius, angle, angle * 2)
        cr.line_to(nw.x, 0 + (c[0] and [radius] or [0])[0])
        # fill and stoke path
        if context.hovered:
            cr.set_source_rgba(.8, .8, 1, .8)
        else:
            cr.set_source_rgba(1, 1, 1, .8)
        cr.fill_preserve()
        cr.set_source_rgb(0, 0, 0.8)
        cr.stroke()
