from gaphas.item import Element, Item, NW, NE,SW, SE
from gaphas.connector import Handle
from gaphas.solver import VERY_STRONG
import math

from asc import *

class AsciiItem(Item):

    def init_geometry(self):
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
        # initilise x, y
        self.matrix = (1.0, 0.0, 0.0, 1.0, x, y)
        # normalise points
        pts = []
        for pos in self.positions:
            px = pos[0] * CHAR_X - x
            py = pos[1] * CHAR_Y - y
            pts.append((px, py))
        self.pts = pts

    def init_handles(self):
        self._handles = []
        for pt in self.pts:
            pt = self.renderise(pt)
            h = Handle(strength=VERY_STRONG)
            h.pos.x = pt[0]
            h.pos.y = pt[1]
            self._handles.append(h)

    def init_constraints(self):
        l = len(self._handles)
        for i in range(l):
            h = self._handles[i]
            if i < l - 1:
                next_h = self._handles[i+1]
            else:
                if not self.closed_shape:
                    return
                next_h = self._handles[0]
            if next_h.pos.x > h.pos.x or next_h.pos.x < h.pos.x:
                self.constraint(horizontal=(h.pos, next_h.pos))
            else:
                self.constraint(vertical=(h.pos, next_h.pos))


    def normalize(self):
        updated = False
        # update figure points
        for i in range(len(self.pts)):
            pt = self.pts[i]
            pt = self.renderise(pt)
            h = self._handles[i]
            if pt[0] != h.pos.x or pt[1] != h.pos.y:
                self.pts[i] = h.pos.x - CHAR_X / 2.0, h.pos.y - CHAR_Y / 2.0
                updated = True
        if updated:
            # find x/y offsets
            x, y = self.pts[0]
            for pt in self.pts:
                if pt[0] < x:
                    x = pt[0]
                if pt[1] < y:
                    y = pt[1]
            # apply any offsets
            if x or y:
                self.matrix.translate(x, y)
                for i in range(len(self.pts)):
                    self.pts[i] = self.pts[i][0] - x, self.pts[i][1] - y
                    self._handles[i].pos.x -= x
                    self._handles[i].pos.y -= y
        return updated

    def _get_width(self):
        x2 = self.pts[0][0]
        for pt in self.pts:
            if pt[0] > x2:
                x2 = pt[0]
        return x2 + CHAR_X

    width = property(_get_width)            

    def _get_height(self):
        y2 = self.pts[0][1]
        for pt in self.pts:
            if pt[1] > y2:
                y2 = pt[1]
        return y2 + CHAR_Y

    height = property(_get_height)

    def renderise(self, pt):
        return pt[0] + CHAR_X / 2.0, pt[1] + CHAR_Y / 2.0

    def draw(self, context):
        cr = context.cairo
        # draw fill area
        r, g, b, a = self.fill_area
        cr.set_source_rgba(r, g, b, a)
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()
        # create path
        angle = 90.0  * (math.pi/180.0)
        radius = 5
        pts = self.pts
        c = self.curves
        l = len(pts)
        for i in range(l):
            pt = self.renderise(pts[i])
            curve = c[i]
            xoffset = 0
            yoffset = 0
            x2offset = 0
            y2offset = 0
            a1 = 0
            a2 = 0
            if i < l - 1:
                next_pt = self.renderise(pts[i+1])
                next_curve = c[i+1]
            else:
                if not self.closed_shape:
                    break
                next_pt = self.renderise(pts[0])
                next_curve = c[0]
            # get direction
            if next_pt[0] > pt[0]:
                if curve:
                    xoffset = radius
                if next_curve:
                    x2offset = -radius
            elif next_pt[0] < pt[0]:
                if curve:
                    xoffset = -radius
                if next_curve:
                    x2offset = radius
            elif next_pt[1] > pt[1]:
                if curve:
                    yoffset = radius
                if next_curve:
                    y2offset = -radius
            elif next_pt[1] < pt[1]:
                if curve:
                    yoffset = -radius
                if next_curve:
                    y2offset = radius
            cr.line_to(pt[0] + xoffset, pt[1] + yoffset)
            cr.line_to(next_pt[0] + x2offset, next_pt[1] + y2offset)
        if self.closed_shape:
            cr.close_path()
        # fill and stoke path
        if self.closed_shape:
            if context.hovered:
                cr.set_source_rgba(.8, .8, 1, .8)
            else:
                cr.set_source_rgba(1, 1, 1, .8)
            cr.fill_preserve()
        if self.dashed:
            cr.set_dash((5, 3))
        cr.set_source_rgb(0, 0, 0.8)
        cr.stroke()

class Box(AsciiItem):

    closed_shape = True
    fill_area = (0, 0, 0.8, 0.07)

    def __init__(self, box, canvas):
        super(Box, self).__init__()
        self.positions = box.positions
        self.curves = box.curves
        self.dashed = box.dashed
        # initialize geometry
        self.init_geometry()
        # initialize handles
        self.init_handles()
        # init_geometry constraints
        self.init_constraints()
        # add to canvas
        canvas.add(self)


class Line(AsciiItem):

    closed_shape = False
    fill_area = (0, 0.8, 0.8, 0.07)

    def __init__(self, box, canvas):
        super(Line, self).__init__()
        self.positions = box.positions
        self.curves = box.curves
        self.dashed = box.dashed
        # initialize geometry
        self.init_geometry()
        # initialize handles
        self.init_handles()
        # init_geometry constraints
        self.init_constraints()
        # add to canvas
        canvas.add(self)
