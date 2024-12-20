
# External libraries
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui
import PyQt6.QtCore as QtCore

# Internal libraries
import automatey.OS.FileUtils as FileUtils
import automatey.Media.ImageUtils as ImageUtils

class Image:
    '''
    Image, may be used with all element(s) of the GUI.
    '''
    
    def __init__(self, img:ImageUtils.Image, size=None):
        
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
            self.qImage = self.qImage.scaled(size[0], size[1], QtCore.Qt.AspectRatioMode.IgnoreAspectRatio)

class Icon:
    '''
    Icon, may be used with all element(s) of the GUI.
    '''
    
    def __init__(self, qIcon:QtGui.QIcon, size=None):
        self.qIcon = qIcon
        self.size = size
    
    @staticmethod
    def createFromFile(f:FileUtils.File, size=None):
        '''
        Create from file.
        '''
        return Icon(QtGui.QIcon(str(f)), size=size)
    
    @staticmethod
    def createFromLibrary(standardIcon, size=None):
        '''
        Creates an Icon from the library (i.e., a standard icon).
        '''
        return Icon(QtWidgets.QApplication.instance().style().standardIcon(standardIcon.qStandardIcon), size=size)

    class GStandardIcon:

        class FileSave:
            qStandardIcon = QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton
        class FileOpen:
            qStandardIcon = QtWidgets.QStyle.StandardPixmap.SP_DirIcon

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
        class MediaVolume:
            qStandardIcon = QtWidgets.QStyle.StandardPixmap.SP_MediaVolume
        class MediaVolumeMute:
            qStandardIcon = QtWidgets.QStyle.StandardPixmap.SP_MediaVolumeMuted

        class ScrollUp:
            qStandardIcon = QtWidgets.QStyle.StandardPixmap.SP_TitleBarShadeButton
        class ScrollDown:
            qStandardIcon = QtWidgets.QStyle.StandardPixmap.SP_TitleBarUnshadeButton

class GEventHandler:
    
    def __init__(self, fcn):
        self.fcn = fcn

class GEventHandlers:
    '''
    Different event-handler(s).
    
    Note,
    - All expect no argument(s), except otherwise specified.
    '''
    
    class GClickEventHandler(GEventHandler):
        pass

    class GSelectionChangeEventHandler(GEventHandler):
        pass

    class GTextChangeEventHandler(GEventHandler):
        pass