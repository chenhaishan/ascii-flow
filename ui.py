import gtk
import gaphas

import gaphs

class GridPainter(gaphas.painter.Painter):

    visible = True

    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y

    def paint(self, context):
        cr = context.cairo
        if self.visible:
            cr.save()
            # get grid drawing extents
            x1, y1, x2, y2 = cr.clip_extents()
            x1 -= x1 % self.grid_x
            y1 -= y1 % self.grid_y
            # setup line properties
            cr.set_source_rgb(0.5, 0.5, 0.5)
            cr.set_line_width(1.0)
            # draw grid points
            for x in range(x1, x2, self.grid_x):
                for y in range(y1, y2, self.grid_y):
                    cr.move_to(x + 0.5, y)
                    cr.line_to(x + 0.5, y + 1.0)
            cr.stroke()
            cr.restore()

def dit_painter(grid_x, grid_y):
    chain = gaphas.painter.PainterChain()
    chain.append(GridPainter(grid_x, grid_y))
    chain.append(gaphas.painter.ItemPainter())
    chain.append(gaphas.painter.HandlePainter())
    chain.append(gaphas.painter.LineSegmentPainter())
    chain.append(gaphas.painter.ToolPainter())
    return chain

class UI:

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __init__(self, canvas, save_cb, grid_x, grid_y):
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
        hbox.pack_start(vbox, expand=False)

        # gaphas view
        view = gaphas.GtkView()
        view.canvas = canvas
        view.painter = dit_painter(grid_x, grid_y)
        view.set_size_request(600, 400)
        hbox.add(view)

        self.window.show_all()

    def main(self):
        gtk.main()



