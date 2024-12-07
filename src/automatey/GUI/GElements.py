
# External Libraries
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui

# Internal Libraries
import automatey.GUI.GUtils as GUtils
import automatey.Base.ColorUtils as ColorUtils

class GLayouts:
    ''''
    Note that,
    - Layout(s) are treated as any other GUI element.
    '''

    class GGridLayout(QtWidgets.QWidget):
        '''
        A grid (e.g., 2x2) layout. 
        '''
        
        def __init__(self):
            super().__init__()
            
            # PyQt6: It is easier (i.e., compatible with more API(s)) if a layout is within a 'QWidget'.
            self.setLayout(QtWidgets.QGridLayout())
        
        def setElement(self, element, rowIdx, colIdx, rowSpan=1, colSpan=1):
            '''
            Set an element in a specific location within the grid.
            '''
            self.layout().addWidget(element, rowIdx, colIdx, rowSpan, colSpan)

class GColorBlock(QtWidgets.QWidget):
    
    def __init__(self, color:ColorUtils.Color):
        super().__init__()
        
        # ? Setting fill-color of widget.
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor('#' + color.asHEX()))
        self.setPalette(palette)

class GApplication(QtWidgets.QApplication):
    '''
    Only one instance of 'Application' is required.
    
    Note:
    - An 'Application' instance must be the first construction, before any element.
    '''
    
    qStyle = None
    
    def __init__(self):
        super().__init__([])
        
        # PyQt6: A cross-platform style called 'Fusion'.
        self.setStyle('Fusion')
        
    def GRun(self):
        '''
        Runs the GUI event-loop.
        '''
        self.exec()

class GWindow(QtWidgets.QMainWindow):
    '''
    Multiple window(s) may be created.
    '''
    
    def __init__(self, title:str, icon:GUtils.GIcon, rootElement, minimumSize, isSizeFixed=False):
        super().__init__()
        
        # ? Setting root layout.
        # PyQt: A layout must be attached to a 'QWidget' instance.
        self.setCentralWidget(rootElement)
        
        # ? All other settings.
        if (isSizeFixed):
            self.setFixedSize(minimumSize[0], minimumSize[1])
        else:
            self.setMinimumSize(minimumSize[0], minimumSize[1])
        self.setWindowTitle(title)
        self.setWindowIcon(icon.qIcon)
    
    def GShow(self):
        '''
        Show window.
        '''
        self.show()

    def GHide(self):
        '''
        Hide window.
        '''
        self.hide()