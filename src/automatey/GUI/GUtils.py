
# External libraries
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui

# Internal libraries
import automatey.OS.FileUtils as FileUtils

class GIcon:
    '''
    Icon, may be used in all element(s) of the GUI.
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
