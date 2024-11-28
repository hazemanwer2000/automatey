
import PIL.ImageEnhance
import PIL.ImageOps
import cv2
from automatey.FileUtils import File
import PIL
import numpy as np
import imageio

class INTERNAL:

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
        def addBorder(imgHandler, size, color):
            '''
            Adds a border.
            
            Color must be in '(R, G, B)' format.
            '''
            imgHandler = PIL.ImageOps.expand(imgHandler, border=size, fill=color)
            return imgHandler

    class CV2Wrapper:
        
        @staticmethod
        def createFromFile(f:File):
            return cv2.imread(str(f))
        
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
            orig_w, orig_h = INTERNAL.CV2Wrapper.getDimensions(imgHandler)
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
            imgHandler = cv2.transform(imgHandler, INTERNAL.CV2Wrapper.sepiaToneMatrix)
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
            orig_w, orig_h = INTERNAL.CV2Wrapper.getDimensions(imgHandler)
            width = int(orig_w * factor)
            height = int(orig_h * factor)
            imgHandler = cv2.resize(imgHandler, (width, height), interpolation=cv2.INTER_AREA)
            imgHandler = cv2.resize(imgHandler, (orig_w, orig_h), interpolation=cv2.INTER_NEAREST)
            return imgHandler

        @staticmethod
        def saveAs(imgHandler, f:File):
            '''
            Save image, into a file.
            '''
            cv2.imwrite(str(f), imgHandler)

class Color:
    Black = (0, 0, 0)
    White = (255, 255, 255)

# Uses 'CV2' as its format
class Image:
    '''
    Image handler.
    '''

    def __init__(self, f:File):
        self.imgHandler = INTERNAL.CV2Wrapper.createFromFile(f)

    def getDimensions(self):
        '''
        Returns a '(width, height)' tuple.
        '''
        return INTERNAL.CV2Wrapper.getDimensions(self.imgHandler)

    def resize(self, width, height):
        '''
        Resize an image, given '(W, H)'.
        
        If either set to '-1', aspect ratio is preserved.
        '''
        self.imgHandler = INTERNAL.CV2Wrapper.resize(self.imgHandler, width, height)

    def grayscale(self):
        '''
        Convert into grayscale.
        '''
        self.imgHandler = INTERNAL.CV2Wrapper.grayscale(self.imgHandler)
        
    def blackWhite(self, threshold=0.5):
        '''
        Convert grayscale into black-and-white.
        
        Threshold range is (0, 1). A lower threshold leads to more white regions.
        '''
        self.imgHandler = INTERNAL.CV2Wrapper.blackWhite(self.imgHandler, threshold)

    def invert(self):
        self.imgHandler = INTERNAL.CV2Wrapper.invert(self.imgHandler)

    def sepiaTone(self):
        '''
        Applies sepia-tone (i.e., a yellow-ish, vintage effect).
        '''
        self.imgHandler = INTERNAL.CV2Wrapper.sepiaTone(self.imgHandler)

    def brightnessContrast(self, brightness=1.0, contrast=1.0):
        '''
        Adjust brightness and contrast.
        
        Value(s) are factor(s) (i.e., '1.0' has no effect).
        '''
        pillowImgHandler = INTERNAL.CV2ToPillow(self.imgHandler)
        pillowImgHandler = INTERNAL.PillowWrapper.brightnessContrast(pillowImgHandler, brightness, contrast)
        self.imgHandler = INTERNAL.PillowToCV2(pillowImgHandler)

    def gaussianBlur(self, kernelSize):
        '''
        Applies gaussian blur.
        
        Kernel-size must be odd.
        '''
        self.imgHandler = INTERNAL.CV2Wrapper.gaussianBlur(self.imgHandler, kernelSize)
        
    def medianBlur(self, kernelSize):
        '''
        Applies median blur.
        
        Kernel-size must be odd.
        '''
        self.imgHandler = INTERNAL.CV2Wrapper.medianBlur(self.imgHandler, kernelSize)

    def bilateralFilter(self, kernelSize):
        '''
        Applies bilateral filter.
        
        Kernel-size must be odd.
        '''
        self.imgHandler = INTERNAL.CV2Wrapper.bilateralFilter(self.imgHandler, kernelSize)

    def sharpen(self, factor):
        '''
        Sharpen an image.
        
        Value(s) are factor(s) (i.e., '1.0' has no effect).
        '''
        pillowImgHandler = INTERNAL.CV2ToPillow(self.imgHandler)
        pillowImgHandler = INTERNAL.PillowWrapper.sharpen(pillowImgHandler, factor)
        self.imgHandler = INTERNAL.PillowToCV2(pillowImgHandler)
    
    def findEdges(self):
        '''
        Finds and leaves only edges.
        '''
        pillowImgHandler = INTERNAL.CV2ToPillow(self.imgHandler)
        pillowImgHandler = INTERNAL.PillowWrapper.findEdges(pillowImgHandler)
        self.imgHandler = INTERNAL.PillowToCV2(pillowImgHandler)

    def emboss(self):
        '''
        Emboss.
        '''
        pillowImgHandler = INTERNAL.CV2ToPillow(self.imgHandler)
        pillowImgHandler = INTERNAL.PillowWrapper.emboss(pillowImgHandler)
        self.imgHandler = INTERNAL.PillowToCV2(pillowImgHandler)

    def pixelate(self, factor):
        '''
        Pixelate.
        
        Value(s) are factor(s) (i.e., '1.0' has no effect).
        '''
        self.imgHandler = INTERNAL.CV2Wrapper.pixelate(self.imgHandler, factor)

    def addBorder(self, size, color):
        '''
        Adds a border.
        
        Color must be in '(R, G, B)' format.
        '''
        pillowImgHandler = INTERNAL.CV2ToPillow(self.imgHandler)
        pillowImgHandler = INTERNAL.PillowWrapper.addBorder(pillowImgHandler)
        self.imgHandler = INTERNAL.PillowToCV2(pillowImgHandler)
    
    def saveAs(self, f:File):
        '''
        Save image, into a file.
        '''
        INTERNAL.CV2Wrapper.saveAs(self.imgHandler, f)

    class Utils:
        
        SupportedExtensions = ['jpeg', 'jpg', 'png']
        
        @staticmethod
        def isImage(f:File):
            return f.getExtension() in Image.Utils.SupportedExtensions

# Uses 'ImageIO' as its format (Like CV2's, but in 'RGB' instead of 'BGR')
class GIF:

    def __init__(self, f:File):
        reader = imageio.get_reader(str(f))
        self.frames = []
        self.totalDuration = 0
        for i, frame in enumerate(reader):
            meta = reader.get_meta_data(i)
            self.frames.append(frame)
            frameDuration = meta.get("duration", 0)
            self.totalDuration += frameDuration

    def getTotalDuration(self):
        '''
        Get total duration, in 'ms'.
        '''
        return self.totalDuration
    
    def getFrameCount(self):
        '''
        Get frame count.
        '''
        return len(self.frames)
    
    def getFPS(self):
        '''
        Get FPS.
        '''
        return self.getFrameCount() / (self.getTotalDuration() / 1000)

    def __CV2Applier(self, fcn, *args, **kwargs):
        for i in range(len(self.frames)):
            cv2ImgHandler = INTERNAL.ImageIOToCV2(self.frames[i])
            cv2ImgHandler = fcn(cv2ImgHandler, *args, **kwargs)
            self.frames[i] = INTERNAL.CV2ToImageIO(cv2ImgHandler)

    def __PillowApplier(self, fcn, *args, **kwargs):
        for i in range(len(self.frames)):
            pillowImgHandler = INTERNAL.ImageIOToPillow(self.frames[i])
            pillowImgHandler = fcn(pillowImgHandler, *args, **kwargs)
            self.frames[i] = INTERNAL.PillowToImageIO(pillowImgHandler)

    def getDimensions(self):
        '''
        Returns a '(width, height)' tuple.
        '''
        return INTERNAL.CV2Wrapper.getDimensions(self.frames[0])

    def resize(self, width, height):
        '''
        Resize an image, given '(W, H)'.
        
        If either set to '-1', aspect ratio is preserved.
        '''
        self.__CV2Applier(INTERNAL.CV2Wrapper.resize, width, height)

    def grayscale(self):
        '''
        Convert into grayscale.
        '''
        self.__CV2Applier(INTERNAL.CV2Wrapper.grayscale)

    def blackWhite(self, threshold=0.5):
        '''
        Convert grayscale into black-and-white.
        
        Threshold range is (0, 1). A lower threshold leads to more white regions.
        '''
        self.__CV2Applier(INTERNAL.CV2Wrapper.blackWhite, threshold)

    def invert(self):
        self.__CV2Applier(INTERNAL.CV2Wrapper.invert)

    def sepiaTone(self):
        '''
        Applies sepia-tone (i.e., a yellow-ish, vintage effect).
        '''
        self.__CV2Applier(INTERNAL.CV2Wrapper.sepiaTone)

    def brightnessContrast(self, brightness=1.0, contrast=1.0):
        '''
        Adjust brightness and contrast.
        
        Value(s) are factor(s) (i.e., '1.0' has no effect).
        '''
        self.__PillowApplier(INTERNAL.PillowWrapper.brightnessContrast, brightness, contrast)

    def gaussianBlur(self, kernelSize):
        '''
        Applies gaussian blur.
        
        Kernel-size must be odd.
        '''
        self.__CV2Applier(INTERNAL.CV2Wrapper.gaussianBlur, kernelSize)
        
    def medianBlur(self, kernelSize):
        '''
        Applies median blur.
        
        Kernel-size must be odd.
        '''
        self.__CV2Applier(INTERNAL.CV2Wrapper.medianBlur, kernelSize)

    def bilateralFilter(self, kernelSize):
        '''
        Applies bilateral filter.
        
        Kernel-size must be odd.
        '''
        self.__CV2Applier(INTERNAL.CV2Wrapper.bilateralFilter, kernelSize)

    def sharpen(self, factor):
        '''
        Sharpen an image.
        
        Value(s) are factor(s) (i.e., '1.0' has no effect).
        '''
        self.__PillowApplier(INTERNAL.PillowWrapper.sharpen, factor)
    
    def findEdges(self):
        '''
        Finds and leaves only edges.
        '''
        self.__PillowApplier(INTERNAL.PillowWrapper.findEdges)

    def emboss(self):
        '''
        Emboss.
        '''
        self.__PillowApplier(INTERNAL.PillowWrapper.emboss)

    def pixelate(self, factor):
        '''
        Pixelate.
        
        Value(s) are factor(s) (i.e., '1.0' has no effect).
        '''
        self.__CV2Applier(INTERNAL.CV2Wrapper.pixelate, factor)

    def addBorder(self, size, color):
        '''
        Adds a border.
        
        Color must be in '(R, G, B)' format.
        '''
        self.__PillowApplier(INTERNAL.PillowWrapper.addBorder, size, color)
    
    def saveAs(self, f:File, fps=None):
        '''
        Save into file.
        '''
        if fps == None:
            fps = self.getFPS()
        
        writer = imageio.get_writer(str(f), fps=fps)
        for frame in self.frames:
            writer.append_data(frame)
        writer.close()