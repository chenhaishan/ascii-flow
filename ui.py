import gtk
import gaphas

import gaphs
from asc import CHAR_X, CHAR_Y

class GridPainter(gaphas.painter.Painter):

    visible = True

    def __init__(self):
        pass

    def paint(self, context):
        cr = context.cairo
        if self.visible:
            cr.save()
            # get grid drawing extents
            x1, y1, x2, y2 = cr.clip_extents()
            x1 -= x1 % CHAR_X
            y1 -= y1 % CHAR_Y
            # setup line properties
            cr.set_source_rgb(0.5, 0.5, 0.5)
            cr.set_line_width(1.0)
            # draw grid points
            for x in range(int(x1), int(x2), CHAR_X):
                for y in range(int(y1), int(y2), CHAR_Y):
                    cr.move_to(x + 0.5, y)
                    cr.line_to(x + 0.5, y + 1.0)
            cr.stroke()
            cr.restore()


def snap_to_grid(x, y, offsetx=0, offsety=0):
    # snap coords to grid
    dx = (x + offsetx) % CHAR_X
    if dx > CHAR_X / 2:
        x += CHAR_X - dx
    elif dx > 0:
        x -= dx
    dy = (y + offsety) % CHAR_Y
    if dy > CHAR_Y / 2:
        y += CHAR_Y - dy
    elif dy > 0:
        y -= dy
    return x, y

@gaphas.aspect.InMotion.when_type(gaphs.Box)
class SnapItemInMotion(object):

    def __init__(self, item, view):
        self.item = item
        self.view = view
        self.last_x, self.last_y = None, None

    def start_move(self, pos):
        self.last_x, self.last_y = snap_to_grid(pos[0], pos[1])

    def move(self, pos):
        """
        Move the item. x and y are in view coordinates.
        """
        item = self.item
        view = self.view
        v2i = view.get_matrix_v2i(item)

        pos = snap_to_grid(pos[0], pos[1], 0, 0)

        x, y = pos
        dx, dy = x - self.last_x, y - self.last_y
        dx, dy = v2i.transform_distance(dx, dy)
        self.last_x, self.last_y = x, y

        item.matrix.translate(dx, dy)
        item.canvas.request_matrix_update(item)

    def stop_move(self):
        pass

@gaphas.aspect.HandleInMotion.when_type(gaphs.Box)
class SnapHandleInMotion(object):
    GLUE_DISTANCE = 10

    def __init__(self, item, handle, view):
        self.item = item
        self.handle = handle
        self.view = view
        self.last_x, self.last_y = None, None

    def start_move(self, pos):
        self.last_x, self.last_y = snap_to_grid(pos[0], pos[1], CHAR_X / 2, CHAR_Y / 2)
        canvas = self.item.canvas

        cinfo = canvas.get_connection(self.handle)
        if cinfo:
            canvas.solver.remove_constraint(cinfo.constraint)

    def move(self, pos):
        item = self.item
        handle = self.handle
        view = self.view

        pos = snap_to_grid(pos[0], pos[1], CHAR_X / 2, CHAR_Y / 2)

        v2i = view.get_matrix_v2i(item)

        x, y = v2i.transform_point(*pos)

        self.handle.pos = (x, y)

        sink = self.glue(pos)

        # do not request matrix update as matrix recalculation will be
        # performed due to item normalization if required
        item.request_update(matrix=False)

    def stop_move(self):
        pass

    def glue(self, pos, distance=GLUE_DISTANCE):
        return None

def create_painter_chain():
    chain = gaphas.painter.PainterChain()
    chain.append(GridPainter())
    chain.append(gaphas.painter.ItemPainter())
    chain.append(gaphas.painter.HandlePainter())
    chain.append(gaphas.painter.LineSegmentPainter())
    chain.append(gaphas.painter.ToolPainter())
    return chain

def create_tool_chain():
    chain = gaphas.tool.ToolChain(). \
        append(gaphas.tool.HoverTool()). \
        append(gaphas.tool.HandleTool()). \
        append(gaphas.tool.ItemTool()). \
        append(gaphas.tool.RubberbandTool())
    return chain

class UI:

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __init__(self, canvas, save_cb):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("destroy", self.destroy)
        self.window.set_title("ascii flow")

        hbox = gtk.HBox()
        self.window.add(hbox)

        # side bar
        vbox = gtk.VBox()
        # save button
        button = gtk.Button("save")
        def click(widget):
            save_cb(canvas)
        button.connect("clicked", click)
        vbox.pack_start(button, expand=False)
        # corner checkboxes
        b = gtk.HBox()
        cb_nw = gtk.CheckButton()
        b.pack_start(cb_nw, expand=False)
        cb_ne = gtk.CheckButton()
        b.pack_start(cb_ne, expand=False)
        vbox.pack_start(b, expand=False)
        b = gtk.HBox()
        cb_sw = gtk.CheckButton()
        b.pack_start(cb_sw, expand=False)
        cb_se = gtk.CheckButton()
        b.pack_start(cb_se, expand=False)
        vbox.pack_start(b, expand=False)
        def cb_corner_toggled(cb):
            items = view.selected_items
            if items:
                for b in items:
                    if cb == cb_nw:
                        b.curves[0] = cb.get_active()
                    if cb == cb_ne:
                        b.curves[1] = cb.get_active()
                    if cb == cb_se:
                        b.curves[2] = cb.get_active()
                    if cb == cb_sw:
                        b.curves[3] = cb.get_active()
                view.queue_draw_refresh()
        cb_nw.connect("toggled", cb_corner_toggled)
        cb_ne.connect("toggled", cb_corner_toggled)
        cb_sw.connect("toggled", cb_corner_toggled)
        cb_se.connect("toggled", cb_corner_toggled)
        # dashed checkbox
        cb_dashed = gtk.CheckButton()
        vbox.pack_start(cb_dashed, expand=False)
        def cb_dashed_toggled(cb):
            items = view.selected_items
            if items:
                for b in items:
                    b.dashed = cb.get_active()
                view.queue_draw_refresh()
        cb_dashed.connect("toggled", cb_dashed_toggled)
        hbox.pack_start(vbox, expand=False)

        # gaphas view
        view = gaphas.GtkView()
        view.canvas = canvas
        view.painter = create_painter_chain()
        view.tool = create_tool_chain()
        view.set_size_request(600, 400)
        def selection_changed(view, items):
            if items:
                for b in items:
                    cb_nw.set_active(b.curves[0])
                    cb_ne.set_active(b.curves[1])
                    cb_se.set_active(b.curves[2])
                    cb_sw.set_active(b.curves[3])
                    cb_dashed.set_active(b.dashed)
                    break;
            else:
                cb_nw.set_active(False)
                cb_ne.set_active(False)
                cb_se.set_active(False)
                cb_sw.set_active(False)
                cb_dashed.set_active(False)
        view.connect("selection-changed", selection_changed)
        hbox.add(view)

        self.window.show_all()

    def main(self):
        gtk.main()



