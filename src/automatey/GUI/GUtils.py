
# External libraries
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui
import PyQt6.QtCore as QtCore

# Internal libraries
import automatey.OS.FileUtils as FileUtils
import automatey.Utils.MathUtils as MathUtils
import automatey.Abstract.Input as Input

class Image:
    '''
    Image, may be used with all element(s) of the GUI.
    '''
    
    def __init__(self, f:FileUtils.File, size=None):

        self.qImage = QtGui.QImage(str(f))
        
        # ? Case: Resizing is necessary.
        if size != None:
            originalSize = [self.qImage.width(), self.qImage.height()]
            MathUtils.keepAspectRatio(size, originalSize)
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

    class StandardIcon:

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

        class Discard:
            qStandardIcon = QtWidgets.QStyle.StandardPixmap.SP_DialogDiscardButton

class EventHandler:
    
    def __init__(self, fcn):
        self.fcn = fcn
    
    Key2QKey = {
        Input.Key.Enter: QtCore.Qt.Key.Key_Return,
        Input.Key.Space: QtCore.Qt.Key.Key_Space,
    }

class EventHandlers:
    '''
    Different event-handler(s).
    
    Note,
    - All expect no argument(s), except otherwise specified.
    '''
    
    class ClickEventHandler(EventHandler):
        pass

    class SelectionChangeEventHandler(EventHandler):
        pass

    class TextChangeEventHandler(EventHandler):
        pass
    
    class KeyEventHandler(EventHandler):
        '''
        Note that,
        - Registered handler shall expect the pressed `Key` is argument.
        '''
        
        def __init__(self, key2FcnDict:dict):
            self.key2FcnDict = key2FcnDict
        
        def INTERNAL_checkIfQKeyRegistered(self, qKey):
            '''
            Check if `qKey` is registered. If not, `None` is returned. Otherwise, corresponding `key` is returned.
            '''
            foundKey = None
            for key in self.key2FcnDict:
                if EventHandler.Key2QKey[key] == qKey:
                    foundKey = key
                    break
            return foundKey

    class KeyPressEventHandler(KeyEventHandler):
        pass