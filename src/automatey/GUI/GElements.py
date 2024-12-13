
# External Libraries
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui
import PyQt6.QtCore as QtCore

# Internal Libraries
import automatey.GUI.GUtils as GUtils
import automatey.Base.ColorUtils as ColorUtils
import automatey.Abstract.Graphics as Graphics
import automatey.Media.ImageUtils as ImageUtils

class INTERNAL:
    
    class GEventManager:
        
        def __init__(self):
            self.eventHandlers = dict()

        def GSetEventHandler(self, eventHandler:GUtils.GEventHandler):
            '''
            Register an event.
            '''
            self.eventHandlers[type(eventHandler)] = eventHandler

class GLayouts:
    ''''
    Note that,
    - Layout(s) are treated as any other GUI element.
    '''

    class GStackedLayout(QtWidgets.QStackedWidget):
        def __init__(self, elements):
            super().__init__()
            
            for element in elements:
                self.addWidget(element)
                
        def GSetCurrentElement(self, element):
            '''
            Set the current element.
            '''
            self.setCurrentWidget(element)

        def GSetCurrentElementByIndex(self, index):
            '''
            Set the current element.
            '''
            self.setCurrentIndex(index)

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
        '''
        A simple color-block.
        '''
        
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

    class GButton(QtWidgets.QPushButton, INTERNAL.GEventManager):
        '''
        Can handle an icon, as well as text.
        '''
        
        def __init__(self, text:str=None, icon:GUtils.GIcon=None, toolTip=None):
            QtWidgets.QPushButton.__init__(self)
            INTERNAL.GEventManager.__init__(self)
            
            # ? Set text (optional).
            if text != None:
                self.setText(text)
            
            # ? Set icon (optional).
            if icon != None:
                self.setIcon(icon.qIcon)
                if icon.size != None:
                    self.setIconSize(QtCore.QSize(icon.size[0], icon.size[1]))
            
            # ? Set status-tip (optional).
            if toolTip != None:
                self.setToolTip(toolTip)
            
            # ? Event-handlers.
            self.clicked.connect(self.INTERNAL_onClicked)
            
        def INTERNAL_onClicked(self):
            if GUtils.GEventHandlers.GClickEventHandler in self.eventHandlers:
                self.eventHandlers[GUtils.GEventHandlers.GClickEventHandler].fcn()
            
    class GLabel(QtWidgets.QLabel):
        '''
        Can handle an image, as well as text.
        '''

        def __init__(self, text:str=None, img:GUtils.GImage=None):
            super().__init__()
            
            if text != None:
                self.setText(text)
            
            if img != None:
                self.setPixmap(QtGui.QPixmap.fromImage(img.qImage))

    class GCheckBox(QtWidgets.QCheckBox, INTERNAL.GEventManager):
        '''
        Text, along with a check-box.
        '''
        
        def __init__(self, text:str, isChecked=False):
            QtWidgets.QCheckBox.__init__(self)
            INTERNAL.GEventManager.__init__(self)
            
            # ? Set text.
            self.setText(text)
            
            # ? Set initial (check-)state.
            initCheckState = QtCore.Qt.CheckState.Checked if isChecked else QtCore.Qt.CheckState.Unchecked
            self.setCheckState(initCheckState)
            
            # ? Event-handlers.
            self.stateChanged.connect(self.INTERNAL_stateChanged)
            
        def GIsChecked(self):
            '''
            (...)
            '''
            return True if (self.checkState() == QtCore.Qt.CheckState.Checked) else False
        
        def INTERNAL_stateChanged(self, value):
            if GUtils.GEventHandlers.GSelectionChangeEventHandler in self.eventHandlers:
                self.eventHandlers[GUtils.GEventHandlers.GSelectionChangeEventHandler].fcn()

    class GDropDownList(QtWidgets.QComboBox, INTERNAL.GEventManager):
        '''
        A drop-down list. Zero-index'ed.
        '''
        
        def __init__(self, itemList, defaultIndex=0):
            QtWidgets.QComboBox.__init__(self)
            INTERNAL.GEventManager.__init__(self)
            
            self.addItems(itemList)
            self.setCurrentIndex(defaultIndex)
            
            # ? Event-handlers.
            self.currentIndexChanged.connect(self.INTERNAL_currentIndexChanged)
            
        def GGetItem(self):
            '''
            Get current item.
            '''
            return self.currentText()

        def INTERNAL_currentIndexChanged(self, newIndex):
            if GUtils.GEventHandlers.GSelectionChangeEventHandler in self.eventHandlers:
                self.eventHandlers[GUtils.GEventHandlers.GSelectionChangeEventHandler].fcn()

    class GList(QtWidgets.QListWidget, INTERNAL.GEventManager):
        '''
        A list of items.
        '''
        
        def __init__(self, itemList, isMultiSelection=False):
            QtWidgets.QListWidget.__init__(self)
            INTERNAL.GEventManager.__init__(self)
            
            self.addItems(itemList)
            
            if isMultiSelection:
                self.setSelectionMode(self.SelectionMode.MultiSelection)
            
            # ? Event-handlers.
            self.itemSelectionChanged.connect(self.INTERNAL_itemSelectionChange)
        
        def GGetItems(self):
            '''
            Get current item(s).
            '''
            return [x.text() for x in self.selectedItems()]

        def GGetItem(self):
            '''
            Get current item.
            '''
            currentItem = self.currentItem()
            return None if (currentItem == None) else currentItem.text()

        def INTERNAL_itemSelectionChange(self):
            if GUtils.GEventHandlers.GSelectionChangeEventHandler in self.eventHandlers:
                self.eventHandlers[GUtils.GEventHandlers.GSelectionChangeEventHandler].fcn()

    class QLineEdit(QtWidgets.QLineEdit, INTERNAL.GEventManager):
        
        def __init__(self, placeholder:str=None):
            QtWidgets.QLineEdit.__init__(self)
            INTERNAL.GEventManager.__init__(self)
            
            if placeholder != None:
                self.setPlaceholderText(placeholder)
                
            # ? Event-handlers.
            self.textChanged.connect(self.INTERNAL_textChanged)
        
        def GGetText(self):
            '''
            Get text.
            '''
            return self.text()
            
        def INTERNAL_textChanged(self):
            if GUtils.GEventHandlers.GTextChangeEventHandler in self.eventHandlers:
                self.eventHandlers[GUtils.GEventHandlers.GTextChangeEventHandler].fcn()

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