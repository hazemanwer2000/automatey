
# External Libraries
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui
import PyQt6.QtCore as QtCore
import vlc
import typing
import ctypes

# Internal Libraries
import automatey.GUI.GUtils as GUtils
import automatey.GUI.GConcurrency as GConcurrency
import automatey.Utils.ColorUtils as ColorUtils
import automatey.Abstract.Graphics as AbstractGraphics
import automatey.Abstract.Input as AbstractInput
import automatey.Utils.TimeUtils as TimeUtils
import automatey.OS.FileUtils as FileUtils
import automatey.Resources as Resources
import automatey.Utils.MathUtils as MathUtils
import automatey.GUI.Wrappers.PyQt6 as PyQt6Wrapper
import automatey.Utils.ExceptionUtils as ExceptionUtils
import automatey.Utils.StringUtils as StringUtils
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
    
            # ? Maintain widget list.
            self.widgetList = []

        def setWidget(self, widget, rowIdx, colIdx, rowSpan=1, colSpan=1):
            '''
            Set an element in a specific location within the grid.
            '''
            self.qLayout.addWidget(widget.qWidget, rowIdx, colIdx, rowSpan, colSpan)

            self.widgetList.append(widget)
        
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
            
            # ? Maintain widget list.
            self.widgetList = []

        HorizontalAlignment2AlignmentFlag = {
            AbstractGraphics.Alignment.Horizontal.Left: QtCore.Qt.AlignmentFlag.AlignLeft,
            AbstractGraphics.Alignment.Horizontal.Right: QtCore.Qt.AlignmentFlag.AlignRight,
            AbstractGraphics.Alignment.Horizontal.Center: QtCore.Qt.AlignmentFlag.AlignHCenter,
        }

        def insertWidget(self, widget, idx=-1, horizontalAlighnment=None):
            '''
            Insert widget at index.
            '''
            args = [idx, widget.qWidget]
            kwargs = {}
            if horizontalAlighnment != None:
                kwargs['alignment'] = Layouts.VerticalLayout.HorizontalAlignment2AlignmentFlag[horizontalAlighnment]
            self.qLayout.insertWidget(*args, **kwargs)
            
            # ? Update widget list.
            self.widgetList.insert((idx if (idx != -1) else self.getCount()), widget)

        def removeWidgetAtIndex(self, idx=-1):
            '''
            Remove widget at index.
            '''
            if idx == -1:
                idx = self.qLayout.count() - 1
            self.removeWidget(self.qLayout.itemAt(idx).widget())
            
            # ? Update widget list.
            self.widgetList.pop(idx)

        def removeWidget(self, widget):
            '''
            Remove widget.
            '''
            self.qLayout.removeWidget(widget.qWidget)
            widget.qWidget.setParent(None)

            # ? Update widget list.
            self.widgetList.remove(widget)
        
        def getCount(self):
            '''
            Get number of widget(s).
            '''
            return self.qLayout.count()

        def getWidgets(self):
            '''
            Get all widget(s), ordered.
            '''
            return self.widgetList

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

            # ? Maintain widget list.
            self.widgetList = []

        def insertWidget(self, widget, idx=-1):
            '''
            Insert widget at index.
            '''
            self.qLayout.insertWidget(idx, widget.qWidget, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

            # ? Update widget list.
            self.widgetList.insert((idx if (idx != -1) else self.getCount()), widget)

        def removeWidgetAtIndex(self, idx=-1):
            '''
            Remove widget at index.
            '''
            if idx == -1:
                idx = self.qLayout.count() - 1
            self.removeWidget(self.qLayout.itemAt(idx).widget())

            # ? Update widget list.
            self.widgetList.pop(idx)

        def removeWidget(self, widget):
            '''
            Remove widget.
            '''
            self.qLayout.removeWidget(widget.qWidget)
            widget.qWidget.setParent(None)

            # ? Update widget list.
            self.widgetList.remove(widget)

        def getCount(self):
            '''
            Get number of widget(s).
            '''
            return self.qLayout.count()

    class FlowLayout(Layout):
        '''
        A flow layout.
        '''
        def __init__(self, elementMargin:AbstractGraphics.Margin, elementSpacing:int):
            self.qLayout = PyQt6Wrapper.QFlowLayout()
            Layout.__init__(self, self.qLayout)

            # ? Other setting(s).
            self.qLayout.setContentsMargins(elementMargin.left,
                                    elementMargin.top,
                                    elementMargin.right,
                                    elementMargin.bottom)
            self.qLayout.setSpacing(elementSpacing)

            self.widgets = []

        def insertWidget(self, widget, idx=-1):
            '''
            Insert widget at index.
            '''
            if idx == -1:
                self.qLayout.addWidget(widget.qWidget)
                self.widgets.append(widget)
            else:
                self.qLayout.insertWidget(idx, widget.qWidget)
                self.widgets.insert(idx, widget)

        def removeWidgetAtIndex(self, idx=-1):
            '''
            Remove widget at index.
            '''
            if idx == -1:
                idx = self.qLayout.count() - 1
            self.removeWidget(self.qLayout.itemAt(idx).widget())
            self.widgets.pop(idx)

        def removeWidget(self, widget):
            '''
            Remove widget.
            '''
            self.qLayout.removeWidget(widget.qWidget)
            widget.qWidget.setParent(None)
            self.widgets.remove(widget)

        def getCount(self):
            '''
            Get number of widget(s).
            '''
            return self.qLayout.count()

class Widget:

    def __init__(self, qWidget:QtWidgets.QWidget):
        
        self.qWidget = qWidget
        self.fromLayoutRef = None

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
        widget.fromLayoutRef = layout
        return widget

class CustomWidget(Widget):
    '''
    Can be inherited from, to implement user-defined widget(s).
    '''
    
    def __init__(self, widget:Widget):
        self.widget = widget
        Widget.__init__(self, widget.qWidget)

class Widgets:

    class Decorators:
        
        class Margin(Widget):
            '''
            Adds a margin around the specified element.
            '''
            
            def __init__(self, widget, elementMargin:AbstractGraphics.Margin):
                Widget.__init__(self, QtWidgets.QWidget())
                
                # ? Setting element.
                self.layout = Layouts.GridLayout(1, 1, elementMargin=elementMargin, elementSpacing=0)
                self.layout.setWidget(widget, 0, 0, 1, 1)
                self.qWidget.setLayout(self.layout.qLayout)

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
                self.layout = Layouts.GridLayout(1, 1, elementMargin=elementMargin, elementSpacing=0)
                self.layout.setWidget(widget, 0, 0, 1, 1)
                self.qWidget.setLayout(self.layout.qLayout)

        class ScrollArea(Widget):
            '''
            Encapsulates any element, to allow for vertical/horizontal scrolling.
            '''
            
            def __init__(self, widget, elementMargin:AbstractGraphics.Margin, isVerticalScrollBar=False, isHorizontalScrollBar=False):
                self.qWidget = QtWidgets.QScrollArea()
                Widget.__init__(self, self.qWidget)
                
                # ? Apply decorator(s).
                self.marginDecorator = Widgets.Decorators.Margin(widget, elementMargin=elementMargin)

                # ? Set element.
                self.qWidget.setWidgetResizable(True)
                self.qWidget.setWidget(self.marginDecorator.qWidget)
                
                # ? Specify if vertical/horizontal scrolling is always on.
                
                verticalScrollBarPolicy = (QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn) if isVerticalScrollBar else (QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                horizontalScrollBarPolicy = (QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn) if isHorizontalScrollBar else (QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                
                self.qWidget.setVerticalScrollBarPolicy(verticalScrollBarPolicy)
                self.qWidget.setHorizontalScrollBarPolicy(horizontalScrollBarPolicy)
            
            def ensureWidgetVisible(self, widget):
                '''
                Ensure a widget is visible.
                '''
                self.qWidget.ensureWidgetVisible(widget.qWidget)

        class Central(Widget):
            '''
            For fixed-size widget(s), center widget within a stretching box.
            '''
            def __init__(self, widget):
                self.layout = Layouts.GridLayout(3, 3, AbstractGraphics.SymmetricMargin(0), 0)
                self.layout.setWidget(widget, 1, 1)
                Widget.__init__(self, Widget.fromLayout(self.layout).qWidget)

        class Titled(Widget):
            
            def __init__(self,
                         widget,
                         title:str,
                         isInnerOutline:bool=False,
                         isOuterOutline:bool=False,
                         elementMargin:AbstractGraphics.Margin=AbstractGraphics.SymmetricMargin(5),
                         elementSpacing:int=5):
                self.layout = Layouts.GridLayout(2, 1, AbstractGraphics.SymmetricMargin(0), elementSpacing)
                labelTitle = Widgets.Basics.Label(title)
                
                # ? (...)
                innerWidget = widget
                if isInnerOutline:
                    innerWidget = Widgets.Decorators.Outline(innerWidget, elementMargin)
                
                self.layout.setWidget(labelTitle, 0, 0)
                self.layout.setWidget(innerWidget, 1, 0)
                self.layout.setRowMinimumSize(0, 0)
                layoutsWidget = Widget.fromLayout(self.layout)
                
                # ? (...)
                self.outerWidget = layoutsWidget
                if isOuterOutline:
                    self.outerWidget = Widgets.Decorators.Outline(self.outerWidget, elementMargin)
                
                Widget.__init__(self, self.outerWidget.qWidget)

        class LineEditEraser(Widget):
            '''
            Add an erasing button, left to a line-edit.
            '''
            
            def __init__(self, lineEdit):
                # ? Construct erase button.
                self.eraseButton = Widgets.Basics.Button(icon=GUtils.Icon.createFromFile(Resources.resolve(FileUtils.File('icon/lib/coreui/cil-x.png'))))
                self.eraseButton.setEventHandler(GUtils.EventHandlers.ClickEventHandler(lambda: lineEdit.setText('')))
                # ? Construct layout.
                self.layout = Layouts.GridLayout(1, 2, AbstractGraphics.SymmetricMargin(0), 5)
                self.layout.setWidget(self.eraseButton, 0, 0)
                self.layout.setWidget(lineEdit, 0, 1)
                self.layout.setColumnMinimumSize(0, 0)
                Widget.__init__(self, Widget.fromLayout(self.layout).qWidget)

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

                # ? Maintain widget list.
                self.widgets = widgets
                    
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

            def getLayout(self) -> Layouts.VerticalLayout:
                '''
                Get underlying layout.
                '''
                return self.verticalLayout

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

            def getLayout(self) -> Layouts.HorizontalLayout:
                '''
                Get underlying layout.
                '''
                return self.horizontalLayout

        class TabContainer(Widget, INTERNAL.EventManager):
            '''
            Tabs, to switch between different widget(s).
            '''
            
            def __init__(self, tabNames, widgets, initTabIndex=0):
                self.qTabWidget = QtWidgets.QTabWidget()
                Widget.__init__(self, self.qTabWidget)
                INTERNAL.EventManager.__init__(self)

                # ? Maintain widget list.
                self.widgets = widgets
                                
                # ? Adding tab(s) in-order.
                for tabName, widget in zip(tabNames, widgets):
                    self.qTabWidget.addTab(widget.qWidget, tabName)
                    
                # ? Register event-handler(s).
                self.qTabWidget.currentChanged.connect(self.INTERNAL_currentTabChanged)
                
                # ? Select initial tab.
                self.qTabWidget.setCurrentIndex(initTabIndex)
            
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
        
        class Null(Widget):
            '''
            A widget with no appearance.
            '''
            def __init__(self, size=None):
                Widget.__init__(self, PyQt6Wrapper.QWidget())
                
                # ? Set (i.e., fix) size, if specified.
                if size != None:
                    self.qWidget.setFixedSize(size[0], size[1])

        class ColorBlock(Widget, INTERNAL.EventManager):
            '''
            A simple color-block.
            '''
            
            def __init__(self, initColor:ColorUtils.Color, size=None):
                self.qWidget = PyQt6Wrapper.QWidget()
                Widget.__init__(self, self.qWidget)
                INTERNAL.EventManager.__init__(self)
                
                # ? Setting fill-color of widget.
                self.setColor(initColor)
                self.color = initColor
                
                # ? Set (i.e., fix) size, if specified.
                if size != None:
                    self.qWidget.setFixedSize(size[0], size[1])

                # ? Setup event-handler(s).
                self.qWidget.mousePressEventFcn = self.INTERNAL_mousePressEvent

            def INTERNAL_mousePressEvent(self, event):
                if GUtils.EventHandlers.ClickEventHandler in self.eventHandlers:
                    self.eventHandlers[GUtils.EventHandlers.ClickEventHandler].fcn()

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
            
            def __init__(self, text:str=None, icon:GUtils.Icon=None, toolTip=None, isCheckable:bool=False):
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
                
                # ? Set checkable (optional).
                self.qButton.setCheckable(isCheckable)
                
                # ? Event-handlers.
                self.qButton.clicked.connect(self.INTERNAL_onClicked)
                
                # PyQt6: Force widget not to be focusable.
                self.qButton.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                
            def INTERNAL_onClicked(self):
                if GUtils.EventHandlers.ClickEventHandler in self.eventHandlers:
                    self.eventHandlers[GUtils.EventHandlers.ClickEventHandler].fcn()

            def isChecked(self) -> bool:
                return self.qButton.isChecked()
            
            def setChecked(self, flag:bool):
                self.qButton.setChecked(flag)

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

            def __bool__(self):
                return self.isChecked()
            
            def __str__(self):
                return str(bool(self))

        class List(Widget, INTERNAL.EventManager):
            '''
            A list of items.
            '''
            
            def __init__(self, itemList, isMultiSelection=False, isDragNDrop=False):
                self.qWidget = PyQt6Wrapper.QListWidget()
                INTERNAL.EventManager.__init__(self)
                Widget.__init__(self, self.qWidget)
                
                self.qWidget.addItems(itemList)
                
                if isMultiSelection:
                    self.qWidget.setSelectionMode(self.qWidget.SelectionMode.MultiSelection)
                
                if isDragNDrop:
                    self.qWidget.setDragDropMode(QtWidgets.QListWidget.DragDropMode.InternalMove)
                
                # PyQt6: Enforce that the scroll-bar is always present.
                self.qWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
                
                # ? Event-handlers.
                self.qWidget.itemSelectionChanged.connect(self.INTERNAL_itemSelectionChange)
                self.qWidget.dropEventFcn = self.INTERNAL_dropEvent
            
            def INTERNAL_dropEvent(self, event):
                if GUtils.EventHandlers.OrderChangeEventHandler in self.eventHandlers:
                    self.eventHandlers[GUtils.EventHandlers.OrderChangeEventHandler].fcn()
            
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

            def getAllItems(self):
                '''
                Get all item(s), ordered.
                '''
                items = []
                for i in range(self.getCount()):
                    items.append(self.qWidget.item(i).text())
                return items

            def getCount(self):
                '''
                Get number of items.
                '''
                return self.qWidget.count()

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

            def setEditable(self, flag:bool):
                self.qWidget.setEnabled(flag)

            def __int__(self):
                return self.getValue()

            def __str__(self):
                return str(int(self))

        class DropDownList(Widget, INTERNAL.EventManager):
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
                return self.qWidget.currentText()
            
            def getSelectedIndex(self):
                '''
                Get index of the current item.
                '''
                return self.qWidget.currentIndex()

            def INTERNAL_currentIndexChanged(self, newIndex):
                if GUtils.EventHandlers.SelectionChangeEventHandler in self.eventHandlers:
                    self.eventHandlers[GUtils.EventHandlers.SelectionChangeEventHandler].fcn()

            def __str__(self):
                return str(self.getSelected())

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
            
            def setText(self, text):
                '''
                Set text.
                '''
                return self.qWidget.setText(text)
            
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

            def __str__(self):
                return self.getText()

        class TextEdit(Widget, INTERNAL.EventManager):
            
            def __init__(self, placeholder:str=None, isEditable=True, isMonospaced=False, isWrapText=False, isVerticalScrollBar:bool=True, isHorizontalScrollBar:bool=True, height:int=0):
                self.qWidget = PyQt6Wrapper.QPlainTextEdit()
                INTERNAL.EventManager.__init__(self)
                Widget.__init__(self, self.qWidget)
                
                if placeholder != None:
                    self.qWidget.setPlaceholderText(placeholder)
                    
                # ? Event-handler(s).
                self.qWidget.textChanged.connect(self.INTERNAL_textChanged)
                self.qWidget.keyPressEventFcn = self.INTERNAL_keyPressEvent
                self.qWidget.mousePressEventFcn = self.INTERNAL_mousePressEvent
                
                # ? By default, text is not wrapped.
                if not isWrapText:
                    self.qWidget.setWordWrapMode(QtGui.QTextOption.WrapMode.NoWrap)
            
                # ? By default, font is 'Monospace'.
                if isMonospaced:
                    font = QtGui.QFont("Consolas")
                    font.setStyleHint(QtGui.QFont.StyleHint.Monospace)
                    self.qWidget.setFont(font)
                
                # ? By default, Scroll-Bar is displayed.
                if not isVerticalScrollBar:
                    self.qWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                if not isHorizontalScrollBar:
                    self.qWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

                # ? Set height, if specified.
                if height != 0:
                    self.qWidget.setFixedHeight(height)

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
                return self.qWidget.toPlainText()

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

            def INTERNAL_mousePressEvent(self, event):
                if GUtils.EventHandlers.ClickEventHandler in self.eventHandlers:
                    self.eventHandlers[GUtils.EventHandlers.ClickEventHandler].fcn()

            def __str__(self):
                return self.getText()

        class EntryTable(Widget):
            '''
            An input entry-table.
            '''
            
            def __init__(self, header:list):
                self.layout = Layouts.GridLayout(1, 2, elementMargin=AbstractGraphics.SymmetricMargin(0), elementSpacing=5)
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
                self.verticalContainer = Widgets.Containers.VerticalContainer(elementMargin=AbstractGraphics.SymmetricMargin(0), elementSpacing=5)
                self.layout.setWidget(self.verticalContainer, 0, 0)
                self.layout.setColumnMinimumSize(0, 0)
                # ? ? Create insert button.
                self.insertButton = Widgets.Basics.Button(icon=GUtils.Icon.createFromFile(Resources.resolve(FileUtils.File('icon/lib/coreui/cil-plus.png'))), toolTip='Insert')
                self.insertButton.setEventHandler(GUtils.EventHandlers.ClickEventHandler(self.INTERNAL_insertButton_clickEvent))
                self.verticalContainer.getLayout().insertWidget(self.insertButton)
                # ? ? Create move-up button.
                self.moveUpButton = Widgets.Basics.Button(icon=GUtils.Icon.createFromFile(Resources.resolve(FileUtils.File('icon/lib/coreui/cil-arrow-top.png'))), toolTip='Move Up')
                self.moveUpButton.setEventHandler(GUtils.EventHandlers.ClickEventHandler(self.INTERNAL_moveUpButton_clickEvent))
                self.verticalContainer.getLayout().insertWidget(self.moveUpButton)
                # ? ? Create move-down button.
                self.moveDownButton = Widgets.Basics.Button(icon=GUtils.Icon.createFromFile(Resources.resolve(FileUtils.File('icon/lib/coreui/cil-arrow-bottom.png'))), toolTip='Move Down')
                self.moveDownButton.setEventHandler(GUtils.EventHandlers.ClickEventHandler(self.INTERNAL_moveDownButton_clickEvent))
                self.verticalContainer.getLayout().insertWidget(self.moveDownButton)
                # ? ? Create delete button.
                self.deleteButton = Widgets.Basics.Button(icon=GUtils.Icon.createFromFile(Resources.resolve(FileUtils.File('icon/lib/coreui/cil-x.png'))), toolTip='Delete')
                self.deleteButton.setEventHandler(GUtils.EventHandlers.ClickEventHandler(self.INTERNAL_deleteButton_clickEvent))
                self.verticalContainer.getLayout().insertWidget(self.deleteButton)
                
                # ? Setup context-menu.
                self.qTableWidget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
                self.qTableWidget.customContextMenuRequested.connect(self.INTERNAL_contextMenuEvent)
                self.qContextMenu:QtWidgets.QMenu = None
                # ? ? Context-Info is meant to be fetched by the user, within a context-menu handler. 
                self.contextInfo = {
                    'row-index' : 0,
                    'column-index' : 0,
                }
            
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

            def INTERNAL_setEntry(self, idx, data:dict):
                '''
                Set entry, from a list of string(s).
                '''
                for columnIdx, columnTitle in enumerate(self.header):
                    self.qTableWidget.setItem(idx, columnIdx, QtWidgets.QTableWidgetItem(data[columnTitle]))
            
            def INTERNAL_swapEntries(self, idx1, idx2):
                '''
                Swap entries.
                '''
                data1 = self.getEntry(idx1)
                data2 = self.getEntry(idx2)
                self.INTERNAL_setEntry(idx2, data1)
                self.INTERNAL_setEntry(idx1, data2)

            def INTERNAL_contextMenuEvent(self, pos:QtCore.QPoint):

                if self.qContextMenu != None:
                    item = self.qTableWidget.itemAt(pos)
                    # ? If triggered on a non-empty cell. 
                    if item != None:
                        self.contextInfo['row-index'] = item.row()
                        self.contextInfo['column-index'] = item.column()
                        self.qContextMenu.exec(self.qTableWidget.viewport().mapToGlobal(pos))

            def getContextInfo(self) -> dict:
                '''
                Context-Info is meant to be fetched by the user, within a context-menu handler. 
                
                Returns,
                - `row`: Row of relevant cell.
                - `column`: Column of relevant cell.
                '''
                return self.contextInfo

            def setContextMenu(self, menu:GUtils.Menu):
                '''
                Set context menu.
                
                Note that, it is shown only if on a cell, and cell is not empty.
                '''
                self.qContextMenu = QtWidgets.QMenu()
                menu.INTERNAL_instantiate(self.qContextMenu, self.qWidget)

            def getCell(self, rowIdx:int, colIdx:int):
                '''
                Get cell.
                '''
                qItem = self.qTableWidget.item(rowIdx, colIdx)
                text = qItem.text().strip() if (qItem != None) else ''
                return text

            def getEntry(self, idx) -> dict:
                '''
                Get entry.
                '''
                columnCount = self.qTableWidget.columnCount()
                data = []
                for columnIdx in range(columnCount):
                    qItem = self.qTableWidget.item(idx, columnIdx)
                    data.append(qItem.text().strip() if (qItem != None) else '')
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
                self.qWidget.wheelEventFcn = self.INTERNAL_wheelEvent
            
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
            
            def INTERNAL_wheelEvent(self, event:QtGui.QWheelEvent):
                if GUtils.EventHandlers.ScrollEventHandler in self.eventHandlers:
                    scrollEventHandler:GUtils.EventHandlers.ScrollEventHandler = self.eventHandlers[GUtils.EventHandlers.ScrollEventHandler]
                    # ? Case: Scroll-up.
                    if event.angleDelta().y() > 0:
                        if scrollEventHandler.scrollUpFcn != None:
                            scrollEventHandler.scrollUpFcn()
                    # ? Case: Scroll-down.
                    else:
                        if scrollEventHandler.scrollDownFcn != None:
                            scrollEventHandler.scrollDownFcn()
            
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

        class Tree(Widget):

            '''
            An expandable tree display of (information-)node(s).

            Notes:
            - `rootNode` must satisfy the specified `Node` interface.
            - `header` must specify the column name(s), as a list of string(s).
            '''

            def __init__(self, rootNode:"Widgets.Basics.Tree.Node", header:typing.List[str]):

                self.qWidget = QtWidgets.QTreeWidget()
                super().__init__(self.qWidget)

                self.qWidget.setColumnCount(len(header))
                self.qWidget.setHeaderLabels(header)

                self.qWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
                self.qWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

                # ? Setup context menu.
                self.qWidget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
                self.qWidget.customContextMenuRequested.connect(self.INTERNAL_onContextMenu)
                self.contextInfo = {
                    'node' : None
                }
                self.contextMenuCallout = None
                self.contextMenuPos = None

                self.INTERNAL_constructTree(self.qWidget, rootNode)

                # ? Setup on-collapse handler.
                self.qWidget.itemCollapsed.connect(self.INTERNAL_onItemCollapsed)

            def expandAll(self, node:"Widgets.Basics.Tree.Node"=None):
                if node is None:
                    self.qWidget.expandAll()
                else:
                    self.INTERNAL_expandRecursive(node.INJECTED_qItem)

            def INTERNAL_expandRecursive(self, qItem:QtWidgets.QTreeWidgetItem):
                for idx in range(qItem.childCount()):
                    qChildItem = qItem.child(idx)
                    self.qWidget.expandItem(qChildItem)
                    self.INTERNAL_expandRecursive(qChildItem)

            def collapseAll(self, node:"Widgets.Basics.Tree.Node"=None):
                if node is None:
                    self.qWidget.collapseAll()
                else:
                    self.INTERNAL_collapseRecursive(node.INJECTED_qItem)

            def INTERNAL_collapseRecursive(self, qItem:QtWidgets.QTreeWidgetItem):
                for idx in range(qItem.childCount()):
                    qChildItem = qItem.child(idx)
                    self.qWidget.collapseItem(qChildItem)
                    self.INTERNAL_collapseRecursive(qChildItem)

            def INTERNAL_onItemCollapsed(self, qItem:QtWidgets.QTreeWidgetItem):
                self.INTERNAL_collapseRecursive(qItem)

            def resizeColumnsToContents(self, offset=0):
                for idx in range(self.qWidget.columnCount()):
                    self.qWidget.resizeColumnToContents(idx)
                    self.qWidget.setColumnWidth(idx, self.qWidget.columnWidth(idx) + offset)

            def setContextMenuCallout(self, callout):
                '''
                Set context menu callout, called whenever a context menu is requested.
                '''
                self.contextMenuCallout = callout

            def showContextMenu(self, menu:GUtils.Menu):
                '''
                Called to show a context menu.

                Note: Must be called within a context menu callout.
                '''
                qMenu = QtWidgets.QMenu()
                menu.INTERNAL_instantiate(qMenu, self.qWidget)
                qMenu.exec(self.qWidget.viewport().mapToGlobal(self.contextMenuPos))

            def getContextInfo(self) -> "Widgets.Basics.Tree.Node":
                '''
                Context-Info is meant to be fetched by the user, within a context-menu handler. 
                
                Returns the currently selected node.
                '''
                return self.contextInfo['node']

            def INTERNAL_onContextMenu(self, pos:QtCore.QPoint):

                if self.contextMenuCallout is not None:
                    qCurrentItem = self.qWidget.currentItem()
                    if qCurrentItem is not None:
                        self.contextInfo['node'] = qCurrentItem.INJECTED_node
                        self.contextMenuPos = pos
                        self.contextMenuCallout()

            def construct(self, rootNode:"Widgets.Basics.Tree.Node"):
                '''
                (Re-)construct tree.
                '''
                self.qWidget.clear()
                self.INTERNAL_constructTree(self.qWidget, rootNode)

            @staticmethod
            def INTERNAL_constructTree(qParentWidget, node:"Widgets.Basics.Tree.Node"):
                '''
                Recursively, constructs the GUI tree based on an (information-)node.
                '''
                qTreeWidgetItem = QtWidgets.QTreeWidgetItem(qParentWidget, node.getAttributes())
                qTreeWidgetItem.INJECTED_node = node
                node.INJECTED_qItem = qTreeWidgetItem

                for childNode in node.getChildren():
                    Widgets.Basics.Tree.INTERNAL_constructTree(qTreeWidgetItem, childNode)
            
            def refresh(self, node:"Widgets.Basics.Tree.Node", isRecursive:bool=False):
                '''
                Refresh attributes of node (and optinally, sub-node(s)).
                '''
                # ? Refresh node.
                qTreeWidgetItem = node.INJECTED_qItem
                attributes = node.getAttributes()
                for idx in range(self.qWidget.columnCount()):
                    qTreeWidgetItem.setText(idx, attributes[idx])

                # ? Invoke on sub-node(s), if specified.
                if isRecursive:
                    for subNode in node.getChildren():
                        self.refresh(subNode, isRecursive)

            class Node:

                def __init__(self):
                    pass

                def getChildren(self) -> typing.List["Widgets.Basics.Tree.Node"]:
                    '''
                    (Interface) Must return a list of a (sub-)node(s).
                    '''
                    pass

                def getAttributes(self) -> typing.List[str]:
                    '''
                    (Interface) Must return the column value(s), as a list of string(s).
                    '''
                    pass

    class Complex:

        class ColorSelector(Widget):
            '''
            Color displayer, and selector.
            '''
            
            def __init__(self, initColor:ColorUtils.Color):
                # ? Set initial color, and (fixed-)size.
                self.colorBlock = Widgets.Basics.ColorBlock(initColor=initColor, size=[30, 30])
                Widget.__init__(self, self.colorBlock.qWidget)
                self.colorBlock.setEventHandler(GUtils.EventHandlers.ClickEventHandler(self.INTERNAL_colorBlock_onClick))
            
            def getColor(self):
                return self.colorBlock.getColor()
                
            def INTERNAL_colorBlock_onClick(self):
                newColor = StandardDialog.selectColor(initColor=self.colorBlock.getColor())
                if newColor != None:
                    self.colorBlock.setColor(newColor)
            
            def __str__(self):
                return str(self.getColor())

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
                self.rootLayout = Layouts.GridLayout(2, 1, AbstractGraphics.SymmetricMargin(0), 5)
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
                self.renderer.setEventHandler(GUtils.EventHandlers.ScrollEventHandler(
                    scrollUpFcn = lambda: self.adjustVolume(Widgets.Complex.VideoPlayer.Constants['Adjust-Volume-Delta']),
                    scrollDownFcn = lambda: self.adjustVolume(-1 * Widgets.Complex.VideoPlayer.Constants['Adjust-Volume-Delta']),
                ))
                
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

        class FilterList(Widget):
            
            def __init__(self, filterOptionClassList:typing.List["FilterOption"],
                               isSingleOptionInstance=True,
                               selectedColor:ColorUtils.Color=ColorUtils.Colors.BLACK,
                               deselectedColor:ColorUtils.Color=ColorUtils.Colors.GREY):
                
                self.filterOptionClassList = filterOptionClassList
                self.isSingleOptionInstance = isSingleOptionInstance
                self.selectedColor = selectedColor
                self.deselectedColor = deselectedColor
                
                # ? Construct `FilterOptionContainer`.
                self.filterOptDecContainer = Widgets.Containers.VerticalContainer(elementMargin=AbstractGraphics.SymmetricMargin(0), elementSpacing=5)
                self.filterOptDecContainerScrollArea = Widgets.Decorators.ScrollArea(self.filterOptDecContainer, elementMargin=AbstractGraphics.SymmetricMargin(5), isVerticalScrollBar=True)
                
                # ? Construct `DropDownList`.
                self.dropDownList = Widgets.Basics.DropDownList([filterOptionClass.getName() for filterOptionClass in filterOptionClassList])
                
                # ? Construct `ButtonContainer`.
                self.buttonContainer = Widgets.Containers.VerticalContainer(elementMargin=AbstractGraphics.SymmetricMargin(0), elementSpacing=5)
                
                # ? ? Create insert button.
                self.insertButton = Widgets.Basics.Button(icon=GUtils.Icon.createFromFile(Resources.resolve(FileUtils.File('icon/lib/coreui/cil-plus.png'))), toolTip='Insert')
                self.insertButton.setEventHandler(GUtils.EventHandlers.ClickEventHandler(self.INTERNAL_insertButton_clickEvent))
                self.buttonContainer.getLayout().insertWidget(self.insertButton)
                # ? ? Create move-up button.
                self.moveUpButton = Widgets.Basics.Button(icon=GUtils.Icon.createFromFile(Resources.resolve(FileUtils.File('icon/lib/coreui/cil-arrow-top.png'))), toolTip='Move Up')
                self.moveUpButton.setEventHandler(GUtils.EventHandlers.ClickEventHandler(self.INTERNAL_moveUpButton_clickEvent))
                self.buttonContainer.getLayout().insertWidget(self.moveUpButton)
                # ? ? Create move-down button.
                self.moveDownButton = Widgets.Basics.Button(icon=GUtils.Icon.createFromFile(Resources.resolve(FileUtils.File('icon/lib/coreui/cil-arrow-bottom.png'))), toolTip='Move Down')
                self.moveDownButton.setEventHandler(GUtils.EventHandlers.ClickEventHandler(self.INTERNAL_moveDownButton_clickEvent))
                self.buttonContainer.getLayout().insertWidget(self.moveDownButton)
                # ? ? Create delete button.
                self.deleteButton = Widgets.Basics.Button(icon=GUtils.Icon.createFromFile(Resources.resolve(FileUtils.File('icon/lib/coreui/cil-x.png'))), toolTip='Delete')
                self.deleteButton.setEventHandler(GUtils.EventHandlers.ClickEventHandler(self.INTERNAL_deleteButton_clickEvent))
                self.buttonContainer.getLayout().insertWidget(self.deleteButton)
                
                # ? Construct root layout.
                rootLayout = Layouts.GridLayout(2, 2, elementMargin=AbstractGraphics.SymmetricMargin(0), elementSpacing=5)
                rootLayout.setWidget(self.filterOptDecContainerScrollArea, 1, 1)
                rootLayout.setWidget(self.dropDownList, 0, 1)
                rootLayout.setWidget(self.buttonContainer, 0, 0, rowSpan=2)
                rootLayout.setRowMinimumSize(0, 0)
                rootLayout.setColumnMinimumSize(0, 0)
                Widget.__init__(self, Widget.fromLayout(rootLayout).qWidget)

                # ? Track currently selected filter-option.
                self.selectedFilterOptDec = None

            def getData(self):
                '''
                Collect data, as a list.
                '''
                filterOptDecList = self.filterOptDecContainer.getLayout().getWidgets()
                return [filterOptDec.filterOption.getData() for filterOptDec in filterOptDecList]
            
            def INTERNAL_ensureSelectedOptionVisible(self):
                if self.selectedFilterOptDec != None:
                    self.filterOptDecContainerScrollArea.ensureWidgetVisible(self.selectedFilterOptDec)
                        
            def INTERNAL_insertButton_clickEvent(self):
                
                filterOptDecList = self.filterOptDecContainer.getLayout().getWidgets()
                presentFilterOptClasses = [type(filterOptDec.filterOption) for filterOptDec in filterOptDecList]
                targetFilterOptClass = self.filterOptionClassList[self.dropDownList.getSelectedIndex()]
                
                if (not self.isSingleOptionInstance) or (self.isSingleOptionInstance and (targetFilterOptClass not in presentFilterOptClasses)):

                    # PyQt6: Called at the beginning (i.e., not at the end, as would be expected), because newly created option,
                    #          to be selected, is not fully created yet by 'Qt'. Hence, will scroll to (N-1) widget option.
                    self.INTERNAL_ensureSelectedOptionVisible()           
                    
                    # ? Create filter-option.
                    newFilterOption = targetFilterOptClass()
                    newFilterOptionDec = Widgets.Complex.FilterList.INTERNAL_FilterOptionDecorator(newFilterOption,
                                                                                                selectedColor=self.selectedColor,
                                                                                                deselectedColor=self.deselectedColor)
                    newFilterOptionDec.selectionNotificationFcn = self.INTERNAL_filterOptDec_selectionNotification
                    
                    # ? Insert filter-option.
                    insertionIdx = -1
                    
                    # ? ? If there's a selected option (...)
                    if self.selectedFilterOptDec != None:
                        
                        # ? ? Insertion occurs after selected option.
                        selectedIdx = filterOptDecList.index(self.selectedFilterOptDec)
                        insertionIdx = selectedIdx + 1
                        
                        # ? ? De-select currently selected option.
                        self.selectedFilterOptDec.deselect()
                    
                    # ? Select filter option, and update selection.
                    self.selectedFilterOptDec = newFilterOptionDec
                    newFilterOptionDec.select()
                    
                    # ? Insert option.
                    self.filterOptDecContainer.getLayout().insertWidget(newFilterOptionDec, idx=insertionIdx)
            
            def INTERNAL_moveUpButton_clickEvent(self):
                
                if self.selectedFilterOptDec != None:
                    
                    filterOptDecList = self.filterOptDecContainer.getLayout().getWidgets()
                    selectedIdx = filterOptDecList.index(self.selectedFilterOptDec)
                    
                    # ? Case: Selected index is not zero.
                    if selectedIdx > 0:
                        # ? ? Move filter-option up.
                        self.filterOptDecContainer.getLayout().removeWidget(self.selectedFilterOptDec)
                        self.filterOptDecContainer.getLayout().insertWidget(self.selectedFilterOptDec, idx=(selectedIdx - 1))
                    
                    self.INTERNAL_ensureSelectedOptionVisible()
            
            def INTERNAL_moveDownButton_clickEvent(self):

                if self.selectedFilterOptDec != None:
                    
                    filterOptDecList = self.filterOptDecContainer.getLayout().getWidgets()
                    selectedIdx = filterOptDecList.index(self.selectedFilterOptDec)
                    count = len(filterOptDecList)
                    
                    # ? Case: Selected index is not zero.
                    if selectedIdx < (count - 1):
                        # ? ? Move filter-option down.
                        self.filterOptDecContainer.getLayout().removeWidget(self.selectedFilterOptDec)
                        self.filterOptDecContainer.getLayout().insertWidget(self.selectedFilterOptDec, idx=(selectedIdx + 1))
                    
                    self.INTERNAL_ensureSelectedOptionVisible()
            
            def INTERNAL_deleteButton_clickEvent(self):
                
                if self.selectedFilterOptDec != None:

                    filterOptDecList = self.filterOptDecContainer.getLayout().getWidgets()
                    selectedIdx = filterOptDecList.index(self.selectedFilterOptDec)
                    count = len(filterOptDecList)
                    
                    # ? Find next filter-option. 
                    nextFilterOptDec = None 
                    
                    # ? ? Case: If current option(s) are more than one.
                    if count > 1:
                        # ? ? Case: Selected option is last option.
                        if selectedIdx == (count - 1):
                            nextFilterOptDecIdx = selectedIdx - 1
                        else:
                            nextFilterOptDecIdx = selectedIdx + 1
                        nextFilterOptDec = filterOptDecList[nextFilterOptDecIdx]

                    # ? Discard selected filter-option.
                    self.filterOptDecContainer.getLayout().removeWidget(self.selectedFilterOptDec)
                    self.selectedFilterOptDec.discard()
                    self.selectedFilterOptDec = None
                    
                    # ? Select next filter-option (if applicable).
                    if nextFilterOptDec != None:
                        nextFilterOptDec.select()
                        self.selectedFilterOptDec = nextFilterOptDec
                    
                    self.INTERNAL_ensureSelectedOptionVisible()
            
            def INTERNAL_filterOptDec_selectionNotification(self, selectedFilterOptDec:"Widgets.Complex.FilterList.INTERNAL_FilterOptionDecorator"):
                
                # ? De-select all, except (...)
                for filterOptDec in self.filterOptDecContainer.getLayout().getWidgets():
                    filterOptDec.deselect()
                selectedFilterOptDec.select()

                # ? Track currently selected filter-option.
                self.selectedFilterOptDec = selectedFilterOptDec

            class FilterOption(CustomWidget):
                '''
                (Interface) A filter option.
                
                Interface includes:
                - `getName` class-method, to get the name of option.
                - `getData` method, to collect data (abstract), and return it.
                '''
                def getData(self):
                    '''
                    (Interface) Collects data.
                    '''
                    return None

                @classmethod
                def getName(cls) -> str:
                    '''
                    (Interface) Get name.
                    '''
                    return '-'.join(StringUtils.Split.atWords(cls.__name__))
                
            class INTERNAL_FilterOptionDecorator(Widget):
                
                def __init__(self, filterOption:"Widgets.Complex.FilterList.FilterOption",
                                   selectedColor:ColorUtils.Color,
                                   deselectedColor:ColorUtils.Color):
                    
                    self.filterOption = filterOption
                    self.selectedColor = selectedColor
                    self.deselectedColor = deselectedColor
                    
                    # ? Setup color block (i.e., selector).
                    self.colorBlock = Widgets.Basics.ColorBlock(deselectedColor)
                    
                    # ? ? Setup root layout.
                    self.layout = Layouts.GridLayout(1, 2, elementMargin=AbstractGraphics.SymmetricMargin(0), elementSpacing=5)
                    self.layout.setWidget(self.colorBlock, 0, 0)
                    self.layout.setWidget(self.filterOption, 0, 1)
                    self.layout.setColumnMinimumSize(0, 10)
                    Widget.__init__(self, Widget.fromLayout(self.layout).qWidget)
                    
                    # ? Setup event-handler(s).
                    self.colorBlock.setEventHandler(GUtils.EventHandlers.ClickEventHandler(self.INTERNAL_colorBlock_onClick))
                    
                    # ? Setup registerable notification(s).
                    self.selectionNotificationFcn = None
                    
                def INTERNAL_colorBlock_onClick(self):
                    if self.selectionNotificationFcn != None:
                        self.selectionNotificationFcn(self)
                
                def select(self):
                    self.colorBlock.setColor(self.selectedColor)
                    
                def deselect(self):
                    self.colorBlock.setColor(self.deselectedColor)

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
        
        # (!) OS-specific (Windows-OS)
        # ? Workaround, to display app's icon in Windows task-bar.
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('mycompany.myproduct.subproduct.version')
        
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
        
    def run(self) -> bool:
        '''
        Interrupt the current GUI event-loop, and run the dialog's.
        
        Returns `True` if dialog is not force-closed.
        '''
        return self.qDialog.exec() == QtWidgets.QDialog.DialogCode.Accepted
    
    def accept(self):
        '''
        Accept dialog.
        '''
        self.qDialog.accept()

    def reject(self):
        '''
        Reject dialog.
        '''
        self.qDialog.reject()

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

    @staticmethod
    def showInformation(title:str, text:str, minimumSize, isSizeFixed:bool):
        # ? (...)
        textEdit = Widgets.Basics.TextEdit(isEditable=False, isMonospaced=True)
        textEdit.setText(text)
        # ? (...)
        rootLayout = Layouts.GridLayout(1, 1, elementMargin=AbstractGraphics.SymmetricMargin(5), elementSpacing=0)
        rootLayout.setWidget(textEdit, 0, 0)
        # ? (...)
        dialog = Dialog(title=title, rootLayout=rootLayout, minimumSize=minimumSize, isSizeFixed=isSizeFixed)
        dialog.run()

    @staticmethod
    def selectFromList(title:str, itemList:typing.List[str], minimumSize) -> int:
        '''
        Select an item from list, and return its index.
        
        If dialog is rejected (e.g., closed), `-1` is returned.
        '''
        listWidget = Widgets.Basics.List(itemList)
        selectButton = Widgets.Basics.Button('Select')
        # ? (...)
        rootLayout = Layouts.GridLayout(2, 2, elementMargin=AbstractGraphics.SymmetricMargin(5), elementSpacing=5)
        rootLayout.setWidget(listWidget, rowIdx=0, colIdx=0, colSpan=2)
        rootLayout.setWidget(selectButton, rowIdx=1, colIdx=1)
        rootLayout.setRowMinimumSize(1, 0)
        rootLayout.setColumnMinimumSize(1, 0)
        # ? (...)
        dialog = Dialog(title=title, rootLayout=rootLayout, minimumSize=minimumSize, isSizeFixed=True)
        selectButton.setEventHandler(GUtils.EventHandlers.ClickEventHandler(lambda: dialog.accept()))
        result = dialog.run()
        return (listWidget.getSelectedIndex() if result else -1)

    class Message:
        
        class Announce:
            '''
            Announce information to the user.
            '''
            
            def INTERNAL_Announce(title:str, msg:str, qIcon):
                qMsgBox = QtWidgets.QMessageBox(None)
                qMsgBox.setWindowTitle(title)
                qMsgBox.setText(msg)
                qMsgBox.setWindowIcon(QtWidgets.QApplication.instance().icon.qIcon)
                qMsgBox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
                qMsgBox.setIcon(qIcon)
                qMsgBox.exec()
        
            def Error(msg:str):
                StandardDialog.Message.Announce.INTERNAL_Announce('Error', msg, QtWidgets.QMessageBox.Icon.Critical)

            def Warning(msg:str):
                StandardDialog.Message.Announce.INTERNAL_Announce('Warning', msg, QtWidgets.QMessageBox.Icon.Warning)

            def Information(msg:str):
                StandardDialog.Message.Announce.INTERNAL_Announce('Info', msg, QtWidgets.QMessageBox.Icon.Question)

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

        # ? Save reference to root layout.
        self.rootLayout = rootLayout
        
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