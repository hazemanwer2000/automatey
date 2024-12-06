
import automatey.Base.ColorUtils as ColorUtils

class Point:
    '''
    Representation of a point.
    '''
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    
    def __add__(self, other):
        return Point(self.x - other.x, self.y - other.y)
    
class Border:
    '''
    Representation of a border.
    '''
    def __init__(self, thickness, color:ColorUtils.Color):
        self.thickness = thickness
        self.color = color
        
class Shape:
    '''
    Representation of a shape.
    
    If the fill-color is 'None', the shape is internally transparent.
    '''

    def __init__(self, fillColor:ColorUtils.Color=ColorUtils.Colors.TRANSPARENT, border:Border=None):
        self.fillColor = fillColor
        self.border = border
        
        # For ease of processing.
        if (self.border == None):
            self.border = Border(0, self.fillColor)

class Rectangle(Shape):
    '''
    Representation of a rectangle.
    '''
    def __init__(self, topLeft:Point, bottomRight:Point, fillColor:ColorUtils.Color=ColorUtils.Colors.TRANSPARENT, border:Border=None):
        Shape.__init__(self, fillColor=fillColor, border=border)
        self.topLeft = topLeft
        self.bottomRight = bottomRight