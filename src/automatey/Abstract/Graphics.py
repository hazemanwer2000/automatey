
import colorsys

class Color:
    '''
    Representation of color.
    '''
    
    def __init__(self, R:int, G:int, B:int):
        self.R = R
        self.G = G
        self.B = B
    
    def asRGB(self):
        '''
        Returns RGB representation, as tuple of integers.
        '''
        return (self.R, self.G, self.B)
    
    def asHEX(self) -> str:
        '''
        Returns HEX code representation.
        '''
        return f"{self.R:02x}" + f"{self.G:02x}" + f"{self.B:02x}"
    
    def __str__(self):
        return self.asHEX()

    def __repr__(self):
        return str(self)
    
    @staticmethod
    def fromHEX(hexCode:str):
        '''
        Creates 'Color' from HEX code.
        '''
        RGBFormat = tuple(int(hexCode[i:i+2], 16) for i in (0, 2, 4))
        return Color(RGBFormat[0],
                     RGBFormat[1],
                     RGBFormat[2])
    
    @staticmethod
    def fromHSL(hue:int, saturation:int, lightness:int):
        '''
        Creates 'Color' from HSL value(s).
        
        - Hue spans 0 to 359.
        - Saturation spans 0 to 100.
        - Lightness spans 0 to 100.
        '''
        RGBFormat = colorsys.hls_to_rgb(h=hue/360, l=lightness/100, s=saturation/100)
        compuMethod = lambda x: int(x * 255)
        return Color(compuMethod(RGBFormat[0]),
                     compuMethod(RGBFormat[1]),
                     compuMethod(RGBFormat[2]))

    @staticmethod
    def fromHSB(hue:int, saturation:int, brightness:int):
        '''
        Creates 'Color' from HSL value(s).
        
        - Hue spans 0 to 359.
        - Saturation spans 0 to 100.
        - Brightness spans 0 to 100.
        '''
        RGBFormat = colorsys.hsv_to_rgb(h=hue/360, v=brightness/100, s=saturation/100)
        compuMethod = lambda x: int(x * 255)
        return Color(compuMethod(RGBFormat[0]),
                     compuMethod(RGBFormat[1]),
                     compuMethod(RGBFormat[2]))

class Colors:
    
    BLACK = Color(0, 0, 0)
    WHITE = Color(255, 255, 255)
    TRANSPARENT = None

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
    def __init__(self, thickness, color:Color):
        self.thickness = thickness
        self.color = color
        
class Shape:
    '''
    Representation of a shape.
    
    If the fill-color is 'None', the shape is internally transparent.
    '''

    def __init__(self, fillColor:Color=Colors.TRANSPARENT, border:Border=None):
        self.fillColor = fillColor
        self.border = border
        
        # For ease of processing.
        if (self.border == None):
            self.border = Border(0, self.fillColor)

class Rectangle(Shape):
    '''
    Representation of a rectangle.
    '''
    def __init__(self, topLeft:Point, bottomRight:Point, fillColor:Color=Colors.TRANSPARENT, border:Border=None):
        Shape.__init__(self, fillColor=fillColor, border=border)
        self.topLeft = topLeft
        self.bottomRight = bottomRight