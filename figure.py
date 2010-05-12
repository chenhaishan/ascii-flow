class Box():

    def __init__(self, positions, curves, dashed):
        self.positions = positions
        self.curves = curves
        self.dashed = dashed

    def __str__(self):
        return "Box: positions: %s, curves: %s, dashed: %d" % (self.positions, self.curves, self.dashed)

class Line():

    def __init__(self, positions, curves, dashed, start_arrow, end_arrow):
        self.positions = positions
        self.curves = curves
        self.dashed = dashed
        self.start_arrow = start_arrow
        self.end_arrow = end_arrow

    def __str__(self):
        return "Line: positions: %s, curves: %s, dashed: %d, start_arrow: %d, end_arrow: %d" % (self.positions, self.curves, self.dashed, self.start_arrow, self.end_arrow)

