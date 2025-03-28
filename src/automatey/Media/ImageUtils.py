# External libraries
import cv2
import PIL
import PIL.Image
import PIL.ImageOps
import PIL.ImageEnhance
import PIL.ImageFilter
import imageio
import numpy as np
import typing

# Internal libraries
import automatey.OS.FileUtils as FileUtils
import automatey.Abstract.Graphics as AbstractGraphics
import automatey.Utils.ColorUtils as ColorUtils
import automatey.Utils.ExceptionUtils as ExceptionUtils

class INTERNAL_FrameProcessing:
    '''
    Contains wrapper(s) for different libraries, that process frame(s).
    '''

    class PillowWrapper:
        
        @staticmethod
        def brightnessContrast(imgHandler, brightness=1.0, contrast=1.0):
            '''
            Adjust brightness and contrast.
            
            Value(s) are factor(s) (i.e., '1.0' has no effect).
            '''
            brightness = float(brightness)
            contrast = float(contrast)

            if brightness != 1.0:
                imgHandler = PIL.ImageEnhance.Brightness(imgHandler).enhance(brightness)
            if contrast != 1.0:
                imgHandler = PIL.ImageEnhance.Contrast(imgHandler).enhance(contrast)
                
            return imgHandler

        @staticmethod
        def sharpen(imgHandler, factor):
            '''
            Sharpen an image.
            
            Value(s) are factor(s) (i.e., '1.0' has no effect).
            '''
            factor = float(factor)
            
            if factor != 1.0:
                imgHandler = PIL.ImageEnhance.Sharpness(imgHandler).enhance(factor)
                
            return imgHandler

        @staticmethod
        def findEdges(imgHandler):
            '''
            Finds and leaves only edges.
            '''
            imgHandler = imgHandler.filter(PIL.ImageFilter.FIND_EDGES)
            return imgHandler

        @staticmethod
        def emboss(imgHandler):
            '''
            Finds and leaves only edges.
            '''
            imgHandler = imgHandler.filter(PIL.ImageFilter.EMBOSS)
            return imgHandler

        @staticmethod
        def addBorder(imgHandler, border:AbstractGraphics.Border):
            '''
            Adds a border.
            '''
            imgHandler = PIL.ImageOps.expand(imgHandler, border=border.thickness, fill=border.color.asRGB())
            return imgHandler

    class CV2Wrapper:
        
        @staticmethod
        def createByTiling(f_list:typing.List[FileUtils.File], rowCount:int, columnCount:int):
            '''
            Create an `Image` by tiling image(s) in a grid.
            '''
            
            # ? Read image(s) from file(s).
            imgHandlers = [cv2.imread(str(f)) for f in f_list]

            # ? Tile image(s).
            rowImgHandlers = []
            for rowIdx in range(rowCount):
                startIdx = rowIdx * columnCount
                endIdx = startIdx + columnCount
                selectedImgHandlers = imgHandlers[startIdx:endIdx]
                rowImgHandler = cv2.hconcat(selectedImgHandlers)
                rowImgHandlers.append(rowImgHandler)
            tiledImgHandler = cv2.vconcat(rowImgHandlers)
            
            return tiledImgHandler
        
        @staticmethod
        def createFromFile(f:FileUtils.File):
            return cv2.imread(str(f))

        @staticmethod
        def convertRGBtoBGR(color:ColorUtils.Color):
            Rvalue, Gvalue, Bvalue = color.asRGB()
            return (Bvalue, Gvalue, Rvalue)
        
        @staticmethod
        def getDimensions(imgHandler):
            '''
            Returns a '(width, height)' tuple.
            '''
            shape  = imgHandler.shape
            return (shape[1], shape[0])

        @staticmethod
        def resize(imgHandler, width, height):
            '''
            Resize an image, given '(W, H)'.
            
            If either set to '-1', aspect ratio is preserved.
            '''
            orig_w, orig_h = INTERNAL_FrameProcessing.CV2Wrapper.getDimensions(imgHandler)
            aspectRatio = orig_w / orig_h
            
            if width == -1:
                width = int(height * aspectRatio)
            elif height == -1:
                height = int(width / aspectRatio)
            
            interpolation = cv2.INTER_AREA
            # Case: Up-scaling.
            if (width > orig_w) or (height > orig_h):
                interpolation = cv2.INTER_LANCZOS4

            imgHandler = cv2.resize(imgHandler, (width, height), interpolation=interpolation)
            return imgHandler

        @staticmethod
        def grayscale(imgHandler):
            '''
            Convert into grayscale.
            '''
            if len(imgHandler.shape) > 2:
                imgHandler = cv2.cvtColor(imgHandler, cv2.COLOR_BGR2GRAY)
            return imgHandler

        @staticmethod
        def blackWhite(imgHandler, threshold=0.5):
            '''
            Convert grayscale into black-and-white.
            
            Threshold range is (0, 1). A lower threshold leads to more white regions.
            '''
            _, imgHandler = cv2.threshold(imgHandler, int(threshold*255), 255, cv2.THRESH_BINARY)
            return imgHandler

        @staticmethod
        def invert(imgHandler):
            '''
            Invert value(s).
            '''
            imgHandler = cv2.bitwise_not(imgHandler)
            return imgHandler

        sepiaToneMatrix = np.array([[0.272, 0.534, 0.131],
                                    [0.349, 0.686, 0.168],
                                    [0.393, 0.769, 0.189]])

        @staticmethod
        def sepiaTone(imgHandler):
            '''
            Applies sepia-tone (i.e., a yellow-ish, vintage effect).
            '''
            imgHandler = cv2.transform(imgHandler, INTERNAL_FrameProcessing.CV2Wrapper.sepiaToneMatrix)
            return imgHandler

        @staticmethod
        def gaussianBlur(imgHandler, kernelSize):
            '''
            Applies gaussian blur.
            
            Kernel-size must be odd.
            '''
            imgHandler = cv2.GaussianBlur(imgHandler, (kernelSize, kernelSize), sigmaX=0)
            return imgHandler
            
        @staticmethod
        def medianBlur(imgHandler, kernelSize):
            '''
            Applies median blur.
            
            Kernel-size must be odd.
            '''
            imgHandler = cv2.medianBlur(imgHandler, ksize=kernelSize)
            return imgHandler

        @staticmethod
        def bilateralFilter(imgHandler, kernelSize):
            '''
            Applies bilateral filter.
            
            Kernel-size must be odd.
            '''
            imgHandler = cv2.bilateralFilter(imgHandler, d=kernelSize, sigmaColor=75, sigmaSpace=75)
            return imgHandler

        @staticmethod
        def pixelate(imgHandler, factor):
            '''
            Pixelate.
            
            Value(s) are factor(s) (i.e., '1.0' has no effect).
            '''
            factor = 1 / factor
            orig_w, orig_h = INTERNAL_FrameProcessing.CV2Wrapper.getDimensions(imgHandler)
            width = int(orig_w * factor)
            height = int(orig_h * factor)
            imgHandler = cv2.resize(imgHandler, (width, height), interpolation=cv2.INTER_AREA)
            imgHandler = cv2.resize(imgHandler, (orig_w, orig_h), interpolation=cv2.INTER_NEAREST)
            return imgHandler

        @staticmethod
        def crop(imgHandler, topLeft:AbstractGraphics.Point, bottomRight:AbstractGraphics.Point):
            '''
            Crop.
            
            Note that (1, 1) specifies the pixel at the top-left corner.
            '''
            x1 = topLeft.x - 1
            x2 = bottomRight.x
            
            y1 = topLeft.y - 1
            y2 = bottomRight.y
            
            imgHandler = imgHandler[y1:y2, x1:x2]
            return imgHandler
        
        @staticmethod
        def overlayRectangle(imgHandler, rectangle:AbstractGraphics.Rectangle):
            x1 = rectangle.topLeft.x - 1
            x2 = rectangle.bottomRight.x - 1
            
            y1 = rectangle.topLeft.y - 1
            y2 = rectangle.bottomRight.y - 1
            
            borderColor = INTERNAL_FrameProcessing.CV2Wrapper.convertRGBtoBGR(rectangle.border.color)
            
            if rectangle.fillColor == ColorUtils.Colors.TRANSPARENT:
                imgHandler = cv2.rectangle(imgHandler, (x1, y1), (x2, y2), borderColor, rectangle.border.thickness)
            else:
                fillColor = INTERNAL_FrameProcessing.CV2Wrapper.convertRGBtoBGR(rectangle.fillColor)
                imgHandler = cv2.rectangle(imgHandler, (x1, y1), (x2, y2), borderColor, -1)
                imgHandler = cv2.rectangle(imgHandler, 
                                        (x1+rectangle.border.thickness, y1+rectangle.border.thickness),
                                        (x2-rectangle.border.thickness, y2-rectangle.border.thickness),
                                        fillColor, -1)
                
            return imgHandler
        
        @staticmethod
        def overlayDrawable(imgHandler, shape):
            '''
            Add a drawable (e.g., Rectangle).
            '''
            fcnDict = {
                AbstractGraphics.Rectangle: INTERNAL_FrameProcessing.CV2Wrapper.overlayRectangle,
            }
            return fcnDict[type(shape)](imgHandler, shape)

        @staticmethod
        def saveAs(imgHandler, f:FileUtils.File):
            '''
            Save image, into a file.
            '''
            cv2.imwrite(str(f), imgHandler)

class INTERNAL_FrameConversion:
    '''
    Contains frame-conversion method(s) between the different frame processor(s).
    '''

    @staticmethod
    def ImageIOToPillow(imgHandler):
        return PIL.Image.fromarray(imgHandler)
    
    @staticmethod
    def PillowToImageIO(imgHandler):
        return np.array(imgHandler)

    @staticmethod
    def CV2ToPillow(imgHandler):
        return PIL.Image.fromarray(cv2.cvtColor(imgHandler, cv2.COLOR_BGR2RGB))
    
    @staticmethod
    def PillowToCV2(imgHandler):
        return cv2.cvtColor(np.array(imgHandler), cv2.COLOR_RGB2BGR)
    
    @staticmethod
    def ImageIOToCV2(imgHandler):
        return cv2.cvtColor(imgHandler, cv2.COLOR_RGB2BGR)
    
    @staticmethod
    def CV2ToImageIO(imgHandler):
        return cv2.cvtColor(imgHandler, cv2.COLOR_BGR2RGB)

# Uses 'CV2' as its format
class Image:
    '''
    Image handler.
    '''

    def __init__(self, f:FileUtils.File, INTERNAL_imgHandler=None):
        if (f != None):
            self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.createFromFile(f)
        else:
            self.imgHandler = INTERNAL_imgHandler
    
    def EXTERNAL_toCV2(self):
        '''
        Get CV2 representation.
        '''
        return self.imgHandler

    @staticmethod
    def createByTiling(f_list:typing.List[FileUtils.File], rows:int, columns:int):
        '''
        Create an `Image` by tiling image(s) in a grid.
        '''
        imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.createByTiling(f_list, rows, columns)
        return Image(None, INTERNAL_imgHandler=imgHandler)

    @staticmethod
    def INTERNAL_createFromCV2(imgHandler):
        return Image(None, INTERNAL_imgHandler=imgHandler)

    def getDimensions(self):
        '''
        Returns a '(width, height)' tuple.
        '''
        return INTERNAL_FrameProcessing.CV2Wrapper.getDimensions(self.imgHandler)

    def resize(self, width, height):
        '''
        Resize an image, given '(W, H)'.
        
        If either set to '-1', aspect ratio is preserved.
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.resize(self.imgHandler, width, height)

    def grayscale(self):
        '''
        Convert into grayscale.
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.grayscale(self.imgHandler)
        
    def blackWhite(self, threshold=0.5):
        '''
        Convert grayscale into black-and-white.
        
        Threshold range is (0, 1). A lower threshold leads to more white regions.
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.blackWhite(self.imgHandler, threshold)

    def invert(self):
        '''
        Invert value(s).
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.invert(self.imgHandler)

    def sepiaTone(self):
        '''
        Applies sepia-tone (i.e., a yellow-ish, vintage effect).
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.sepiaTone(self.imgHandler)

    def brightnessContrast(self, brightness=1.0, contrast=1.0):
        '''
        Adjust brightness and contrast.
        
        Value(s) are factor(s) (i.e., '1.0' has no effect).
        '''
        pillowImgHandler = INTERNAL_FrameConversion.CV2ToPillow(self.imgHandler)
        pillowImgHandler = INTERNAL_FrameProcessing.PillowWrapper.brightnessContrast(pillowImgHandler, brightness, contrast)
        self.imgHandler = INTERNAL_FrameConversion.PillowToCV2(pillowImgHandler)

    def gaussianBlur(self, kernelSize):
        '''
        Applies gaussian blur.
        
        Kernel-size must be odd.
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.gaussianBlur(self.imgHandler, kernelSize)
        
    def medianBlur(self, kernelSize):
        '''
        Applies median blur.
        
        Kernel-size must be odd.
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.medianBlur(self.imgHandler, kernelSize)

    def bilateralFilter(self, kernelSize):
        '''
        Applies bilateral filter.
        
        Kernel-size must be odd.
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.bilateralFilter(self.imgHandler, kernelSize)

    def sharpen(self, factor):
        '''
        Sharpen an image.
        
        Value(s) are factor(s) (i.e., '1.0' has no effect).
        '''
        pillowImgHandler = INTERNAL_FrameConversion.CV2ToPillow(self.imgHandler)
        pillowImgHandler = INTERNAL_FrameProcessing.PillowWrapper.sharpen(pillowImgHandler, factor)
        self.imgHandler = INTERNAL_FrameConversion.PillowToCV2(pillowImgHandler)
    
    def findEdges(self):
        '''
        Finds and leaves only edges.
        '''
        pillowImgHandler = INTERNAL_FrameConversion.CV2ToPillow(self.imgHandler)
        pillowImgHandler = INTERNAL_FrameProcessing.PillowWrapper.findEdges(pillowImgHandler)
        self.imgHandler = INTERNAL_FrameConversion.PillowToCV2(pillowImgHandler)

    def emboss(self):
        '''
        Emboss.
        '''
        pillowImgHandler = INTERNAL_FrameConversion.CV2ToPillow(self.imgHandler)
        pillowImgHandler = INTERNAL_FrameProcessing.PillowWrapper.emboss(pillowImgHandler)
        self.imgHandler = INTERNAL_FrameConversion.PillowToCV2(pillowImgHandler)

    def pixelate(self, factor):
        '''
        Pixelate.
        
        Value(s) are factor(s) (i.e., '1.0' has no effect).
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.pixelate(self.imgHandler, factor)

    def addBorder(self, border:AbstractGraphics.Border):
        '''
        Adds a border.
        '''
        pillowImgHandler = INTERNAL_FrameConversion.CV2ToPillow(self.imgHandler)
        pillowImgHandler = INTERNAL_FrameProcessing.PillowWrapper.addBorder(pillowImgHandler, border)
        self.imgHandler = INTERNAL_FrameConversion.PillowToCV2(pillowImgHandler)
    
    def crop(self, topLeft:AbstractGraphics.Point, bottomRight:AbstractGraphics.Point):
        '''
        Crop.
        
        Note that (1, 1) specifies the pixel at the top-left corner.
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.crop(self.imgHandler, topLeft, bottomRight)
        
    def overlayDrawable(self, shape):
        '''
        Add a drawable (e.g., Rectangle).
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.overlayDrawable(self.imgHandler, shape)
    
    def saveAs(self, f:FileUtils.File):
        '''
        Save image, into a file.
        '''
        if f.isExists():
            raise ExceptionUtils.ValidationError('Destination file must not exist.')
        INTERNAL_FrameProcessing.CV2Wrapper.saveAs(self.imgHandler, f)

    class Utils:
        
        SupportedExtensions = ['jpeg', 'jpg', 'png']
        
        @staticmethod
        def isImage(f:FileUtils.File):
            return f.getExtension() in Image.Utils.SupportedExtensions

# Uses 'ImageIO' as its format (Like CV2's, but in 'RGB' instead of 'BGR')
class GIF:
    '''
    GIF-handler.
    '''

    def __init__(self, f:FileUtils.File):
        reader = imageio.get_reader(str(f))
        self.frames = []
        totalDuration = 0
        for i, frame in enumerate(reader):
            meta = reader.get_meta_data(i)
            self.frames.append(frame)
            frameDuration = meta.get("duration", 0)
            totalDuration += frameDuration
        self.fps = len(self.frames) / (totalDuration / 1000)
    
    def getFrameCount(self):
        '''
        Get frame count.
        '''
        return len(self.frames)
    
    def getFPS(self):
        '''
        Get FPS.
        '''
        return self.fps

    def selectFrames(self, ranges):
        '''
        Select specific range(s) of frame(s).
        
        Note that backward range(s) are supported.
        
        Note that frame(s) are '1'-indexed.
        '''
        newFrames = []
        for _range in ranges:
            start = _range[0] - 1
            stop = _range[1] - 1
            step = -1 if (stop < start) else 1
            for i in range(start, (stop + step), step):
                copiedFrame = np.copy(self.frames[i])
                newFrames.append(copiedFrame)
        self.frames = newFrames

    def asImage(self, frameIdx) -> Image:
        '''
        Get a specific frame, as an 'Image'.
        
        Note that frame(s) are '1'-indexed.
        '''
        cv2ImgHandler = INTERNAL_FrameConversion.ImageIOToCV2(self.frames[frameIdx-1])
        return Image.INTERNAL_createFromCV2(cv2ImgHandler)

    def INTERNAL_CV2Applier(self, fcn, *args, **kwargs):
        for i in range(len(self.frames)):
            cv2ImgHandler = INTERNAL_FrameConversion.ImageIOToCV2(self.frames[i])
            cv2ImgHandler = fcn(cv2ImgHandler, *args, **kwargs)
            self.frames[i] = INTERNAL_FrameConversion.CV2ToImageIO(cv2ImgHandler)

    def INTERNAL_PillowApplier(self, fcn, *args, **kwargs):
        for i in range(len(self.frames)):
            pillowImgHandler = INTERNAL_FrameConversion.ImageIOToPillow(self.frames[i])
            pillowImgHandler = fcn(pillowImgHandler, *args, **kwargs)
            self.frames[i] = INTERNAL_FrameConversion.PillowToImageIO(pillowImgHandler)

    def getDimensions(self):
        '''
        Returns a '(width, height)' tuple.
        '''
        return INTERNAL_FrameProcessing.CV2Wrapper.getDimensions(self.frames[0])

    def resize(self, width, height):
        '''
        Resize an image, given '(W, H)'.
        
        If either set to '-1', aspect ratio is preserved.
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.resize, width, height)

    def grayscale(self):
        '''
        Convert into grayscale.
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.grayscale)

    def blackWhite(self, threshold=0.5):
        '''
        Convert grayscale into black-and-white.
        
        Threshold range is (0, 1). A lower threshold leads to more white regions.
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.blackWhite, threshold)

    def invert(self):
        '''
        Invert value(s).
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.invert)

    def sepiaTone(self):
        '''
        Applies sepia-tone (i.e., a yellow-ish, vintage effect).
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.sepiaTone)

    def brightnessContrast(self, brightness=1.0, contrast=1.0):
        '''
        Adjust brightness and contrast.
        
        Value(s) are factor(s) (i.e., '1.0' has no effect).
        '''
        self.INTERNAL_PillowApplier(INTERNAL_FrameProcessing.PillowWrapper.brightnessContrast, brightness, contrast)

    def gaussianBlur(self, kernelSize):
        '''
        Applies gaussian blur.
        
        Kernel-size must be odd.
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.gaussianBlur, kernelSize)
        
    def medianBlur(self, kernelSize):
        '''
        Applies median blur.
        
        Kernel-size must be odd.
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.medianBlur, kernelSize)

    def bilateralFilter(self, kernelSize):
        '''
        Applies bilateral filter.
        
        Kernel-size must be odd.
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.bilateralFilter, kernelSize)

    def sharpen(self, factor):
        '''
        Sharpen an image.
        
        Value(s) are factor(s) (i.e., '1.0' has no effect).
        '''
        self.INTERNAL_PillowApplier(INTERNAL_FrameProcessing.PillowWrapper.sharpen, factor)
    
    def findEdges(self):
        '''
        Finds and leaves only edges.
        '''
        self.INTERNAL_PillowApplier(INTERNAL_FrameProcessing.PillowWrapper.findEdges)

    def emboss(self):
        '''
        Emboss.
        '''
        self.INTERNAL_PillowApplier(INTERNAL_FrameProcessing.PillowWrapper.emboss)

    def pixelate(self, factor):
        '''
        Pixelate.
        
        Value(s) are factor(s) (i.e., '1.0' has no effect).
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.pixelate, factor)

    def addBorder(self, border:AbstractGraphics.Border):
        '''
        Adds a border.
        '''
        self.INTERNAL_PillowApplier(INTERNAL_FrameProcessing.PillowWrapper.addBorder, border)
    
    def crop(self, topLeft:AbstractGraphics.Point, bottomRight:AbstractGraphics.Point):
        '''
        Crop.
        
        Note that (1, 1) specifies the pixel at the top-left corner.
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.crop, topLeft, bottomRight)

    def overlayDrawable(self, shape):
        '''
        Add a drawable (e.g., Rectangle).
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.overlayShape, shape)
        
    def overlayDrawablePerFrame(self, callout):
        '''
        Add a drawable (e.g., Rectangle).
        
        Callout receives the current frame index (1 to FRAME-COUNT), and returns a shape.
        '''
        # Cannot use CV2Applier, must do it manually.
        for i in range(len(self.frames)):
            cv2ImgHandler = INTERNAL_FrameConversion.ImageIOToCV2(self.frames[i])
            cv2ImgHandler = INTERNAL_FrameProcessing.CV2Wrapper.overlayDrawable(cv2ImgHandler, callout(i+1))
            self.frames[i] = INTERNAL_FrameConversion.CV2ToImageIO(cv2ImgHandler)

    def saveAs(self, f:FileUtils.File, fps=None):
        '''
        Save into file.
        '''
        if f.isExists():
            raise ExceptionUtils.ValidationError('Destination file must not exist.')
        
        if fps == None:
            fps = self.fps
        
        writer = imageio.get_writer(str(f), fps=fps)
        for frame in self.frames:
            writer.append_data(frame)
        writer.close()
