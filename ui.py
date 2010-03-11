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


class ItemTool(gaphas.tool.ItemTool):

    def on_motion_notify(self, event):
        """
        Normally do nothing.
        If a button is pressed move the items around (with snap to grid).
        """
        if event.state & gtk.gdk.BUTTON_PRESS_MASK:

            pt = snap_to_grid(event.x, event.y)

            if not self._movable_items:
                self._movable_items = set(self.movable_items())
                for inmotion in self._movable_items:
                    inmotion.start_move(pt)

            for inmotion in self._movable_items:
                inmotion.move(pt)

            return True

class HandleTool(gaphas.tool.HandleTool):

    def on_motion_notify(self, event):
        """
        Handle motion events. If a handle is grabbed: drag it around,
        else, if the pointer is over a handle, make the owning item the
        hovered-item.
        """
        view = self.view
        if self.grabbed_handle and event.state & gtk.gdk.BUTTON_PRESS_MASK:
            canvas = view.canvas
            item = self.grabbed_item
            handle = self.grabbed_handle
            pos = snap_to_grid(event.x, event.y, CHAR_X / 2, CHAR_Y / 2)

            if not self.motion_handle:
                self.motion_handle = gaphas.tool.HandleInMotion(item, handle, self.view)
                self.motion_handle.start_move(pos)
            self.motion_handle.move(pos)

            return True        

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
        append(HandleTool()). \
        append(ItemTool()). \
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
        button = gtk.Button("save")
        def click(widget):
            save_cb(canvas)
        button.connect("clicked", click)
        vbox.pack_start(button, expand=False)
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
        def toggled(cb):
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
        cb_nw.connect("toggled", toggled)
        cb_ne.connect("toggled", toggled)
        cb_sw.connect("toggled", toggled)
        cb_se.connect("toggled", toggled)
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
                    break;
            else:
                cb_nw.set_active(False)
                cb_ne.set_active(False)
                cb_se.set_active(False)
                cb_sw.set_active(False)
        view.connect("selection-changed", selection_changed)
        hbox.add(view)

        self.window.show_all()

    def main(self):
        gtk.main()



