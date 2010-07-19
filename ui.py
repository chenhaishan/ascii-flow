import gtk, pango
import gaphas
import subprocess, os

import gaphs
import options
import preprocess
import aparser
import figure
import serializer
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

@gaphas.aspect.InMotion.when_type(gaphs.AsciiItem)
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

@gaphas.aspect.HandleInMotion.when_type(gaphs.AsciiItem)
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

def load_canvas(canvas, text):
    for item in canvas.get_all_items():
        canvas.remove(item)
    ascii = preprocess.preprocess(options.Options(), text)
    figures = aparser.parse(ascii)
    for f in figures:
        if isinstance(f, figure.Box):
            gaphs.Box(f, canvas)
        elif isinstance(f, figure.Line):
            gaphs.Line(f, canvas)

class UI:

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __init__(self, filename):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("destroy", self.destroy)
        self.window.set_title("ascii flow")

        # the gaphas canvas object
        canvas = gaphas.Canvas()

        hbox = gtk.HBox()
        self.window.add(hbox)

        # side bar
        vbox = gtk.VBox()
        # save button
        button = gtk.Button("open")
        def click(widget):
            chooser = gtk.FileChooserDialog(title=None, action=gtk.FILE_CHOOSER_ACTION_OPEN,
                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            filter = gtk.FileFilter()
            filter.set_name("All Files")
            filter.add_pattern("*.txt")
            chooser.add_filter(filter)
            response = chooser.run()
            filename = chooser.get_filename()
            chooser.destroy()
            if response == gtk.RESPONSE_OK:
                if self._notebook.get_current_page() != 0:
                    self._notebook.set_current_page(0)
                    while gtk.events_pending():
                        gtk.main_iteration()
                data = open(filename, 'r').read()
                load_canvas(canvas, data)
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
                print '---'
                for b in items:
                    print b.positions
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

        # ascii view
        asciiview = gtk.TextView()
        buffer = gtk.TextBuffer()
        asciiview.set_buffer(buffer)
        pangoFont = pango.FontDescription("Courier 11")
        asciiview.modify_font(pangoFont)

        # renderview
        renderview = gtk.Image()

        # notebook
        notebook = gtk.Notebook()
        notebook.append_page(view, gtk.Label("Vectors"))
        notebook.append_page(asciiview, gtk.Label("Ascii"))
        notebook.append_page(renderview, gtk.Label("Render"))
        def switch_page(notebook, page, page_num):
            if notebook.loaded:
                # set text
                if notebook.last_page_num == 0:
                    ascii = serializer.serialize(canvas.get_all_items())
                    text = ""
                    for line in ascii:
                        text += line + "\n"
                else:
                    text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
                # init current page
                if page_num == 0:
                    # set vector view
                    load_canvas(canvas, text)
                if page_num == 1:
                    # set ascii view
                    buffer.set_text(text)
                if page_num == 2:
                    # set ascii view
                    buffer.set_text(text)
                    # set render view
                    txt_filename = ".tempfile.txt"
                    img_filename = ".tempfile.png"
                    java = r'"C:\Program Files (x86)\Java\jre6\bin\javaw.exe"'
                    open(txt_filename, "w").write(text)
                    subprocess.Popen("%s -jar ditaa0_9.jar %s -o" % (java, txt_filename)).wait()
                    renderview.set_from_file(img_filename)

            notebook.loaded = True
            notebook.last_page_num = page_num
        notebook.connect("switch-page", switch_page)
        notebook.loaded = False
        notebook.last_page_num = -1
        self._notebook = notebook

        hbox.add(notebook)

        # load file
        if filename:
            data = open(filename, 'r').read()
            load_canvas(canvas, data)

        self.window.show_all()

    def main(self):
        gtk.main()



