from gaphas.item import Element, Item, NW, NE,SW, SE

class Box(Element):
    """ A Box has 4 handles (for a start):
     NW +---+ NE
     SW +---+ SE
    """

    def __init__(self, width = 10, height = 10):
        super(Box, self).__init__(width, height)
        print "box", self.width, self.height

    def draw(self, context):
        cr = context.cairo
        nw = self._handles[NW]
        cr.rectangle(nw.x, nw.y, self.width, self.height)
        if context.hovered:
            cr.set_source_rgba(.8, .8, 1, .8)
        else:
            cr.set_source_rgba(1, 1, 1, .8)
        cr.fill_preserve()
        cr.set_source_rgb(0, 0, 0.8)
        cr.stroke()
