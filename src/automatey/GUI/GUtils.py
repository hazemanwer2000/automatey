
# External libraries
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui
from PyQt6.QtCore import Qt

# Internal libraries
import automatey.OS.FileUtils as FileUtils
import automatey.Media.ImageUtils as ImageUtils

class GImage:
    '''
    Image, may be used with all element(s) of the GUI.
    '''
    
    def __init__(self, img:ImageUtils.Image, size=None):
        super().__init__()
        
        cv2ImgHandler = img.EXTERNAL_toCV2()
        
        # ? Handling size.
        originalSize = [cv2ImgHandler.shape[1], cv2ImgHandler.shape[0]]
        if size != None:
            aspectRatio = originalSize[0] / originalSize[1]
            if size[0] == -1:
                size[0] = int(aspectRatio * size[1])
            elif size[1] == -1:
                size[1] = int(size[0] / aspectRatio)
       
        # PyQt: Derriving image.
        self.qImage = QtGui.QImage(cv2ImgHandler.data, originalSize[0], originalSize[1], QtGui.QImage.Format.Format_RGB888).rgbSwapped()
        if size != None:
            self.qImage = self.qImage.scaled(size[0], size[1], Qt.AspectRatioMode.IgnoreAspectRatio)
            
    def INTERNAL_toQImage(self):
        return self.qImage

class GIcon:
    '''
    Icon, may be used with all element(s) of the GUI.
    '''
    
    def __init__(self, qIcon:QtGui.QIcon):
        self.qIcon = qIcon
    
    @staticmethod
    def GCreateFromFile(f:FileUtils.File):
        '''
        Create from file.
        '''
        return None
    
    @staticmethod
    def GCreateFromLibrary(standardIcon):
        '''
        Creates an Icon from the library (i.e., a standard icon).
        '''
        return GIcon(QtWidgets.QApplication.instance().style().standardIcon(standardIcon.qStandardIcon))

    class GStandardIcon:

        class FileSave:
            qStandardIcon = QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton

        class MediaPlay:
            qStandardIcon = QtWidgets.QStyle.StandardPixmap.SP_MediaPlay
        class MediaPause:
            qStandardIcon = QtWidgets.QStyle.StandardPixmap.SP_MediaPause
        class MediaStop:
            qStandardIcon = QtWidgets.QStyle.StandardPixmap.SP_MediaStop
        class MediaSeekForward:
            qStandardIcon = QtWidgets.QStyle.StandardPixmap.SP_MediaSeekForward
        class MediaSeekBackward:
            qStandardIcon = QtWidgets.QStyle.StandardPixmap.SP_MediaSeekBackward
