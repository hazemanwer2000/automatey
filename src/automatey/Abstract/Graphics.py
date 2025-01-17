
import automatey.Base.ColorUtils as ColorUtils

# GUI-oriented

class Margin:
    '''
    Representation of a margin.
    '''
    
    def __init__(self, top=0, left=0, bottom=0, right=0):
        self.top = top
        self.left = left
        self.bottom = bottom
        self.right = right

class SymmetricMargin(Margin):
    '''
    Representation of a symmetric margin.
    '''
    def __init__(self, value):
        Margin.__init__(self, value, value, value, value)

class Alignment:
    
    class Horizontal:
        class Left: pass
        class Right: pass
        class Center: pass
        
    class Vertical:
        class Top: pass
        class Bottom: pass
        class Center: pass

class Rotation:
    
    def __init__(self, degrees):
        while degrees < 0:
            degrees += 360
        while degrees >= 360:
            degrees -= 360
        self.degrees = degrees
    
    def __int__(self):
        return int(self.degrees)

class Mirror:
    
    class Horizontal: pass
    class Vertical: pass

# Drawable(s)

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
    
class Line:
    '''
    (2D) Representation of a line.
    '''
    def __init__(self, thickness, color:ColorUtils.Color):
        self.thickness = thickness
        self.color = color
        
class StraightLine(Line):
    '''
    (2D) Representation of a straight line.
    '''
    def __init__(self, thickness, color:ColorUtils.Color, x:Point, y:Point):
        Line.__init__(self, thickness, color)
        self.x = x
        self.y = y
    
class Border:
    '''
    (2D) Representation of a border.
    '''
    def __init__(self, thickness, color:ColorUtils.Color):
        self.thickness = thickness
        self.color = color
        
class Shape:
    '''
    (2D) Representation of a shape.
    
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
    (2D) Representation of a rectangle.
    '''
    def __init__(self, topLeft:Point, bottomRight:Point, fillColor:ColorUtils.Color=ColorUtils.Colors.TRANSPARENT, border:Border=None):
        Shape.__init__(self, fillColor=fillColor, border=border)
        self.topLeft = topLeft
        self.bottomRight = bottomRight

# Text.

class TextStyle:
    '''
    Styling of text.
    '''
    def __init__(self, isItalic:bool=False, isBold:bool=False):
        self.isItalic = isItalic
        self.isBold = isBold

class TextColor:
    '''
    Coloring of text.
    '''
    def __init__(self, foreground:ColorUtils.Color, background:ColorUtils.Color):
        self.foreground = foreground
        self.background = background
