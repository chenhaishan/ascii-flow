from gaphas.item import Element, Item, NW, NE,SW, SE
import math

from asc import *

class Box(Element):

    def __init__(self, box, canvas):
        self.positions = box.positions
        self.curves = box.curves
        # calc x, y, width & height
        x = x2 = self.positions[0][0]
        y = y2 = self.positions[0][1]
        for pos in self.positions:
            if pos[0] < x:
                x = pos[0]
            elif pos[0] > x2:
                x2 = pos[0]
            if pos[1] < y:
                y = pos[1]
            elif pos[1] > y2:
                y2 = pos[1]
        width = x2 - x + 1
        height = y2 - y + 1
        x *= CHAR_X
        y *= CHAR_Y
        width *= CHAR_X
        height *= CHAR_Y
        # initilise x, y, width & height
        super(Box, self).__init__(width, height)
        self.matrix = (1.0, 0.0, 0.0, 1.0, x, y)
        canvas.add(self)
        self.width = width
        self.height = height
        # normalise points
        pts = []
        for pos in self.positions:
            px = (pos[0] * CHAR_X - x) / float(width)
            py = (pos[1] * CHAR_Y - y) / float(height)
            pts.append((px, py))
        self.pts = pts

    def denormalise(self, pt):
        return pt[0] * self.width + CHAR_X / 2.0, pt[1] * self.height + CHAR_Y / 2.0

    def draw(self, context):
        cr = context.cairo
        # draw fill area
        nw = self._handles[NW]
        cr.set_source_rgba(0, 0, 0.8, 0.07)
        cr.rectangle(nw.x, nw.y, self.width, self.height)
        cr.fill()
        # create path
        angle = 90.0  * (math.pi/180.0)
        radius = 5
        pts = self.pts
        c = self.curves
        l = len(pts)
        for i in range(l):
            pt = self.denormalise(pts[i])
            curve = c[i]
            xoffset = 0
            yoffset = 0
            x2offset = 0
            y2offset = 0
            a1 = 0
            a2 = 0
            if i < l - 1:
                next_pt = self.denormalise(pts[i+1])
                next_curve = c[i+1]
            else:
                next_pt = self.denormalise(pts[0])
                next_curve = c[0]
            # get direction
            if next_pt[0] > pt[0]:
                dir = DIR_EAST
                if curve:
                    xoffset = radius
                if next_curve:
                    x2offset = -radius
            elif next_pt[0] < pt[0]:
                dir = DIR_WEST
                if curve:
                    xoffset = -radius
                if next_curve:
                    x2offset = radius
            elif next_pt[1] > pt[1]:
                dir = DIR_SOUTH
                if curve:
                    yoffset = radius
                if next_curve:
                    y2offset = -radius
            elif next_pt[1] < pt[1]:
                dir = DIR_NORTH
                if curve:
                    yoffset = -radius
                if next_curve:
                    y2offset = radius

            cr.line_to(pt[0] + xoffset, pt[1] + yoffset)
            cr.line_to(next_pt[0] + x2offset, next_pt[1] + y2offset)
        cr.close_path()
        # fill and stoke path
        if context.hovered:
            cr.set_source_rgba(.8, .8, 1, .8)
        else:
            cr.set_source_rgba(1, 1, 1, .8)
        cr.fill_preserve()
        cr.set_source_rgb(0, 0, 0.8)
        cr.stroke()



        
