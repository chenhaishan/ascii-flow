class Box():

    def __init__(self, positions, curves):
        self.positions = positions
        self.curves = curves

    def __str__(self):
        return "Box: positions: %s, curves: %s" % (self.positions, self.curves)

