
# External libraries
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui
import PyQt6.QtCore as QtCore

# Internal libraries
import automatey.OS.FileUtils as FileUtils
import automatey.Utils.MathUtils as MathUtils
import automatey.Abstract.Input as AbstractInput

class GIF:
    
    '''
    Image, may be used with all element(s) of the GUI.
    '''
    
    def __init__(self, f:FileUtils.File):
        self.qMovie = QtGui.QMovie(str(f))

class Image:
    '''
    Image, may be used with all element(s) of the GUI.
    '''
    
    def __init__(self, f:FileUtils.File, size=None):

        self.qImage = QtGui.QImage(str(f))
        
        # ? Case: Resizing is necessary.
        if size != None:
            originalSize = [self.qImage.width(), self.qImage.height()]
            MathUtils.MediaSpecific.keepAspectRatio(size, originalSize)
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
        AbstractInput.Key.Enter: QtCore.Qt.Key.Key_Return,
        AbstractInput.Key.Space: QtCore.Qt.Key.Key_Space,
        
        AbstractInput.Key.Letter_M: QtCore.Qt.Key.Key_M,
        
        AbstractInput.Key.Apostrophe: QtCore.Qt.Key.Key_Apostrophe,
        AbstractInput.Key.SemiColon: QtCore.Qt.Key.Key_Semicolon,
        AbstractInput.Key.Slash: QtCore.Qt.Key.Key_Slash,
        AbstractInput.Key.Dot: QtCore.Qt.Key.Key_Period,
        AbstractInput.Key.Comma: QtCore.Qt.Key.Key_Comma,
        AbstractInput.Key.SquareBrackets_Left: QtCore.Qt.Key.Key_BracketLeft,
        AbstractInput.Key.SquareBrackets_Right: QtCore.Qt.Key.Key_BracketRight,
        
        AbstractInput.Key.Up: QtCore.Qt.Key.Key_Up,
        AbstractInput.Key.Down: QtCore.Qt.Key.Key_Down,
        AbstractInput.Key.Left: QtCore.Qt.Key.Key_Left,
        AbstractInput.Key.Right: QtCore.Qt.Key.Key_Right,
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
    
    class OrderChangeEventHandler(EventHandler):
        pass
    
    class KeyEventHandler(EventHandler):
        
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
    
    class ScrollEventHandler(KeyEventHandler):
        def __init__(self, scrollUpFcn=None, scrollDownFcn=None):
            self.scrollUpFcn = scrollUpFcn
            self.scrollDownFcn = scrollDownFcn

class Menu:
    '''
    A menu based on a contract.
    
    Contract shall consist of a list of entries, of type `EndPoint`, `SubMenu`, or `Separator`.
    '''
    
    class EndPoint:
        
        def __init__(self, text, fcn, icon:Icon=None, isCheckable=False, isChecked=False):
            self.text = text
            self.fcn = fcn
            self.icon = icon
            self.isCheckable = isCheckable
            self.isChecked = isChecked
        
        def INTERNAL_instantiate(self, qMenu, qParent):
            action = QtGui.QAction(
                self.text,
                qParent
            )
            if self.icon != None:
                action.setIcon(self.icon.qIcon)
            action.triggered.connect(self.fcn)
            action.setCheckable(self.isCheckable)
            action.setChecked(self.isChecked)
            qMenu.addAction(action)
        
    class SubMenu:
        
        def __init__(self, text, entries):
            self.text = text
            self.entries = entries
        
        def INTERNAL_instantiate(self, qMenu, qParent):
            qSubMenu = qMenu.addMenu(self.text)
            for entry in self.entries:
                entry.INTERNAL_instantiate(qSubMenu, qParent)

    class Separator:

        def INTERNAL_instantiate(self, qMenu, qParent):
            qMenu.addSeparator()
    
    def __init__(self, entries):
        self.entries = entries
    
    def INTERNAL_instantiate(self, qMenu, qParent):
        for entry in self.entries:
            entry.INTERNAL_instantiate(qMenu, qParent)
