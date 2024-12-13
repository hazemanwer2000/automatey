
# External Libraries
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui
import PyQt6.QtCore as QtCore

# Internal Libraries
import automatey.GUI.GUtils as GUtils
import automatey.Base.ColorUtils as ColorUtils
import automatey.Abstract.Graphics as Graphics
import automatey.Media.ImageUtils as ImageUtils
import automatey.OS.FileUtils as FileUtils

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

class GDecorations:

    class GBorder(QtWidgets.QFrame):
        
        def __init__(self, element, elementMargin:Graphics.Margin):
            super().__init__()
            
            # PyQt6: Stylizing 'QFrame' to mimic a border.
            self.setFrameShape(QtWidgets.QFrame.Shape.Box)
            self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
            
            # ? Setting element.
            layout = QtWidgets.QGridLayout(self)
            layout.setSpacing(0)
            layout.setContentsMargins(elementMargin.left,
                                    elementMargin.top,
                                    elementMargin.right,
                                    elementMargin.bottom)
            layout.addWidget(element, 0, 0, 1, 1)

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

    class GColorSelector(QtWidgets.QWidget):
        '''
        Color displayer, and selector.
        '''
        
        def __init__(self, initColor:ColorUtils.Color):
            super().__init__()
            self.color = initColor
            
            # ? Set initial color.
            self.INTERNAL_setColor(self.color)
            
            # ? Set (i.e., fix) size to a square-size.
            self.setFixedSize(30, 30)
            
        def INTERNAL_setColor(self, color:ColorUtils.Color):
            # ? Setting fill-color of widget.
            self.setAutoFillBackground(True)
            palette = self.palette()
            palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor('#' + color.asHEX()))
            self.setPalette(palette)
            
        def GGetColor(self) -> ColorUtils.Color:
            '''
            Get currently selected color.
            '''
            return self.color
            
        def mousePressEvent(self, event):
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                newColor = GStandardDialog.GSelectColor(initColor=self.color)
                if newColor != None:
                    self.color = newColor
                    self.INTERNAL_setColor(self.color)
                event.accept()

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
            
        def GGetSelectedItem(self):
            '''
            Get current item.
            '''
            return self.currentText()
        
        def GGetSelectedItemByIndex(self):
            '''
            Get index of the current item.
            '''
            return self.currentIndex()

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
        
        def GGetSelectedItems(self):
            '''
            Get current item(s).
            '''
            return [x.text() for x in self.selectedItems()]

        def GGetSelectedItem(self):
            '''
            Get current item.
            '''
            currentItem = self.currentItem()
            return None if (currentItem == None) else currentItem.text()

        def GGetSelectedItemByIndex(self) -> int:
            '''
            Get index of current item. If none are selected, `-1` is returned.
            '''
            return self.currentRow()

        def GAddItem(self, item):
            '''
            Add item to (end-of-)list.
            '''
            self.addItem(item)

        def GInsertItemByIndex(self, item, index):
            '''
            Add item to (end-of-)list.
            '''
            self.insertItem(index, item)
            
        def GRemoveItemByIndex(self, index):
            '''
            Remove item at a specific index.
            '''
            self.takeItem(index)

        def GRemoveAllItems(self):
            '''
            Remove all item(s).
            '''
            self.clear()

        def INTERNAL_itemSelectionChange(self):
            if GUtils.GEventHandlers.GSelectionChangeEventHandler in self.eventHandlers:
                self.eventHandlers[GUtils.GEventHandlers.GSelectionChangeEventHandler].fcn()

    class GLineEdit(QtWidgets.QLineEdit, INTERNAL.GEventManager):
        
        def __init__(self, placeholder:str=None, isEditable=True):
            QtWidgets.QLineEdit.__init__(self)
            INTERNAL.GEventManager.__init__(self)
            
            if placeholder != None:
                self.setPlaceholderText(placeholder)
                
            # ? Event-handlers.
            self.textChanged.connect(self.INTERNAL_textChanged)
        
            # ? By default, font is 'Monospace'.
            font = QtGui.QFont("Consolas")
            font.setStyleHint(QtGui.QFont.StyleHint.Monospace)
            self.setFont(font)
            
            # ? Set editable-mode.
            self.setEditable(isEditable)
        
        def setEditable(self, flag:bool):
            '''
            Set editable-mode.
            '''
            self.setReadOnly(not flag)
        
        def GGetText(self):
            '''
            Get text.
            '''
            return self.text()
            
        def INTERNAL_textChanged(self):
            if GUtils.GEventHandlers.GTextChangeEventHandler in self.eventHandlers:
                self.eventHandlers[GUtils.GEventHandlers.GTextChangeEventHandler].fcn()
    
    class GTextEdit(QtWidgets.QPlainTextEdit, INTERNAL.GEventManager):
        
        def __init__(self, placeholder:str=None, isEditable=True):
            QtWidgets.QTextEdit.__init__(self)
            INTERNAL.GEventManager.__init__(self)
            
            if placeholder != None:
                self.setPlaceholderText(placeholder)
                
            # ? Event-handlers.
            self.textChanged.connect(self.INTERNAL_textChanged)
            
            # ? By default, font is 'Monospace'.
            font = QtGui.QFont("Consolas")
            font.setStyleHint(QtGui.QFont.StyleHint.Monospace)
            self.setFont(font)

            # ? Set editable-mode.
            self.setEditable(isEditable)
        
        def setEditable(self, flag:bool):
            '''
            Set editable-mode.
            '''
            self.setReadOnly(not flag)
            
        def keyPressEvent(self, event):
            # PyQt6: When 'TAB' is pressed, insert space(s) instead.
            if event.key() == QtCore.Qt.Key.Key_Tab:
                cursor = self.textCursor()
                cursor.insertText(" " * 2)
                event.accept()
            else:
                super().keyPressEvent(event)

        def GGetText(self):
            '''
            Get text.
            '''
            return self.text()

        def GSetText(self, text):
            '''
            Set text.
            '''
            self.setPlainText(text)
            
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
    
    def GSetIcon(self, icon:GUtils.GIcon):
        '''
        Set application-wide icon.
        '''
        self.icon = icon

class GDialog(QtWidgets.QDialog):
    '''
    A dialog is a blocking window (i.e., blocks execution of invoking GUI event-loop).
    '''
    
    def __init__(self, title:str, rootElement, minimumSize, isSizeFixed=False):
        super().__init__()
        
        # ? All other settings.
        if (isSizeFixed):
            self.setFixedSize(minimumSize[0], minimumSize[1])
        else:
            self.setMinimumSize(minimumSize[0], minimumSize[1])
        self.setWindowTitle(title)
        self.setWindowIcon(QtWidgets.QApplication.instance().icon.qIcon)
        
        # ? Setting root layout.
        # PyQt: For Dialogs', layout must not be attached to a 'QWidget'.
        layout = QtWidgets.QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setRowStretch(0, 1)
        layout.setColumnStretch(0, 1)
        layout.addWidget(rootElement, 0, 0, 1, 1)
        self.setLayout(layout)
        
    def GRun(self):
        '''
        Interrupt the current GUI event-loop, and run the dialog's.
        '''
        self.exec()

class GStandardDialog:
    '''
    Open a standard dialog, to get specific info.
    '''
    
    @staticmethod
    def GSelectExistingFile(initialDirectory:FileUtils.File):
        '''
        Select an existing file. Returns `None` if none were selected.
        '''
        path, _ = QtWidgets.QFileDialog.getOpenFileName(None, directory=str(initialDirectory))
        path = FileUtils.File(path) if (path != '') else None
        return path

    @staticmethod
    def GSelectExistingFiles(initialDirectory:FileUtils.File):
        '''
        Select existing files, returned as a list.
        '''
        paths, _ = QtWidgets.QFileDialog.getOpenFileNames(None, directory=str(initialDirectory))
        return [FileUtils.File(path) for path in paths]
    
    @staticmethod
    def GSelectExistingDirectory(initialDirectory:FileUtils.File):
        '''
        Select existing directory.
        '''
        path = QtWidgets.QFileDialog.getExistingDirectory(None, directory=str(initialDirectory))
        path = FileUtils.File(path) if (path != '') else None
        return path

    @staticmethod
    def GSelectFile(initialDirectory:FileUtils.File):
        '''
        Select a file. Returns `None` if none were selected.
        '''
        path, _ = QtWidgets.QFileDialog.getSaveFileName(None, directory=str(initialDirectory))
        path = FileUtils.File(path) if (path != '') else None
        return path
    
    @staticmethod
    def GSelectColor(initColor:ColorUtils.Color=None) -> ColorUtils.Color:
        '''
        Select a color.
        '''
        colorDialog = QtWidgets.QColorDialog(None)
        colorDialog.setWindowIcon(QtWidgets.QApplication.instance().icon.qIcon)
        if initColor != None:
            colorDialog.setCurrentColor(QtGui.QColor('#' + initColor.asHEX()))
        colorSelected = None
        if colorDialog.exec():
            colorSelected = ColorUtils.Color.fromHEX(colorDialog.selectedColor().name()[1:])
        return colorSelected

    class GBackgroundActivity:
        '''
        Handles dialog, meant to block user until a background-activity completes.
        '''
        
        qProgressDialog:QtWidgets.QProgressDialog = None
        
        @staticmethod
        def GAwait():
            '''
            Opens up dialog.
            
            Note,
            - Dialog does not block the GUI event-loop.
            '''
            # PyQt6: 'QProcessDialog' does not block the GUI event-loop.
            progressDialog = QtWidgets.QProgressDialog("", "", 0, 0, None)
            progressDialog.setWindowTitle("(...)")
            progressDialog.setWindowIcon(QtWidgets.QApplication.instance().icon.qIcon)
            progressDialog.setFixedSize(progressDialog.size())
            progressDialog.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
            progressDialog.setWindowFlag(QtCore.Qt.WindowType.WindowCloseButtonHint, False)
            progressDialog.setCancelButton(None)
            progressDialog.show()
            GStandardDialog.GBackgroundActivity.qProgressDialog = progressDialog

        @staticmethod
        def GRelease():
            '''
            Closes dialog.
            '''
            GStandardDialog.GBackgroundActivity.qProgressDialog.close()
            GStandardDialog.GBackgroundActivity.qProgressDialog = None

class GWindow(QtWidgets.QMainWindow):
    '''
    Multiple window(s) may be created.
    '''
    
    def __init__(self, title:str, rootElement, minimumSize, isSizeFixed=False):
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
        self.setWindowIcon(QtWidgets.QApplication.instance().icon.qIcon)
    
    def setTitle(self, title):
        '''
        Set title of window.
        '''
        self.setWindowTitle(title)
    
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