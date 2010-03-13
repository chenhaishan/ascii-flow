class Box():

    def __init__(self, positions, curves, dashed):
        self.positions = positions
        self.curves = curves
        self.dashed = dashed

    def __str__(self):
        return "Box: positions: %s, curves: %s, dashed: %d" % (self.positions, self.curves, self.dashed)

