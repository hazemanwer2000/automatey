
# External Libraries
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui
import PyQt6.QtCore as QtCore
import vlc

# Internal Libraries
import automatey.GUI.GUtils as GUtils
import automatey.GUI.GConcurrency as GConcurrency
import automatey.Base.ColorUtils as ColorUtils
import automatey.Abstract.Graphics as AbstractGraphics
import automatey.Abstract.Input as AbstractInput
import automatey.Base.TimeUtils as TimeUtils
import automatey.OS.FileUtils as FileUtils
import automatey.Resources as Resources
import automatey.Utils.MathUtils as MathUtils
import automatey.GUI.Wrappers.PyQt6 as PyQt6Wrapper
import automatey.Base.ExceptionUtils as ExceptionUtils
import automatey.OS.Clipboard as Clipboard

class INTERNAL:
    
    class EventManager:
        
        def __init__(self):
            self.eventHandlers = dict()

        def setEventHandler(self, eventHandler:GUtils.EventHandler):
            '''
            Register an event.
            '''
            self.eventHandlers[type(eventHandler)] = eventHandler

class Layout:
    
    def __init__(self, qLayout):
        
        self.qLayout = qLayout

class Layouts:

    class GridLayout(Layout):
        '''
        A grid (e.g., 2x2) layout.
        
        Note,
        - By default, all row(s) and column(s) are stretchable.
        '''
        
        def __init__(self, rowCount:int, colCount:int, elementMargin:AbstractGraphics.Margin, elementSpacing:int):
            self.qLayout = QtWidgets.QGridLayout()
            Layout.__init__(self, self.qLayout)
            
            # ? Other setting(s).
            self.qLayout.setContentsMargins(elementMargin.left,
                                    elementMargin.top,
                                    elementMargin.right,
                                    elementMargin.bottom)
            self.qLayout.setSpacing(elementSpacing)
            
            # ? Set all row(s) and column(s) as stretchable by default.
            for i in range(rowCount):
                self.qLayout.setRowStretch(i, 1)
            for i in range(colCount):
                self.qLayout.setColumnStretch(i, 1)
        
        def setWidget(self, widget, rowIdx, colIdx, rowSpan=1, colSpan=1):
            '''
            Set an element in a specific location within the grid.
            '''
            self.qLayout.addWidget(widget.qWidget, rowIdx, colIdx, rowSpan, colSpan)
        
        def setRowMinimumSize(self, rowIdx, size):
            '''
            Fix row size (i.e., no longer stretchable).
            '''
            self.qLayout.setRowStretch(rowIdx, 0)
            self.qLayout.setRowMinimumHeight(rowIdx, size)

        def setColumnMinimumSize(self, colIdx, size):
            '''
            Fix column size (i.e., no longer stretchable).
            '''
            self.qLayout.setColumnStretch(colIdx, 0)
            self.qLayout.setColumnMinimumWidth(colIdx, size)

    class VerticalLayout(Layout):
        '''
        A vertical layout.
        '''
        
        def __init__(self, elementMargin:AbstractGraphics.Margin, elementSpacing:int):
            self.qLayout = QtWidgets.QVBoxLayout()
            Layout.__init__(self, self.qLayout)

            # ? Other setting(s).
            self.qLayout.setContentsMargins(elementMargin.left,
                                    elementMargin.top,
                                    elementMargin.right,
                                    elementMargin.bottom)
            self.qLayout.setSpacing(elementSpacing)

        HorizontalAlignment2AlignmentFlag = {
            AbstractGraphics.Alignment.Horizontal.Left: QtCore.Qt.AlignmentFlag.AlignLeft,
            AbstractGraphics.Alignment.Horizontal.Right: QtCore.Qt.AlignmentFlag.AlignRight,
            AbstractGraphics.Alignment.Horizontal.Center: QtCore.Qt.AlignmentFlag.AlignHCenter,
        }

        def insertWidget(self, widget, idx=-1, alignment=AbstractGraphics.Alignment.Horizontal.Center):
            '''
            Insert widget at index.
            '''
            self.qLayout.insertWidget(idx, 
                                      widget.qWidget,
                                      alignment=Layouts.VerticalLayout.HorizontalAlignment2AlignmentFlag[alignment])

        def removeWidgetAtIndex(self, idx=-1):
            '''
            Remove widget at index.
            '''
            if idx == -1:
                idx = self.qLayout.count() - 1
            self.removeWidget(self.qLayout.itemAt(idx).widget())

        def removeWidget(self, widget):
            '''
            Remove widget.
            '''
            self.qLayout.removeWidget(widget)
            widget.setParent(None)
        
        def getCount(self):
            '''
            Get number of widget(s).
            '''
            return self.qLayout.count()

    class HorizontalLayout(Layout):
        '''
        A horizontal layout.
        '''
        
        def __init__(self, elementMargin:AbstractGraphics.Margin, elementSpacing:int):
            self.qLayout = QtWidgets.QHBoxLayout()
            Layout.__init__(self, self.qLayout)

            # ? Other setting(s).
            self.qLayout.setContentsMargins(elementMargin.left,
                                    elementMargin.top,
                                    elementMargin.right,
                                    elementMargin.bottom)
            self.qLayout.setSpacing(elementSpacing)

        def insertWidget(self, widget, idx=-1):
            '''
            Insert widget at index.
            '''
            self.qLayout.insertWidget(idx, widget.qWidget, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        def removeWidgetAtIndex(self, idx=-1):
            '''
            Remove widget at index.
            '''
            if idx == -1:
                idx = self.qLayout.count() - 1
            self.removeWidget(self.qLayout.itemAt(idx).widget())

        def removeWidget(self, widget):
            '''
            Remove widget.
            '''
            self.qLayout.removeWidget(widget)
            widget.setParent(None)

        def getCount(self):
            '''
            Get number of widget(s).
            '''
            return self.qLayout.count()

class Widget:

    def __init__(self, qWidget:QtWidgets.QWidget):
        
        self.qWidget = qWidget

    def discard(self):
        '''
        Discard widget (i.e., to save memory). Must be called before removing all reference(s) of widget.
        '''
        self.qWidget.deleteLater()
        
    @staticmethod
    def fromLayout(layout):
        '''
        Create widget from layout.
        '''
        qWidget = QtWidgets.QWidget()
        qWidget.setLayout(layout.qLayout)
        widget = Widget(qWidget)
        return widget

class Widgets:

    class Decorators:

        class Outline(Widget):
            '''
            Adds an outline around the specified element.
            '''
            
            def __init__(self, widget, elementMargin:AbstractGraphics.Margin):
                Widget.__init__(self, QtWidgets.QFrame())
                
                # PyQt6: Stylizing 'QFrame' to mimic a border.
                self.qWidget.setFrameShape(QtWidgets.QFrame.Shape.Box)
                self.qWidget.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
                
                # ? Setting element.
                layout = Layouts.GridLayout(1, 1, elementMargin=elementMargin, elementSpacing=0)
                layout.setWidget(widget, 0, 0, 1, 1)
                self.qWidget.setLayout(layout.qLayout)

        class ScrollArea(Widget):
            '''
            Encapsulates any element, to allow for vertical/horizontal scrolling.
            '''
            
            def __init__(self, widget, isVerticalScrollBar=False, isHorizontalScrollBar=False):
                self.qWidget = QtWidgets.QScrollArea()
                Widget.__init__(self, self.qWidget)
                
                # ? Set element.
                self.qWidget.setWidgetResizable(True)
                self.qWidget.setWidget(widget.qWidget)
                
                # ? Specify if vertical/horizontal scrolling is always on.
                
                verticalScrollBarPolicy = (QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn) if isVerticalScrollBar else (QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                horizontalScrollBarPolicy = (QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn) if isHorizontalScrollBar else (QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                
                self.qWidget.setVerticalScrollBarPolicy(verticalScrollBarPolicy)
                self.qWidget.setHorizontalScrollBarPolicy(horizontalScrollBarPolicy)

        class Central(Widget):
            '''
            For fixed-size widget(s), center widget within a stretching box.
            '''
            def __init__(self, widget):
                self.layout = Layouts.GridLayout(3, 3, AbstractGraphics.SymmetricMargin(0), 0)
                self.layout.setWidget(widget, 1, 1)
                layoutsWidget = Widget.fromLayout(self.layout)
                Widget.__init__(self, layoutsWidget.qWidget)

    class Containers:
        
        class StackContainer(Widget):
            '''
            A container, where widgets are stacked on-top of one-another.
            '''
            
            def __init__(self, widgets, initWidget):
                Widget.__init__(self, QtWidgets.QStackedWidget())
                
                for widget in widgets:
                    self.qWidget.addWidget(widget.qWidget)
                
                self.qWidget.setCurrentWidget(initWidget.qWidget)
                    
            def setCurrentWidget(self, widget):
                '''
                Set the current element.
                '''
                self.qWidget.setCurrentWidget(widget.qWidget)

            def setCurrentWidgetByIndex(self, index):
                '''
                Set the current element.
                '''
                self.qWidget.setCurrentIndex(index)

        class VerticalContainer(Widget):
            '''
            A container, where widgets are arranged vertically.
            '''
            
            def __init__(self, elementMargin:AbstractGraphics.Margin, elementSpacing:int):
                Widget.__init__(self, QtWidgets.QWidget())
                
                # ? Setting up grid (root-)layout.
                self.gridLayout = Layouts.GridLayout(2, 1, elementMargin=elementMargin, elementSpacing=0)
                self.gridLayout.setRowMinimumSize(0, 0)
                self.qWidget.setLayout(self.gridLayout.qLayout)
                
                # ? Setting up vertical layout.
                self.verticalLayout = Layouts.VerticalLayout(elementMargin=AbstractGraphics.SymmetricMargin(0), elementSpacing=elementSpacing)
                self.gridLayout.setWidget(Widget.fromLayout(self.verticalLayout), 0, 0)

            def insertWidget(self, widget, idx=-1, alignment=AbstractGraphics.Alignment.Horizontal.Center):
                '''
                Insert widget at index.
                '''
                self.verticalLayout.insertWidget(widget, idx, alignment)

            def removeWidgetAtIndex(self, idx=-1):
                '''
                Remove widget at index.
                '''
                self.verticalLayout.removeWidgetAtIndex(idx)

            def removeWidget(self, widget):
                '''
                Remove widget.
                '''
                self.verticalLayout.removeWidget(widget)

            def getCount(self):
                '''
                Get number of widget(s).
                '''
                return self.verticalLayout.getCount()

        class HorizontalContainer(Widget):
            '''
            A container, where widgets are arranged horizontally.
            '''
            
            def __init__(self, elementMargin:AbstractGraphics.Margin, elementSpacing:int):
                Widget.__init__(self, QtWidgets.QWidget())
                
                # ? Setting up grid (root-)layout.
                self.gridLayout = Layouts.GridLayout(1, 2, elementMargin=elementMargin, elementSpacing=0)
                self.gridLayout.setColumnMinimumSize(0, 0)
                self.qWidget.setLayout(self.gridLayout.qLayout)
                
                # ? Setting up vertical layout.
                self.horizontalLayout = Layouts.HorizontalLayout(elementMargin=AbstractGraphics.SymmetricMargin(0), elementSpacing=elementSpacing)
                self.gridLayout.setWidget(Widget.fromLayout(self.horizontalLayout), 0, 0)

            def insertWidget(self, widget, idx=-1):
                '''
                Insert widget at index.
                '''
                self.horizontalLayout.insertWidget(widget, idx)

            def removeWidgetAtIndex(self, idx=-1):
                '''
                Remove widget at index.
                '''
                self.horizontalLayout.removeWidgetAtIndex(idx)

            def removeWidget(self, widget):
                '''
                Remove widget.
                '''
                self.horizontalLayout.removeWidget(widget)

            def getCount(self):
                '''
                Get number of widget(s).
                '''
                return self.verticalLayout.getCount()

        class TabContainer(Widget, INTERNAL.EventManager):
            '''
            Tabs, to switch between different widget(s).
            '''
            
            def __init__(self, tabNames, widgets):
                self.qTabWidget = QtWidgets.QTabWidget()
                Widget.__init__(self, self.qTabWidget)
                INTERNAL.EventManager.__init__(self)
                                
                # ? Adding tab(s) in-order.
                for tabName, widget in zip(tabNames, widgets):
                    self.qTabWidget.addTab(widget.qWidget, tabName)
                    
                # ? Register event-handler(s).
                self.qTabWidget.currentChanged.connect(self.INTERNAL_currentTabChanged)
            
            def INTERNAL_currentTabChanged(self, index):
                if GUtils.EventHandlers.SelectionChangeEventHandler in self.eventHandlers:
                    self.eventHandlers[GUtils.EventHandlers.SelectionChangeEventHandler].fcn()
            
            def getCurrentTabByIndex(self) -> int:
                '''
                Get index of currently selected tab.
                '''
                return self.qTabWidget.currentIndex()

            def getCurrentTabByName(self) -> str:
                '''
                Get name of currently selected tab.
                '''
                return self.qTabWidget.tabText(self.getCurrentTabByIndex())

    class Basics:

        class ColorBlock(Widget):
            '''
            A simple color-block.
            '''
            
            def __init__(self, initColor:ColorUtils.Color, size=None):
                Widget.__init__(self, PyQt6Wrapper.QWidget())
                
                # ? Setting fill-color of widget.
                self.setColor(initColor)
                self.color = initColor
                
                # ? Set (i.e., fix) size, if specified.
                if size != None:
                    self.qWidget.setFixedSize(size[0], size[1])

            def setColor(self, color:ColorUtils.Color):
                '''
                Set color.
                '''
                # ? Setting fill-color of widget.
                self.qWidget.setAutoFillBackground(True)
                palette = self.qWidget.palette()
                palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor('#' + color.asHEX()))
                self.qWidget.setPalette(palette)
                self.color = color
                
            def getColor(self) -> ColorUtils.Color:
                '''
                Get color.
                '''
                return self.color

        class Button(Widget, INTERNAL.EventManager):
            '''
            Can handle an icon, as well as text.
            '''
            
            def __init__(self, text:str=None, icon:GUtils.Icon=None, toolTip=None):
                self.qButton = QtWidgets.QPushButton()
                Widget.__init__(self, self.qButton)
                INTERNAL.EventManager.__init__(self)
                
                # ? Set text (optional).
                if text != None:
                    self.qButton.setText(text)
                
                # ? Set icon (optional).
                if icon != None:
                    self.qButton.setIcon(icon.qIcon)
                    if icon.size != None:
                        self.qButton.setIconSize(QtCore.QSize(icon.size[0], icon.size[1]))
                
                # ? Set status-tip (optional).
                if toolTip != None:
                    self.qButton.setToolTip(toolTip)
                
                # ? Event-handlers.
                self.qButton.clicked.connect(self.INTERNAL_onClicked)
                
                # PyQt6: Force widget not to be focusable.
                self.qButton.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                
            def INTERNAL_onClicked(self):
                if GUtils.EventHandlers.ClickEventHandler in self.eventHandlers:
                    self.eventHandlers[GUtils.EventHandlers.ClickEventHandler].fcn()

        class Label:
            '''
            Can handle an image, GIF, and text.
            '''

            def __init__(self, text:str=None, img:GUtils.Image=None, gif:GUtils.GIF=None):
                self.qWidget = PyQt6Wrapper.QLabel()
                Widget.__init__(self, self.qWidget)
                
                if text != None:
                    self.qWidget.setText(text)
                
                if img != None:
                    self.qWidget.setPixmap(QtGui.QPixmap.fromImage(img.qImage))

                if gif != None:
                    self.qWidget.setMovie(gif.qMovie)
                    gif.qMovie.start()

                # PyQt6: Force widget not to be focusable.
                self.qWidget.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

        class CheckBox(Widget, INTERNAL.EventManager):
            '''
            Text, along with a check-box.
            '''
            
            def __init__(self, text:str=None, isChecked=False):
                self.qWidget = QtWidgets.QCheckBox()
                INTERNAL.EventManager.__init__(self)
                Widget.__init__(self, self.qWidget)
                
                # ? Set text.
                if text != None:
                    self.qWidget.setText(text)
                
                # ? Set initial (check-)state.
                initCheckState = QtCore.Qt.CheckState.Checked if isChecked else QtCore.Qt.CheckState.Unchecked
                self.qWidget.setCheckState(initCheckState)
                
                # ? Event-handlers.
                self.qWidget.stateChanged.connect(self.INTERNAL_stateChanged)
                
                # PyQt6: Force widget not to be focusable.
                self.qWidget.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                
            def isChecked(self):
                '''
                (...)
                '''
                return True if (self.qWidget.checkState() == QtCore.Qt.CheckState.Checked) else False
            
            def INTERNAL_stateChanged(self, value):
                if GUtils.EventHandlers.SelectionChangeEventHandler in self.eventHandlers:
                    self.eventHandlers[GUtils.EventHandlers.SelectionChangeEventHandler].fcn()

        class List(Widget, INTERNAL.EventManager):
            '''
            A list of items.
            '''
            
            def __init__(self, itemList, isMultiSelection=False):
                self.qWidget = QtWidgets.QListWidget()
                INTERNAL.EventManager.__init__(self)
                Widget.__init__(self, self.qWidget)
                
                self.qWidget.addItems(itemList)
                
                if isMultiSelection:
                    self.qWidget.setSelectionMode(self.qWidget.SelectionMode.MultiSelection)
                
                # PyQt6: Enforce that the scroll-bar is always present.
                self.qWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
                
                # ? Event-handlers.
                self.qWidget.itemSelectionChanged.connect(self.INTERNAL_itemSelectionChange)
            
            def getAllSelected(self):
                '''
                Get current item(s).
                '''
                return [x.text() for x in self.qWidget.selectedItems()]

            def getSelected(self):
                '''
                Get current item.
                '''
                currentItem = self.qWidget.currentItem()
                return None if (currentItem == None) else currentItem.text()

            def getSelectedIndex(self) -> int:
                '''
                Get index of current item. If none are selected, `-1` is returned.
                '''
                return self.qWidget.currentRow()

            def insert(self, item, index=-1):
                '''
                Insert item at index.
                '''
                if index == -1: 
                    index = self.qWidget.count()
                self.qWidget.insertItem(index, item)
                
            def removeByIndex(self, index):
                '''
                Remove item at a specific index.
                '''
                self.qWidget.takeItem(index)

            def removeAll(self):
                '''
                Remove all item(s).
                '''
                self.qWidget.clear()

            def INTERNAL_itemSelectionChange(self):
                if GUtils.EventHandlers.SelectionChangeEventHandler in self.eventHandlers:
                    self.eventHandlers[GUtils.EventHandlers.SelectionChangeEventHandler].fcn()

        class Slider(Widget, INTERNAL.EventManager):
            '''
            A slider (deals only with integer value(s)).
            '''
            
            def __init__(self, valueRange, initValue, isHorizontal=True):
                self.qWidget = PyQt6Wrapper.QSlider()
                INTERNAL.EventManager.__init__(self)
                Widget.__init__(self, self.qWidget)
                
                # ? Set orientation.
                orientation = QtCore.Qt.Orientation.Horizontal if isHorizontal else QtCore.Qt.Orientation.Vertical
                self.qWidget.setOrientation(orientation)
                
                # PyQt6: Fix tick-interval at '1'.
                self.qWidget.setTickInterval(1)
                
                # ? Set value-range, and init-value.
                self.qWidget.setRange(valueRange[0], valueRange[1])
                self.qWidget.setValue(initValue)
                
                # ? Register Mouse Event(s).
                self.qWidget.mouseMoveEventFcn = self.INTERNAL_mouseEvent
                self.qWidget.mousePressEventFcn = self.INTERNAL_mouseEvent

                # PyQt6: Force widget not to be focusable.
                self.qWidget.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                
            def INTERNAL_mouseEvent(self, event):
                # ? Update value.
                ratio = event.position().x() / self.qWidget.width()
                value = MathUtils.mapValue(ratio, [0.0, 1.0], [self.qWidget.minimum(), self.qWidget.maximum()])
                value = MathUtils.clampValue(value, self.qWidget.minimum(), self.qWidget.maximum())
                self.qWidget.setValue(int(value))
                
                # ? Call event-handler, if present.
                if GUtils.EventHandlers.SelectionChangeEventHandler in self.eventHandlers:
                    self.eventHandlers[GUtils.EventHandlers.SelectionChangeEventHandler].fcn()
                
            def setValue(self, value):
                '''
                Set value.
                '''
                self.qWidget.setValue(value)

            def getValue(self):
                '''
                Get value.
                '''
                return self.qWidget.value()

        class DropDownList(QtWidgets.QComboBox, INTERNAL.EventManager):
            '''
            A drop-down list.
            '''
            
            def __init__(self, itemList, defaultIndex=0):
                self.qWidget = QtWidgets.QComboBox()
                INTERNAL.EventManager.__init__(self)
                Widget.__init__(self, self.qWidget)
                
                self.qWidget.addItems(itemList)
                self.qWidget.setCurrentIndex(defaultIndex)
                
                # ? Event-handlers.
                self.qWidget.currentIndexChanged.connect(self.INTERNAL_currentIndexChanged)
                
            def getSelected(self):
                '''
                Get current item.
                '''
                return self.currentText()
            
            def getSelectedIndex(self):
                '''
                Get index of the current item.
                '''
                return self.currentIndex()

            def INTERNAL_currentIndexChanged(self, newIndex):
                if GUtils.EventHandlers.SelectionChangeEventHandler in self.eventHandlers:
                    self.eventHandlers[GUtils.EventHandlers.SelectionChangeEventHandler].fcn()

        class LineEdit(Widget, INTERNAL.EventManager):
            
            def __init__(self, placeholder:str=None, isEditable=True, isMonospaced=False):
                self.qWidget = PyQt6Wrapper.QLineEdit()
                INTERNAL.EventManager.__init__(self)
                Widget.__init__(self, self.qWidget)
                
                if placeholder != None:
                    self.qWidget.setPlaceholderText(placeholder)
                    
                # ? Event-handler(s).
                self.qWidget.textChanged.connect(self.INTERNAL_textChanged)
                self.qWidget.keyPressEventFcn = self.INTERNAL_keyPressEvent
            
                # ? By default, font is 'Monospace'.
                if isMonospaced:
                    font = QtGui.QFont("Consolas")
                    font.setStyleHint(QtGui.QFont.StyleHint.Monospace)
                    self.qWidget.setFont(font)
                
                # ? Set editable-mode.
                self.setEditable(isEditable)
            
            def setEditable(self, flag:bool):
                '''
                Set editable-mode.
                '''
                self.qWidget.setReadOnly(not flag)
            
            def getText(self):
                '''
                Get text.
                '''
                return self.qWidget.text()
            
            def INTERNAL_keyPressEvent(self, event):
                qKey = event.key()
                if GUtils.EventHandlers.KeyPressEventHandler in self.eventHandlers:
                    keyPressEventHandler:GUtils.EventHandlers.KeyPressEventHandler = self.eventHandlers[GUtils.EventHandlers.KeyPressEventHandler]
                    foundKey = keyPressEventHandler.INTERNAL_checkIfQKeyRegistered(qKey)
                    if foundKey != None:
                        keyPressEventHandler.key2FcnDict[foundKey]()
                        return 0
                
            def INTERNAL_textChanged(self):
                if GUtils.EventHandlers.TextChangeEventHandler in self.eventHandlers:
                    self.eventHandlers[GUtils.EventHandlers.TextChangeEventHandler].fcn()

        class TextEdit(Widget, INTERNAL.EventManager):
            
            def __init__(self, placeholder:str=None, isEditable=True, isMonospaced=False):
                self.qWidget = PyQt6Wrapper.QPlainTextEdit()
                INTERNAL.EventManager.__init__(self)
                Widget.__init__(self, self.qWidget)
                
                if placeholder != None:
                    self.qWidget.setPlaceholderText(placeholder)
                    
                # ? Event-handler(s).
                self.qWidget.textChanged.connect(self.INTERNAL_textChanged)
                self.qWidget.keyPressEventFcn = self.INTERNAL_keyPressEvent
            
                # ? By default, font is 'Monospace'.
                if isMonospaced:
                    font = QtGui.QFont("Consolas")
                    font.setStyleHint(QtGui.QFont.StyleHint.Monospace)
                    self.qWidget.setFont(font)
                
                # ? Set editable-mode.
                self.setEditable(isEditable)
            
            def setEditable(self, flag:bool):
                '''
                Set editable-mode.
                '''
                self.qWidget.setReadOnly(not flag)
            
            def getText(self):
                '''
                Get text.
                '''
                return self.qWidget.text()

            def setText(self, text):
                '''
                Get text.
                '''
                return self.qWidget.setPlainText(text)
            
            def INTERNAL_keyPressEvent(self, event):
                qKey = event.key()
                if GUtils.EventHandlers.KeyPressEventHandler in self.eventHandlers:
                    keyPressEventHandler:GUtils.EventHandlers.KeyPressEventHandler = self.eventHandlers[GUtils.EventHandlers.KeyPressEventHandler]
                    foundKey = keyPressEventHandler.INTERNAL_checkIfQKeyRegistered(qKey)
                    if foundKey != None:
                        keyPressEventHandler.key2FcnDict[foundKey]()
                        return 0
                
            def INTERNAL_textChanged(self):
                if GUtils.EventHandlers.TextChangeEventHandler in self.eventHandlers:
                    self.eventHandlers[GUtils.EventHandlers.TextChangeEventHandler].fcn()

        class EntryTable(Widget):
            '''
            An input entry-table.
            '''
            
            def __init__(self, header:list):
                self.layout = Layouts.GridLayout(1, 2, elementMargin=AbstractGraphics.SymmetricMargin(0), elementSpacing=0)
                Widget.__init__(self, Widget.fromLayout(self.layout).qWidget)
                
                # ? Create table.
                self.qTableWidget = QtWidgets.QTableWidget(1, len(header))
                self.layout.setWidget(Widget(self.qTableWidget), 0, 1)
                # ? ? Assign header.
                self.header = header
                self.qTableWidget.setHorizontalHeaderLabels(header)
                # ? ? Fix header-column, and row size.
                qVerticalHeader = self.qTableWidget.verticalHeader()
                qVerticalHeader.setFixedWidth(50)
                qVerticalHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)

                # ? Create (control-)panel.
                self.verticalContainer = Widgets.Containers.VerticalContainer(elementMargin=AbstractGraphics.SymmetricMargin(5), elementSpacing=5)
                self.layout.setWidget(self.verticalContainer, 0, 0)
                self.layout.setColumnMinimumSize(0, 0)
                # ? ? Create insert button.
                self.insertButton = Widgets.Basics.Button(icon=GUtils.Icon.createFromFile(Resources.resolve(FileUtils.File('icon/lib/feather/plus.svg'))), toolTip='Insert Entry')
                self.insertButton.setEventHandler(GUtils.EventHandlers.ClickEventHandler(self.INTERNAL_insertButton_clickEvent))
                self.verticalContainer.insertWidget(self.insertButton)
                # ? ? Create move-up button.
                self.moveUpButton = Widgets.Basics.Button(icon=GUtils.Icon.createFromFile(Resources.resolve(FileUtils.File('icon/lib/feather/arrow-up.svg'))), toolTip='Move Entry Up')
                self.moveUpButton.setEventHandler(GUtils.EventHandlers.ClickEventHandler(self.INTERNAL_moveUpButton_clickEvent))
                self.verticalContainer.insertWidget(self.moveUpButton)
                # ? ? Create move-down button.
                self.moveDownButton = Widgets.Basics.Button(icon=GUtils.Icon.createFromFile(Resources.resolve(FileUtils.File('icon/lib/feather/arrow-down.svg'))), toolTip='Move Entry Down')
                self.moveDownButton.setEventHandler(GUtils.EventHandlers.ClickEventHandler(self.INTERNAL_moveDownButton_clickEvent))
                self.verticalContainer.insertWidget(self.moveDownButton)
                # ? ? Create delete button.
                self.deleteButton = Widgets.Basics.Button(icon=GUtils.Icon.createFromFile(Resources.resolve(FileUtils.File('icon/lib/feather/x.svg'))), toolTip='Delete Entry')
                self.deleteButton.setEventHandler(GUtils.EventHandlers.ClickEventHandler(self.INTERNAL_deleteButton_clickEvent))
                self.verticalContainer.insertWidget(self.deleteButton)
            
            def INTERNAL_insertButton_clickEvent(self):
                currentRowIdx = self.qTableWidget.currentRow()
                self.qTableWidget.insertRow(currentRowIdx + 1)

            def INTERNAL_deleteButton_clickEvent(self):
                rowCount = self.qTableWidget.rowCount()
                if rowCount > 1:
                    # ? Remove current row.
                    currentRowIdx = self.qTableWidget.currentRow()
                    self.qTableWidget.removeRow(currentRowIdx)
                    # ? Select (appropriate) row.
                    newLastRowIdx = (rowCount - 1) - 1
                    selectIdx = currentRowIdx if (currentRowIdx <= newLastRowIdx) else newLastRowIdx
                    self.qTableWidget.setCurrentCell(selectIdx, self.qTableWidget.currentColumn())

            def INTERNAL_moveUpButton_clickEvent(self):
                currentRowIdx = self.qTableWidget.currentRow()
                if (currentRowIdx > 0):
                    # Swap with previous row.
                    previousRowIdx = currentRowIdx - 1
                    self.INTERNAL_swapEntries(currentRowIdx, previousRowIdx)
                    # ? Select (appropriate) row.
                    self.qTableWidget.setCurrentCell(previousRowIdx, self.qTableWidget.currentColumn())

            def INTERNAL_moveDownButton_clickEvent(self):
                currentRowIdx = self.qTableWidget.currentRow()
                rowCount = self.qTableWidget.rowCount()
                nextRowIdx = currentRowIdx + 1
                if (nextRowIdx < rowCount):
                    # Swap with next row.
                    self.INTERNAL_swapEntries(currentRowIdx, nextRowIdx)
                    # ? Select (appropriate) row.
                    self.qTableWidget.setCurrentCell(nextRowIdx, self.qTableWidget.currentColumn())

            def INTERNAL_setEntry(self, idx, data):
                '''
                Set entry, from a list of string(s).
                '''
                columnCount = self.qTableWidget.columnCount()
                for columnIdx in range(columnCount):
                    self.qTableWidget.setItem(idx, columnIdx, QtWidgets.QTableWidgetItem(data[columnIdx]))
            
            def INTERNAL_swapEntries(self, idx1, idx2):
                '''
                Swap entries.
                '''
                data1 = self.getEntry(idx1)
                data2 = self.getEntry(idx2)
                self.INTERNAL_setEntry(idx2, data1)
                self.INTERNAL_setEntry(idx1, data2)

            def getEntry(self, idx) -> dict:
                '''
                Get entry.
                '''
                columnCount = self.qTableWidget.columnCount()
                data = []
                for columnIdx in range(columnCount):
                    qItem = self.qTableWidget.item(idx, columnIdx)
                    data.append(qItem.text() if (qItem != None) else '')
                return dict(zip(self.header, data))

            def getEntries(self):
                '''
                Get a list of all entries.
                '''
                rowCount = self.qTableWidget.rowCount()
                entries = []
                for idx in range(rowCount):
                    entries.append(self.getEntry(idx))
                return entries

            def getEntryCount(self):
                '''
                Get number of entries.
                '''
                return self.qTableWidget.rowCount()

        class VideoRenderer(Widget, INTERNAL.EventManager):
            '''
            Renders a video.
            
            Limitation(s):
            - Video-on-repeat is not optional.
            '''
        
            def __init__(self):
                self.qWidget = PyQt6Wrapper.QFrame()
                INTERNAL.EventManager.__init__(self)
                Widget.__init__(self, self.qWidget)
                
                # ? Setting up VLC media-player.
                # ? ? Option (quiet) silences VLC log messages.
                # ? ? Option (input-repeat) sets the number of video-repetitions.
                self.VLCInstance = vlc.Instance('--quiet', '--input-repeat=999999999')
                self.player = self.VLCInstance.media_player_new()
                # ? ? Configure player to ignore mouse/key event(s).
                vlc.libvlc_video_set_mouse_input(self.player, 0)
                vlc.libvlc_video_set_key_input(self.player, 0)
                # (!) OS-specific (Windows-OS)
                self.player.set_hwnd(self.qWidget.winId())
                
                # ? Set initial volume.
                self.isMuteFlag = False
                self.volume = 100
                self.player.audio_set_volume(self.volume)
                
                # ? Set event-handler(s).
                self.qWidget.keyPressEventFcn = self.INTERNAL_keyPressEvent
                self.qWidget.enterEventFcn = self.INTERNAL_enterEvent
                self.qWidget.contextMenuEventFcn = self.INTERNAL_contextMenuEvent
                self.qContextMenu:QtWidgets.QMenu = None
                self.qWidget.mouseMoveEventFcn = self.INTERNAL_mouseMoveEvent
                self.qWidget.setMouseTracking(True)
                self.lastMousePosition = (0, 0)
            
            def setContextMenu(self, menu:GUtils.Menu):
                '''
                Set context menu.
                
                Note that, it is shown only if triggered within video's frame.
                '''
                self.qContextMenu = QtWidgets.QMenu()
                menu.INTERNAL_instantiate(self.qContextMenu, self.qWidget)
            
            def INTERNAL_contextMenuEvent(self, event:QtGui.QContextMenuEvent):
                if self.qContextMenu != None:
                    videoMousePosition = MathUtils.MediaSpecific.BoundingBox.isWithinFrame(
                        self.player.video_get_size(),
                        [self.qWidget.size().width(), self.qWidget.size().height()],
                        [event.pos().x(), event.pos().y()],
                    )
                    if (videoMousePosition != None):
                        self.qContextMenu.exec(event.globalPos())
            
            def INTERNAL_mouseMoveEvent(self, event):
                videoMousePosition = MathUtils.MediaSpecific.BoundingBox.isWithinFrame(
                    self.player.video_get_size(),
                    [self.qWidget.size().width(), self.qWidget.size().height()],
                    [event.pos().x(), event.pos().y()],
                )
                if (videoMousePosition != None):
                    self.lastMousePosition = tuple(videoMousePosition)
            
            def INTERNAL_keyPressEvent(self, event):
                qKey = event.key()
                if GUtils.EventHandlers.KeyPressEventHandler in self.eventHandlers:
                    keyPressEventHandler:GUtils.EventHandlers.KeyPressEventHandler = self.eventHandlers[GUtils.EventHandlers.KeyPressEventHandler]
                    foundKey = keyPressEventHandler.INTERNAL_checkIfQKeyRegistered(qKey)
                    if foundKey != None:
                        keyPressEventHandler.key2FcnDict[foundKey]()
                    
            def INTERNAL_enterEvent(self, event):
                # ? Gain focus (to be able to handle key-press(es)), when mouse enters widget's area.
                self.qWidget.setFocus()
            
            def load(self, f:FileUtils.File):
                '''
                Load video.
                
                Note,
                - Video auto-plays.
                '''
                media = self.VLCInstance.media_new(str(f))
                self.player.set_media(media)
                self.player.play()
            
            def play(self):
                '''
                Play video.
                '''
                if not self.player.is_playing():
                    self.player.play()

            def pause(self):
                '''
                Pause video.
                '''
                if self.player.is_playing():
                    self.player.pause()
        
            def isPlaying(self):
                '''
                (...)
                '''
                return self.player.is_playing()
            
            def restart(self):
                '''
                Seek `0` and play.
                '''
                self.play()
                self.player.set_time(0)
            
            def getDuration(self) -> TimeUtils.Time:
                '''
                Get video duration.
                '''
                return TimeUtils.Time.createFromMilliseconds(self.player.get_length())

            def getPosition(self) -> TimeUtils.Time:
                '''
                (...)
                '''
                return TimeUtils.Time.createFromMilliseconds(self.player.get_time())
            
            def seekPosition(self, position:TimeUtils.Time):
                '''
                Seek position. If out-of-bounds, `0` is seeked.
                '''
                if (position > self.getDuration()):
                    position = TimeUtils.Time(0)
                self.player.set_time(int(position.toMilliseconds()))
            
            def seekForward(self, skipTime:TimeUtils.Time):
                '''
                Skip forward. If out-of-bounds, `0` is seeked.
                '''
                newPosition = self.getPosition() + skipTime
                self.seekPosition(newPosition)

            def seekBackward(self, skipTime:TimeUtils.Time):
                '''
                Skip backward. If out-of-bounds, `0` is seeked.
                '''
                newPosition = self.getPosition() - skipTime
                self.seekPosition(newPosition)

            def adjustVolume(self, delta:int):
                '''
                Adjust volume (0-100). Value is clamped.
                '''
                self.setVolume(self.volume + delta)
            
            def setVolume(self, value:int):
                '''
                Adjust volume (0-100). Value is clamped.
                '''
                self.volume = int(MathUtils.clampValue(value, 0, 100))
                if not self.isMuteFlag:
                    self.player.audio_set_volume(self.volume)

            def getVolume(self) -> int:
                '''
                Get current volume (i.e., indepdent of is muted), range `0-100`.
                '''
                return self.volume
            
            def mute(self):
                '''
                Mute.
                
                Note,
                - Volume adjustment(s) does not affect the mute feature.
                '''
                self.isMuteFlag = True
                self.player.audio_set_volume(0)

            def unmute(self):
                '''
                Un-Mute.
                
                Note,
                - Volume adjustment(s) does not affect the mute feature.
                '''
                self.isMuteFlag = False
                self.player.audio_set_volume(self.volume)

            def isMute(self):
                '''
                (...)
                
                Note,
                - Volume adjustment(s) does not affect the mute feature.
                '''
                return self.isMuteFlag

            def getDimensions(self):
                '''
                Returns a '(width, height)' tuple.
                '''
                return self.player.video_get_size()

            def getMousePosition(self):
                '''
                Get mouse position within video, updated only when triggered to show context-menu.
                '''
                return self.lastMousePosition

        class GIFRenderer(Widget, INTERNAL.EventManager):
            '''
            GIF renderer.
            '''

            def __init__(self, ):
                self.label = Widget(PyQt6Wrapper.QLabel())
                self.decorator = Widgets.Decorators.Central(self.label)
                Widget.__init__(self, self.decorator.qWidget)
                
                # (...) 
                self.qMovie = None
                
                # ? Initialize event-handler(s).
                self.label.qWidget.contextMenuEventFcn = self.INTERNAL_contextMenuEvent
                self.qContextMenu:QtWidgets.QMenu = None
                self.lastMousePosition = (0, 0)
                self.label.qWidget.mouseMoveEventFcn = self.INTERNAL_mouseMoveEvent
                self.label.qWidget.setMouseTracking(True)
            
            def INTERNAL_mouseMoveEvent(self, event):
                self.lastMousePosition = (event.pos().x(), event.pos().y())
            
            def INTERNAL_contextMenuEvent(self, event:QtGui.QContextMenuEvent):
                if self.qContextMenu != None:
                    self.qContextMenu.exec(event.globalPos())
            
            def setContextMenu(self, menu:GUtils.Menu):
                '''
                Set context menu.
                '''
                self.qContextMenu = QtWidgets.QMenu()
                menu.INTERNAL_instantiate(self.qContextMenu, self.label.qWidget)

            def getMousePosition(self):
                '''
                Get mouse position within GIF, updated only when triggered to show context-menu.
                '''
                return self.lastMousePosition
            
            def load(self, f:FileUtils.File):
                '''
                Load GIF file.
                '''
                if self.qMovie != None:
                    self.qMovie.stop()
                self.qMovie = QtGui.QMovie(str(f))
                self.label.qWidget.setMovie(self.qMovie)
                self.qMovie.start()

        class ImageRenderer(Widget, INTERNAL.EventManager):
            '''
            Image renderer.
            '''

            def __init__(self):
                self.label = Widget(PyQt6Wrapper.QLabel())
                self.decorator = Widgets.Decorators.Central(self.label)
                Widget.__init__(self, self.decorator.qWidget)
                
                # (...) 
                self.qMovie = None
                
                # ? Initialize event-handler(s).
                self.label.qWidget.contextMenuEventFcn = self.INTERNAL_contextMenuEvent
                self.qContextMenu:QtWidgets.QMenu = None
                self.lastMousePosition = (0, 0)
                self.label.qWidget.mouseMoveEventFcn = self.INTERNAL_mouseMoveEvent
                self.label.qWidget.setMouseTracking(True)
            
            def INTERNAL_mouseMoveEvent(self, event):
                self.lastMousePosition = (event.pos().x(), event.pos().y())
            
            def INTERNAL_contextMenuEvent(self, event:QtGui.QContextMenuEvent):
                if self.qContextMenu != None:
                    self.qContextMenu.exec(event.globalPos())
            
            def setContextMenu(self, menu:GUtils.Menu):
                '''
                Set context menu.
                '''
                self.qContextMenu = QtWidgets.QMenu()
                menu.INTERNAL_instantiate(self.qContextMenu, self.label.qWidget)

            def getMousePosition(self):
                '''
                Get mouse position within GIF, updated only when triggered to show context-menu.
                '''
                return self.lastMousePosition
            
            def load(self, f:FileUtils.File):
                '''
                Load image file.
                '''
                self.label.qWidget.setPixmap(QtGui.QPixmap.fromImage(GUtils.Image(f).qImage))

    class Complex:

        class ColorSelector(Widget):
            '''
            Color displayer, and selector.
            '''
            
            def __init__(self, initColor:ColorUtils.Color):
                # ? Set initial color, and (fixed-)size.
                self.colorBlock = Widgets.Basics.ColorBlock(initColor=initColor, size=[30, 30])
                Widget.__init__(self, self.colorBlock.qWidget)
                self.colorBlock.qWidget.mousePressEventFcn = self.INTERNAL_mousePressEvent
            
            def getColor(self):
                return self.colorBlock.getColor()
                
            def INTERNAL_mousePressEvent(self, event):
                newColor = StandardDialog.selectColor(initColor=self.colorBlock.getColor())
                if newColor != None:
                    self.colorBlock.setColor(newColor)

        class VideoPlayer(Widget):
            '''
            A video player.
            '''
            
            Constants = {
                'Skip-Time' : {
                    'L3' : TimeUtils.Time.createFromSeconds(10.0),
                    'L2' : TimeUtils.Time.createFromSeconds(3.0),
                    'L1' : TimeUtils.Time.createFromSeconds(1.0),
                    'L0' : TimeUtils.Time.createFromSeconds(0.1),
                },
                'Adjust-Volume-Delta' : 10,
                'Load-Default' : Resources.resolve(FileUtils.File('video/static.mp4')),
            }
            
            def __init__(self):
                # ? Setting up root (...)
                self.rootLayout = Layouts.GridLayout(2, 1, AbstractGraphics.SymmetricMargin(5), 5)
                Widget.__init__(self, Widget.fromLayout(self.rootLayout).qWidget)
                
                # ? Setting-up video-renderer.
                self.renderer = Widgets.Basics.VideoRenderer()
                self.rootLayout.setWidget(self.renderer, 0, 0)
                
                # ? Setting-up control-panel.  
                # ? ? Specifying panel parameter(s).
                panelWidgetCount = 6
                panelSeekbarIdx = (panelWidgetCount - 1) - 1
                panelWorkingIdx = 0
                # ? ? Setting up panel's root (...)
                self.panelLayout = Layouts.GridLayout(1, 6, AbstractGraphics.SymmetricMargin(0), 5)
                self.rootLayout.setWidget(Widget.fromLayout(self.panelLayout), 1, 0)
                self.rootLayout.setRowMinimumSize(1, 0)
                # ? ? Only the seekbar's containing column shall be stretchable. 
                for idx in range(panelWidgetCount):
                    if idx != panelSeekbarIdx:
                        self.panelLayout.setColumnMinimumSize(idx, 0)
                # ? ? Setting-up play-pause button.
                self.playButton = Widgets.Basics.Button(icon=GUtils.Icon.createFromLibrary(GUtils.Icon.StandardIcon.MediaPlay), toolTip='Play')
                self.playButton.setEventHandler(GUtils.EventHandlers.ClickEventHandler(self.play))
                self.pauseButton = Widgets.Basics.Button(icon=GUtils.Icon.createFromLibrary(GUtils.Icon.StandardIcon.MediaPause), toolTip='Pause')
                self.pauseButton.setEventHandler(GUtils.EventHandlers.ClickEventHandler(self.pause))
                self.playPauseButton = Widgets.Containers.StackContainer([self.playButton, self.pauseButton], self.pauseButton)
                self.panelLayout.setWidget(self.playPauseButton, 0, panelWorkingIdx)
                panelWorkingIdx += 1
                # ? ? Setting-up restart button.
                self.restartButton = Widgets.Basics.Button(icon=GUtils.Icon.createFromLibrary(GUtils.Icon.StandardIcon.MediaStop), toolTip='Stop')
                self.restartButton.setEventHandler(GUtils.EventHandlers.ClickEventHandler(self.restart))
                self.panelLayout.setWidget(self.restartButton, 0, panelWorkingIdx)
                panelWorkingIdx += 1
                # ? ? Setting-up seek-backward button.
                self.seekBackwardButton = Widgets.Basics.Button(icon=GUtils.Icon.createFromLibrary(GUtils.Icon.StandardIcon.MediaSeekBackward), toolTip='Seek Backward')
                self.seekBackwardButton.setEventHandler(GUtils.EventHandlers.ClickEventHandler(lambda: self.seekBackward(Widgets.Complex.VideoPlayer.Constants['Skip-Time']['L2'])))
                self.panelLayout.setWidget(self.seekBackwardButton, 0, panelWorkingIdx)
                panelWorkingIdx += 1
                # ? ? Setting-up seek-forward button.
                self.seekForwardButton = Widgets.Basics.Button(icon=GUtils.Icon.createFromLibrary(GUtils.Icon.StandardIcon.MediaSeekForward), toolTip='Seek Forward')
                self.seekForwardButton.setEventHandler(GUtils.EventHandlers.ClickEventHandler(lambda: self.seekForward(Widgets.Complex.VideoPlayer.Constants['Skip-Time']['L2'])))
                self.panelLayout.setWidget(self.seekForwardButton, 0, panelWorkingIdx)
                panelWorkingIdx += 1
                # ? ? Setting-up seeker (i.e., slider).
                # ? ? ? Max. value is set arbitrarily, and value-mapping is used to derive video position.
                self.seekerMaxValue = 10000000
                self.seeker = Widgets.Basics.Slider(valueRange=[0, self.seekerMaxValue], initValue=0, isHorizontal=True)
                self.seeker.setEventHandler(GUtils.EventHandlers.SelectionChangeEventHandler(self.INTERNAL_seeker_selectionChangeEvent))
                self.panelLayout.setWidget(self.seeker, 0, panelWorkingIdx)
                panelWorkingIdx += 1
                # ? ? Setting-up (un-)mute button.
                self.unmuteButton = Widgets.Basics.Button(icon=GUtils.Icon.createFromLibrary(GUtils.Icon.StandardIcon.MediaVolumeMute), toolTip='(Un-)mute')
                self.unmuteButton.setEventHandler(GUtils.EventHandlers.ClickEventHandler(self.unmute))
                self.muteButton = Widgets.Basics.Button(icon=GUtils.Icon.createFromLibrary(GUtils.Icon.StandardIcon.MediaVolume), toolTip='(Un-)mute')
                self.muteButton.setEventHandler(GUtils.EventHandlers.ClickEventHandler(self.mute))
                self.muteContainer = Widgets.Containers.StackContainer([self.muteButton, self.unmuteButton], self.muteButton)
                self.panelLayout.setWidget(self.muteContainer, 0, panelWorkingIdx)
                panelWorkingIdx += 1
                
                # ? Every XXX-ms, a timer fires, to guarantee the seeker is sync'ed with the video (as it progresses).
                self.timer = GConcurrency.Timer(self.INTERNAL_timingEvent, TimeUtils.Time.createFromMilliseconds(50))
                self.timer.start()
                
                # ? Set-up key shortcut(s).
                self.renderer.setEventHandler(GUtils.EventHandlers.KeyPressEventHandler({
                    AbstractInput.Key.Space: self.togglePlay,
                    AbstractInput.Key.Letter_M: self.toggleMute,
                    
                    AbstractInput.Key.Up: lambda: self.adjustVolume(Widgets.Complex.VideoPlayer.Constants['Adjust-Volume-Delta']),
                    AbstractInput.Key.Down: lambda: self.adjustVolume(-1 * Widgets.Complex.VideoPlayer.Constants['Adjust-Volume-Delta']),

                    AbstractInput.Key.SquareBrackets_Left: lambda: self.seekBackward(Widgets.Complex.VideoPlayer.Constants['Skip-Time']['L0']),
                    AbstractInput.Key.SquareBrackets_Right: lambda: self.seekForward(Widgets.Complex.VideoPlayer.Constants['Skip-Time']['L0']),                    
                    AbstractInput.Key.SemiColon: lambda: self.seekBackward(Widgets.Complex.VideoPlayer.Constants['Skip-Time']['L1']),
                    AbstractInput.Key.Apostrophe: lambda: self.seekForward(Widgets.Complex.VideoPlayer.Constants['Skip-Time']['L1']),
                    AbstractInput.Key.Left: lambda: self.seekBackward(Widgets.Complex.VideoPlayer.Constants['Skip-Time']['L2']),
                    AbstractInput.Key.Right: lambda: self.seekForward(Widgets.Complex.VideoPlayer.Constants['Skip-Time']['L2']),
                    AbstractInput.Key.Comma: lambda: self.seekBackward(Widgets.Complex.VideoPlayer.Constants['Skip-Time']['L3']),
                    AbstractInput.Key.Dot: lambda: self.seekForward(Widgets.Complex.VideoPlayer.Constants['Skip-Time']['L3']),
                }))
                
                # ? Set-up context-menu of renderer.
                self.renderer.setContextMenu(GUtils.Menu([
                    GUtils.Menu.SubMenu('Copy', [
                        GUtils.Menu.EndPoint('(X, Y)', self.INTERNAL_contextMenu_copyMousePosition),
                        GUtils.Menu.EndPoint('HH:MM:SS.xxx', self.INTERNAL_contextMenu_copyVideoPosition),
                    ]),
                ]))
            
            def INTERNAL_timingEvent(self):
                videoDuration = int(self.renderer.getDuration())
                if videoDuration > 0:
                    ratio = int(self.renderer.getPosition()) / videoDuration
                    value = int(ratio * self.seekerMaxValue)
                    self.seeker.setValue(value)
            
            def INTERNAL_seeker_selectionChangeEvent(self):
                ratio = self.seeker.getValue() / self.seekerMaxValue
                videoDurationInMS = int(self.renderer.getDuration().toMilliseconds())
                
                seekTimeInMS = MathUtils.mapValue(ratio, [0.0, 1.0], [0, videoDurationInMS])
                self.renderer.seekPosition(TimeUtils.Time.createFromMilliseconds(seekTimeInMS))

            def INTERNAL_contextMenu_copyMousePosition(self):
                Clipboard.copy(str(self.renderer.getMousePosition()))

            def INTERNAL_contextMenu_copyVideoPosition(self):
                Clipboard.copy(str(self.renderer.getPosition()))

            def load(self, f:FileUtils.File):
                self.playPauseButton.setCurrentWidget(self.pauseButton)
                self.renderer.load(f)

            def loadDefault(self):
                '''
                Load default video.
                '''
                self.load(Widgets.Complex.VideoPlayer.Constants['Load-Default'])

            def seekForward(self, skipTime:TimeUtils.Time):
                self.renderer.seekForward(skipTime)

            def seekBackward(self, skipTime:TimeUtils.Time):
                self.renderer.seekBackward(skipTime)

            def seekPosition(self, time:TimeUtils.Time):
                self.renderer.seekPosition(time)

            def play(self):
                self.playPauseButton.setCurrentWidget(self.pauseButton)
                self.renderer.play()

            def pause(self):
                self.playPauseButton.setCurrentWidget(self.playButton)
                self.renderer.pause()

            def togglePlay(self):
                if self.renderer.isPlaying():
                    self.pause()
                else:
                    self.play()
            
            def restart(self):
                self.playPauseButton.setCurrentWidget(self.pauseButton)
                self.renderer.restart()
                
            def mute(self):
                self.muteContainer.setCurrentWidget(self.unmuteButton)
                self.renderer.mute()
            
            def unmute(self):
                self.muteContainer.setCurrentWidget(self.muteButton)
                self.renderer.unmute()

            def toggleMute(self):
                if self.renderer.isMute():
                    self.unmute()
                else:
                    self.mute()

            def setVolume(self, volume:int):
                self.renderer.setVolume(volume)

            def adjustVolume(self, delta:int):
                self.renderer.adjustVolume(delta)

            def getRenderer(self):
                return self.renderer

        class GIFPlayer(Widget):
            '''
            A GIF player.
            '''
            
            def __init__(self):
                self.renderer = Widgets.Basics.GIFRenderer()
                Widget.__init__(self, self.renderer.qWidget)

                # ? Set-up context-menu of renderer.
                self.renderer.setContextMenu(GUtils.Menu([
                    GUtils.Menu.SubMenu('Copy', [
                        GUtils.Menu.EndPoint('(X, Y)', self.INTERNAL_contextMenu_copyMousePosition),
                    ]),
                ]))
            
            def INTERNAL_contextMenu_copyMousePosition(self):
                Clipboard.copy(str(self.renderer.getMousePosition()))

            def getRenderer(self):
                '''
                Get underlying renderer.
                '''
                return self.renderer

        class ImageViewer(Widget):
            '''
            Am image viewer.
            '''
            
            def __init__(self):
                self.renderer = Widgets.Basics.ImageRenderer()
                Widget.__init__(self, self.renderer.qWidget)

                # ? Set-up context-menu of renderer.
                self.renderer.setContextMenu(GUtils.Menu([
                    GUtils.Menu.SubMenu('Copy', [
                        GUtils.Menu.EndPoint('(X, Y)', self.INTERNAL_contextMenu_copyMousePosition),
                    ]),
                ]))
            
            def INTERNAL_contextMenu_copyMousePosition(self):
                Clipboard.copy(str(self.renderer.getMousePosition()))

            def getRenderer(self):
                '''
                Get underlying renderer.
                '''
                return self.renderer

class Application:
    '''
    Only one instance of 'Application' is required.
    
    Note:
    - An 'Application' instance must be the first construction, before any element.
    '''
    
    def __init__(self):
        
        self.qApplication = QtWidgets.QApplication([])
        
        # PyQt6: A cross-platform style called 'Fusion'.
        self.qApplication.setStyle('Fusion')
        
    def run(self):
        '''
        Runs the GUI event-loop.
        '''
        self.qApplication.exec()
    
    def setIcon(self, icon:GUtils.Icon):
        '''
        Set application-wide icon.
        '''
        self.qApplication.icon = icon

class Dialog:
    '''
    A dialog is a blocking window (i.e., blocks execution of invoking GUI event-loop).
    '''
    
    def __init__(self, title:str, rootLayout:Layout, minimumSize, isSizeFixed=False):
        
        self.qDialog = QtWidgets.QDialog()
        
        # ? All other settings.
        if (isSizeFixed):
            self.qDialog.setFixedSize(minimumSize[0], minimumSize[1])
        else:
            self.qDialog.setMinimumSize(minimumSize[0], minimumSize[1])
        self.qDialog.setWindowTitle(title)
        self.qDialog.setWindowIcon(QtWidgets.QApplication.instance().icon.qIcon)
        
        # ? Setting root layout.
        self.qDialog.setLayout(rootLayout.qLayout)
        
    def run(self):
        '''
        Interrupt the current GUI event-loop, and run the dialog's.
        '''
        self.qDialog.exec()

class StandardDialog:
    '''
    Open a standard dialog, to get specific info.
    '''
    
    @staticmethod
    def selectExistingFile(initialDirectory:FileUtils.File):
        '''
        Select an existing file. Returns `None` if none were selected.
        '''
        path, _ = QtWidgets.QFileDialog.getOpenFileName(None, directory=str(initialDirectory))
        path = FileUtils.File(path) if (path != '') else None
        return path

    @staticmethod
    def selectExistingFiles(initialDirectory:FileUtils.File):
        '''
        Select existing files, returned as a list.
        '''
        paths, _ = QtWidgets.QFileDialog.getOpenFileNames(None, directory=str(initialDirectory))
        return [FileUtils.File(path) for path in paths]
    
    @staticmethod
    def selectExistingDirectory(initialDirectory:FileUtils.File):
        '''
        Select existing directory.
        '''
        path = QtWidgets.QFileDialog.getExistingDirectory(None, directory=str(initialDirectory))
        path = FileUtils.File(path) if (path != '') else None
        return path

    @staticmethod
    def selectFile(initialDirectory:FileUtils.File):
        '''
        Select a file. Returns `None` if none were selected.
        '''
        path, _ = QtWidgets.QFileDialog.getSaveFileName(None, directory=str(initialDirectory))
        path = FileUtils.File(path) if (path != '') else None
        return path
    
    @staticmethod
    def selectColor(initColor:ColorUtils.Color=None) -> ColorUtils.Color:
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

    class BackgroundActivity:
        '''
        Handles dialog, meant to block user until a background-activity completes.
        '''
        
        qProgressDialog:QtWidgets.QProgressDialog = None
        
        @staticmethod
        def awaitActivity():
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
            StandardDialog.BackgroundActivity.qProgressDialog = progressDialog

        @staticmethod
        def release():
            '''
            Closes dialog.
            '''
            StandardDialog.BackgroundActivity.qProgressDialog.close()
            StandardDialog.BackgroundActivity.qProgressDialog = None

class Window:
    '''
    Multiple window(s) may be created.
    '''
    
    def __init__(self, title:str, rootLayout:Layout, minimumSize, isSizeFixed=False, isEnableStatusBar=False):
        super().__init__()
        
        self.qWindow = QtWidgets.QMainWindow()
        
        # ? Setting root layout.
        self.qWindow.setCentralWidget(Widget.fromLayout(rootLayout).qWidget)
        
        # ? All other settings.
        if (isSizeFixed):
            self.qWindow.setFixedSize(minimumSize[0], minimumSize[1])
        else:
            self.qWindow.setMinimumSize(minimumSize[0], minimumSize[1])
        self.qWindow.setWindowTitle(title)
        self.qWindow.setWindowIcon(QtWidgets.QApplication.instance().icon.qIcon)
        
        # ? Enable status-bar (optional).
        if isEnableStatusBar:
            self.statusBar = QtWidgets.QStatusBar()
            self.qWindow.setStatusBar(self.statusBar)

    def setStatus(self, text:str):
        '''
        Update status-bar.
        '''
        self.statusBar.showMessage(text)

    def setTitle(self, title):
        '''
        Set title of window.
        '''
        self.qWindow.setWindowTitle(title)

    def createToolbar(self, menu:GUtils.Menu):
        '''
        Creates a Tool-bar.
        '''
        toolbar = QtWidgets.QToolBar()
        toolbar.setMovable(False)
        toolbar.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.PreventContextMenu)
        menu.INTERNAL_instantiate(toolbar, self.qWindow)
        self.qWindow.addToolBar(toolbar)

    def addMenu(self, menuName:str, menu:GUtils.Menu):
        '''
        Adds a menu(-entry), to the (menu-)bar.
        '''
        qMenuBar = self.qWindow.menuBar()
        qMenu = qMenuBar.addMenu('&' + menuName)
        menu.INTERNAL_instantiate(qMenu, self.qWindow)

    def show(self):
        '''
        Show window.
        '''
        self.qWindow.show()

    def hide(self):
        '''
        Hide window.
        '''
        self.qWindow.hide()