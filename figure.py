
class Figure:

    def __init__(self, x = 10, y = 10, width = 10, height = 10):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __str__(self):
        return "Figure: x %d, y %d, width %d, height %d" % (self.x, self.y, self.width, self.height)

class Box(Figure):

    def __init__(self, x = 10, y = 10, width = 10, height = 10):
        Figure.__init__(self, x, y, width, height)

    def __str__(self):
        return "Box " + Figure.__str__(self)

if __name__ == "__main__":
    b = Box()
    print b
            
