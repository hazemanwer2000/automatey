
import PIL.ImageEnhance
import cv2
from automatey.FileUtils import File
import automatey.MathUtils as MathUtils
import PIL
import numpy as np

class BlurType:
    class GaussianBlur: pass
    class MedianBlur: pass
    class BilateralFilter: pass

class Image:
    '''
    Image handler.
    '''
  
    def __init__(self, f:File):
        self.imgHandler = cv2.imread(str(f))

    def getDimensions(self):
        '''
        Returns a '(width, height)' tuple.
        '''
        height, width, _  = self.imgHandler.shape
        return (width, height)
    
    def grayscale(self):
        '''
        Convert into grayscale.
        '''
        if len(self.imgHandler.shape) > 2:
            self.imgHandler = cv2.cvtColor(self.imgHandler, cv2.COLOR_BGR2GRAY)
        
    def blackWhite(self, threshold):
        '''
        Convert grayscale into black-and-white.
        
        Threshold range is (0, 1). A lower threshold leads to more white regions.
        '''
        _, self.imgHandler = cv2.threshold(self.imgHandler, int(threshold*255), 255, cv2.THRESH_BINARY)
    
    def brightnessContrast(self, brightness=1.0, contrast=1.0):
        '''
        Adjust brightness and contrast.
        
        Value(s) are factor(s) (i.e., '1.0' has no effect).
        '''
        brightness = float(brightness)
        contrast = float(contrast)
        
        pillowImgHandler = Image.__CV2ToPillow(self.imgHandler)
        
        if brightness != 1.0:
            pillowImgHandler = PIL.ImageEnhance.Brightness(pillowImgHandler).enhance(brightness)
        if contrast != 1.0:
            pillowImgHandler = PIL.ImageEnhance.Contrast(pillowImgHandler).enhance(contrast)
        
        self.imgHandler = Image.__PillowToCV2(pillowImgHandler)

    def __gaussianBlur(self, kernelSize):
        self.imgHandler = cv2.GaussianBlur(self.imgHandler, (kernelSize, kernelSize), sigmaX=0)
        
    def __medianBlur(self, kernelSize):
        self.imgHandler = cv2.medianBlur(self.imgHandler, ksize=kernelSize)

    def __bilateralFilter(self, kernelSize):
        self.imgHandler = cv2.bilateralFilter(self.imgHandler, d=kernelSize, sigmaColor=75, sigmaSpace=75)

    def blur(self, blurType, kernelSize):
        '''
        Blur an image. Kernel-size must be odd.
        '''
        fcnMap = {
            BlurType.GaussianBlur: self.__gaussianBlur,
            BlurType.MedianBlur: self.__medianBlur,
            BlurType.BilateralFilter: self.__bilateralFilter
        }
        fcnMap[blurType](kernelSize)

    def sharpen(self, factor):
        '''
        Sharpen an image.
        
        Value(s) are factor(s) (i.e., '1.0' has no effect).
        '''
        factor = float(factor)
        
        pillowImgHandler = Image.__CV2ToPillow(self.imgHandler)
        
        if factor != 1.0:
            pillowImgHandler = PIL.ImageEnhance.Sharpness(pillowImgHandler).enhance(factor)
        
        self.imgHandler = Image.__PillowToCV2(pillowImgHandler)
    
    def saveAs(self, f:File):
        '''
        Save image, into a file.
        '''
        cv2.imwrite(str(f), self.imgHandler)
        
    @staticmethod
    def __CV2ToPillow(imgHandler):
        return PIL.Image.fromarray(cv2.cvtColor(imgHandler, cv2.COLOR_BGR2RGB))
    
    @staticmethod
    def __PillowToCV2(imgHandler):
        return cv2.cvtColor(np.array(imgHandler), cv2.COLOR_RGB2BGR)
    
    class Utils:
        
        SupportedExtensions = ['jpeg', 'jpg', 'png']
        
        @staticmethod
        def isImage(f:File):
            return f.getExtension() in Image.Utils.SupportedExtensions