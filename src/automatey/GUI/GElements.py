
# External Libraries
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui
import PyQt6.QtCore as QtCore

# Internal Libraries
import automatey.GUI.GUtils as GUtils
import automatey.Base.ColorUtils as ColorUtils
import automatey.Abstract.Graphics as Graphics
import automatey.Media.ImageUtils as ImageUtils

class GLayouts:
    ''''
    Note that,
    - Layout(s) are treated as any other GUI element.
    '''

    class GGridLayout(QtWidgets.QWidget):
        '''
        A grid (e.g., 2x2) layout.
        
        Note,
        - By default, all row(s) and column(s) are stretchable.
        - All index(s) are zero-based.
        '''
        
        def __init__(self, rowCount:int, colCount:int, elementMargin:Graphics.Margin, elementSpacing:int):
            super().__init__()
            
            # PyQt6: It is easier (i.e., compatible with more API(s)) if a layout is within a 'QWidget'.
            layout = QtWidgets.QGridLayout()
            self.setLayout(layout)
            
            # ? Other setting(s).
            layout.setContentsMargins(elementMargin.left,
                                    elementMargin.top,
                                    elementMargin.right,
                                    elementMargin.bottom)
            layout.setSpacing(elementSpacing)
            
            # ? Set all row(s) and column(s) as stretchable by default.
            for i in range(rowCount):
                layout.setRowStretch(i, 1)
            for i in range(colCount):
                layout.setColumnStretch(i, 1)
        
        def GSetElement(self, element, rowIdx, colIdx, rowSpan=1, colSpan=1):
            '''
            Set an element in a specific location within the grid.
            '''
            layout:QtWidgets.QGridLayout = self.layout()
            layout.addWidget(element, rowIdx, colIdx, rowSpan, colSpan)
        
        def GSetRowMinimumSize(self, rowIdx, size):
            '''
            Fix row size (i.e., no longer stretchable).
            '''
            layout:QtWidgets.QGridLayout = self.layout()
            layout.setRowStretch(rowIdx, 0)
            layout.setRowMinimumHeight(rowIdx, size)

        def GSetColumnMinimumSize(self, colIdx, size):
            '''
            Fix column size (i.e., no longer stretchable).
            '''
            layout:QtWidgets.QGridLayout = self.layout()
            layout.setColumnStretch(colIdx, 0)
            layout.setColumnMinimumWidth(colIdx, size)

class GScrollArea(QtWidgets.QScrollArea):
    '''
    Encapsulates any element, to allow for vertical/horizontal scrolling.
    '''
    
    def __init__(self, element,
                 isVerticalScrollBar=False,
                 isHorizontalScrollBar=False):
        super().__init__()
        
        # ? Set element.
        self.setWidgetResizable(True)
        self.setWidget(element)
        
        # ? Specify if vertical/horizontal scrolling is always on.
        
        verticalScrollBarPolicy = (QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn) if isVerticalScrollBar else (QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        horizontalScrollBarPolicy = (QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn) if isHorizontalScrollBar else (QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.setVerticalScrollBarPolicy(verticalScrollBarPolicy)
        self.setHorizontalScrollBarPolicy(horizontalScrollBarPolicy)

class GWidgets:
    ''''
    Note that,
    - Widget(s) are treated as any other GUI element.
    '''

    class GColorBlock(QtWidgets.QWidget):
        
        def __init__(self, color:ColorUtils.Color, size=None):
            super().__init__()
            
            # ? Setting fill-color of widget.
            self.setAutoFillBackground(True)
            palette = self.palette()
            palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor('#' + color.asHEX()))
            self.setPalette(palette)
            
            # ? Set (i.e., fix) size, if specified.
            if size != None:
                self.setFixedSize(size[0], size[1])

    class GButton(QtWidgets.QPushButton):
        
        def __init__(self, text:str=None, icon:GUtils.GIcon=None):
            super().__init__()
            
            if text != None:
                self.setText(text)
            
            if icon != None:
                self.setIcon(icon.qIcon)
                if icon.size != None:
                    self.setIconSize(QtCore.QSize(icon.size[0], icon.size[1]))
            
    class GLabel(QtWidgets.QLabel):

        def __init__(self, text:str=None, img:GUtils.GImage=None):
            super().__init__()
            
            if text != None:
                self.setText(text)
            
            if img != None:
                self.setPixmap(QtGui.QPixmap.fromImage(img.qImage))

class GApplication(QtWidgets.QApplication):
    '''
    Only one instance of 'Application' is required.
    
    Note:
    - An 'Application' instance must be the first construction, before any element.
    '''
    
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