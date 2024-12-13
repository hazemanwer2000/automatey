
# External Libraries
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui
import PyQt6.QtCore as QtCore
import vlc

# Internal Libraries
import automatey.GUI.GUtils as GUtils
import automatey.GUI.GConcurrency as GConcurrency
import automatey.Base.ColorUtils as ColorUtils
import automatey.Abstract.Graphics as Graphics
import automatey.Media.ImageUtils as ImageUtils
import automatey.Base.TimeUtils as TimeUtils
import automatey.OS.FileUtils as FileUtils
import automatey.Utils.MathUtils as MathUtils

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
        def __init__(self, elements, initElement):
            super().__init__()
            
            for element in elements:
                self.addWidget(element)
            
            self.setCurrentWidget(initElement)
                
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

    class GOutline(QtWidgets.QFrame):
        '''
        Adds an outline around the specified element.
        '''
        
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
            else:
                super().mousePressEvent(event)

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
            
            # PyQt6: Force 'QButton' not to be focusable.
            self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
            
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

    class GSlider(QtWidgets.QSlider, INTERNAL.GEventManager):
        '''
        A slider (deals only with integer value(s)).
        '''
        
        def __init__(self, valueRange, initValue, isHorizontal=True):
            QtWidgets.QSlider.__init__(self)
            INTERNAL.GEventManager.__init__(self)
            
            # ? Set orientation.
            orientation = QtCore.Qt.Orientation.Horizontal if isHorizontal else QtCore.Qt.Orientation.Vertical
            self.setOrientation(orientation)
            
            # PyQt6: Fix tick-interval at '1'.
            self.setTickInterval(1) 
            
            # ? Set value-range, and init-value.
            self.setRange(valueRange[0], valueRange[1])
            self.setValue(initValue)
            
        def INTERNAL_mouseEvent(self, event):
            # ? Update value.
            ratio = event.position().x() / self.width()
            value = MathUtils.mapValue(ratio, [0.0, 1.0], [self.minimum(), self.maximum()])
            value = MathUtils.clampValue(value, self.minimum(), self.maximum())
            self.setValue(int(value))
            
            # ? Call event-handler, if present.
            if GUtils.GEventHandlers.GSelectionChangeEventHandler in self.eventHandlers:
                self.eventHandlers[GUtils.GEventHandlers.GSelectionChangeEventHandler].fcn()
                
            event.accept()
            
        def mousePressEvent(self, event):
            self.INTERNAL_mouseEvent(event)
        
        def mouseMoveEvent(self, event):
            self.INTERNAL_mouseEvent(event)
            
        def GSetValue(self, value):
            '''
            Set value.
            '''
            self.setValue(value)

        def GGetValue(self):
            '''
            Get value.
            '''
            return self.value()

    class GVideoPlayer(QtWidgets.QWidget):
        
        def __init__(self, f_video:FileUtils.File):
            QtWidgets.QWidget.__init__(self)
            
            # ? Configruing root-layout.
            layout = QtWidgets.QGridLayout()
            layout.setRowStretch(0, 1)
            layout.setRowStretch(1, 0)
            layout.setRowMinimumHeight(1, 0)
            layout.setColumnStretch(0, 1)
            layout.setContentsMargins(5, 5, 5, 5)
            layout.setSpacing(5)
            self.setLayout(layout)
            
            # ? Setting-up video-renderer.
            self.renderer = GWidgets.GVideoRenderer()
            self.renderer.GLoad(f_video)
            layout.addWidget(self.renderer, 0, 0, 1, 1)
            
            # ? Setting-up control-layout (i.e., layout for control-panel).
            
            self.controlGridLayout = GLayouts.GGridLayout(1, 6, Graphics.SymmetricMargin(0), elementSpacing=5)
            layout.addWidget(self.controlGridLayout, 1, 0, 1, 1)
            for i in range(6):
                if i not in [4]:
                    self.controlGridLayout.GSetColumnMinimumSize(i, 0)
            
            # ? Setting-up play-pause button.
            
            self.playButton = GWidgets.GButton(icon=GUtils.GIcon.GCreateFromLibrary(GUtils.GIcon.GStandardIcon.MediaPlay),
                                               toolTip='Play')
            self.playButton.GSetEventHandler(GUtils.GEventHandlers.GClickEventHandler(self.INTERNAL_play))
            
            self.pauseButton = GWidgets.GButton(icon=GUtils.GIcon.GCreateFromLibrary(GUtils.GIcon.GStandardIcon.MediaPause),
                                               toolTip='Pause')
            self.pauseButton.GSetEventHandler(GUtils.GEventHandlers.GClickEventHandler(self.INTERNAL_pause))
            
            self.playPauseStackedLayout = GLayouts.GStackedLayout([self.playButton, self.pauseButton], self.pauseButton)
            self.playPauseStackedLayout.GSetCurrentElement(self.pauseButton)
            
            self.controlGridLayout.GSetElement(self.playPauseStackedLayout, 0, 0, 1, 1)
            
            # ? Setting-up stop button.

            self.stopButton = GWidgets.GButton(icon=GUtils.GIcon.GCreateFromLibrary(GUtils.GIcon.GStandardIcon.MediaStop),
                                               toolTip='Stop')
            self.stopButton.GSetEventHandler(GUtils.GEventHandlers.GClickEventHandler(self.INTERNAL_stop))
            
            self.controlGridLayout.GSetElement(self.stopButton, 0, 1, 1, 1)

            # ? Setting-up seek-forward/backward button(s).

            self.seekBackwardButton = GWidgets.GButton(icon=GUtils.GIcon.GCreateFromLibrary(GUtils.GIcon.GStandardIcon.MediaSeekBackward),
                                               toolTip='Seek Backward')
            self.seekBackwardButton.GSetEventHandler(GUtils.GEventHandlers.GClickEventHandler(lambda: self.INTERNAL_skipBackward(TimeUtils.Time.createFromSeconds(3.0))))
            
            self.controlGridLayout.GSetElement(self.seekBackwardButton, 0, 2, 1, 1)

            self.seekForwardButton = GWidgets.GButton(icon=GUtils.GIcon.GCreateFromLibrary(GUtils.GIcon.GStandardIcon.MediaSeekForward),
                                               toolTip='Seek Forward')
            self.seekForwardButton.GSetEventHandler(GUtils.GEventHandlers.GClickEventHandler(lambda: self.INTERNAL_skipForward(TimeUtils.Time.createFromSeconds(3.0))))
            
            self.controlGridLayout.GSetElement(self.seekForwardButton, 0, 3, 1, 1)

            # ? Setting-up seeker (i.e., slider).
            
            # ? ? Maximum has to be reduced by a few milli-seconds, to avoid invalid seek-time value(s).
            self.seekerMaxValue = 10000000
            self.seeker = GWidgets.GSlider(valueRange=[0, self.seekerMaxValue],
                                           initValue=0,
                                           isHorizontal=True)
            self.seeker.GSetEventHandler(GUtils.GEventHandlers.GSelectionChangeEventHandler(self.INTERNAL_EventHandler_seekerValueChanged))
            
            self.controlGridLayout.GSetElement(self.seeker, 0, 4, 1, 1)
            
            self.seekerUpdateTimer = GConcurrency.GTimer(self.INTERNAL_EventHandler_seekerValueUpdate,
                                                         TimeUtils.Time.createFromMilliseconds(1))
            
            # ? ? Offset video-length by a few milli-second(s).
            self.videoLengthOffset = TimeUtils

            # ? Setting-up (un-)mute button.

            self.unmuteButton = GWidgets.GButton(icon=GUtils.GIcon.GCreateFromLibrary(GUtils.GIcon.GStandardIcon.MediaVolume),
                                               toolTip='(Un-)mute')
            self.unmuteButton.GSetEventHandler(GUtils.GEventHandlers.GClickEventHandler(self.INTERNAL_toggleMute))
            
            self.muteButton = GWidgets.GButton(icon=GUtils.GIcon.GCreateFromLibrary(GUtils.GIcon.GStandardIcon.MediaVolumeMute),
                                               toolTip='(Un-)mute')
            self.muteButton.GSetEventHandler(GUtils.GEventHandlers.GClickEventHandler(self.INTERNAL_toggleMute))
            
            self.muteStackedLayout = GLayouts.GStackedLayout([self.muteButton, self.unmuteButton], self.unmuteButton)
            self.muteStackedLayout.GSetCurrentElement(self.unmuteButton)
            
            self.controlGridLayout.GSetElement(self.muteStackedLayout, 0, 5, 1, 1)
        
        KeyHandlers = {
            # Seek forward/backward
            QtCore.Qt.Key.Key_Comma:
                (lambda self: GWidgets.GVideoPlayer.INTERNAL_skipBackward(self, TimeUtils.Time.createFromSeconds(10.0))),
            QtCore.Qt.Key.Key_Period:
                (lambda self: GWidgets.GVideoPlayer.INTERNAL_skipForward(self, TimeUtils.Time.createFromSeconds(10.0))),
            QtCore.Qt.Key.Key_Left:
                (lambda self: GWidgets.GVideoPlayer.INTERNAL_skipBackward(self, TimeUtils.Time.createFromSeconds(3.0))),
            QtCore.Qt.Key.Key_Right:
                (lambda self: GWidgets.GVideoPlayer.INTERNAL_skipForward(self, TimeUtils.Time.createFromSeconds(3.0))),
            QtCore.Qt.Key.Key_Semicolon:
                (lambda self: GWidgets.GVideoPlayer.INTERNAL_skipBackward(self, TimeUtils.Time.createFromSeconds(1.0))),
            QtCore.Qt.Key.Key_Apostrophe:
                (lambda self: GWidgets.GVideoPlayer.INTERNAL_skipForward(self, TimeUtils.Time.createFromSeconds(1.0))),
            
            # Volume up/down/mute
            QtCore.Qt.Key.Key_Up:
                (lambda self: GWidgets.GVideoPlayer.INTERNAL_adjustVolume(self, 10)),
            QtCore.Qt.Key.Key_Down:
                (lambda self: GWidgets.GVideoPlayer.INTERNAL_adjustVolume(self, -10)),
            QtCore.Qt.Key.Key_M:
                (lambda self: GWidgets.GVideoPlayer.INTERNAL_toggleMute(self)),

            # Play/Pause
            QtCore.Qt.Key.Key_Space:
                (lambda self: GWidgets.GVideoPlayer.INTERNAL_togglePlay(self)),
        }

        def enterEvent(self, event):
            # PyQt6: Capture focus whenever 'EnterEvent' occurs.
            self.setFocus()
            event.accept()
        
        def keyPressEvent(self, event):
            key = event.key()
            if key in GWidgets.GVideoPlayer.KeyHandlers:
                GWidgets.GVideoPlayer.KeyHandlers[key](self)
                event.accept()
            else:
                super().keyPressEvent(event)                
        
        def INTERNAL_EventHandler_seekerValueUpdate(self):
            ratio = int(self.renderer.GGetPosition()) / int( self.renderer.GGetLength())
            value = int(ratio * self.seekerMaxValue)
            self.seeker.GSetValue(value)
            return 0
        
        def INTERNAL_EventHandler_seekerValueChanged(self):
            ratio = self.seeker.GGetValue() / self.seekerMaxValue
            videoLengthInMS = int(self.renderer.GGetLength().toMilliseconds())
            
            seekTimeInMS = MathUtils.mapValue(ratio, [0.0, 1.0], [0, videoLengthInMS])
            self.renderer.GSeekPosition(TimeUtils.Time.createFromMilliseconds(seekTimeInMS))
        
        def INTERNAL_skipForward(self, skipTime:TimeUtils.Time):
            self.renderer.GSkipForward(skipTime)

        def INTERNAL_skipBackward(self, skipTime:TimeUtils.Time):
            self.renderer.GSkipBackward(skipTime)
            
        def INTERNAL_play(self):
            self.renderer.GPlay()
            self.playPauseStackedLayout.GSetCurrentElement(self.pauseButton)

        def INTERNAL_pause(self):
            self.renderer.GPause()
            self.playPauseStackedLayout.GSetCurrentElement(self.playButton)

        def INTERNAL_togglePlay(self):
            if self.renderer.GIsPlaying():
                self.INTERNAL_pause()
            else:
                self.INTERNAL_play()
        
        def INTERNAL_stop(self):
            self.renderer.GStop()
            self.playPauseStackedLayout.GSetCurrentElement(self.pauseButton)
        
        def INTERNAL_adjustVolume(self, delta:int):
            self.renderer.GAdjustVolume(delta)

        def INTERNAL_toggleMute(self):
            if self.renderer.GIsMute():
                self.renderer.GUnmute()
                self.muteStackedLayout.GSetCurrentElement(self.unmuteButton)
            else:
                self.renderer.GMute()
                self.muteStackedLayout.GSetCurrentElement(self.muteButton)

        def GRenderer(self):
            '''
            Get underlying `GVideoRenderer`.
            '''
            return self.renderer

    class GVideoRenderer(QtWidgets.QFrame):
        
        def __init__(self):
            QtWidgets.QFrame.__init__(self)
            
            # ? Setting up VLC media-player.
            self.VLCInstance = vlc.Instance()
            self.player = self.VLCInstance.media_player_new()
            # Warning: OS-specific (Windows-OS)
            self.player.set_hwnd(self.winId())
            
            # ? Initial setting(s).
            self.isMute = False
            self.volume = 100
            self.player.audio_set_volume(self.volume)
            
            # ? For robustness, offsetting video-length by a few milli-seconds.
            self.seekEndOffset = TimeUtils.Time.createFromMilliseconds(500)
            # ? To support video-on-repeat, timer will be triggered every 1-ms.
            self.timer = GConcurrency.GTimer(self.INTERNAL_EventHandler_1ms,
                                             TimeUtils.Time.createFromMilliseconds(1))
        
        def INTERNAL_EventHandler_1ms(self):
            
            # ? If position exceeds length (which is offset), seek '0'.
            position = self.GGetPosition()
            if (position > self.GGetLength()):
                position = TimeUtils.Time(0)
                self.player.set_time(int(position.toMilliseconds()))
            
            return 0
        
        def GLoad(self, f:FileUtils.File):
            media = self.VLCInstance.media_new(str(f))
            self.player.set_media(media)
            self.player.play()
        
        def GPlay(self):
            if not self.player.is_playing():
                self.player.play()

        def GPause(self):
            if self.player.is_playing():
                self.player.pause()
    
        def GIsPlaying(self):
            return self.player.is_playing()
        
        def GStop(self):
            self.GPlay()
            self.player.set_time(0)
        
        def GGetLength(self) -> TimeUtils.Time:
            return TimeUtils.Time.createFromMilliseconds(self.player.get_length()) - self.seekEndOffset
        
        def GGetPosition(self) -> TimeUtils.Time:
            return TimeUtils.Time.createFromMilliseconds(self.player.get_time())
        
        def GSeekPosition(self, position:TimeUtils.Time):
            if (position > self.GGetLength()):
                position = TimeUtils.Time(0)
            self.player.set_time(int(position.toMilliseconds()))
        
        def GSkipForward(self, skipTime:TimeUtils.Time):
            newPosition = self.GGetPosition() + skipTime
            self.GSeekPosition(newPosition)

        def GSkipBackward(self, skipTime:TimeUtils.Time):
            newPosition = self.GGetPosition() - skipTime
            self.GSeekPosition(newPosition)

        def GAdjustVolume(self, delta:int):
            self.GSetVolume(self.volume + delta)
        
        def GSetVolume(self, value:int):
            self.volume = value
            self.volume = min(100, max(0, self.volume))
            if not self.isMute:
                self.player.audio_set_volume(self.volume)
        
        def GMute(self):
            self.isMute = True
            self.player.audio_set_volume(0)

        def GUnmute(self):
            self.isMute = False
            self.player.audio_set_volume(self.volume)

        def GIsMute(self):
            return self.isMute

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
    
    def GSetTitle(self, title):
        '''
        Set title of window.
        '''
        self.setWindowTitle(title)

    def GCreateToolbar(self, contract):
        '''
        Creates a Tool-bar based on a contract.
        
        Contract shall consist of a list of dictionaries, with optional `None` value(s) in-between, intepretted as separators.
        
        Each dictionary, representing a button, shall specify,
        - `icon`.
        - `tool-tip`.
        - `handler`.
        - `is-checkable`, specifying whether button is checkable.
            - Note, if `is-checkable`, `handler` receives a single `bool` argument.
        '''
        
        toolbar = QtWidgets.QToolBar()
        toolbar.setMovable(False)
        toolbar.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.PreventContextMenu)
        
        for term in contract:
            if term == None:
                toolbar.addSeparator()
            else:
                action = QtGui.QAction(
                    term['icon'].qIcon,
                    term['tool-tip'],
                    self
                )
                action.triggered.connect(term['handler'])
                action.setCheckable(term['is-checkable'])
                toolbar.addAction(action)
        
        self.addToolBar(toolbar)
  
    def GCreateMenu(self, menuName:str, contract):
        '''
        Creates a (sub-)menu based on a contract.
        
        Contract shall consist of a list of dictionaries, with optional `None` value(s) in-between, intepretted as separators.
        
        Each dictionary, representing a button, shall specify,
        - `text`.
        - `handler`.
        - `is-checkable`, specifying whether button is checkable.
            - Note, if `is-checkable`, `handler` receives a single `bool` argument.
        '''
        
        menu = self.menuBar()
        subMenu = menu.addMenu('&' + menuName)
        
        for term in contract:
            if term == None:
                subMenu.addSeparator()
            else:
                action = QtGui.QAction(
                    term['text'],
                    self
                )
                action.triggered.connect(term['handler'])
                action.setCheckable(term['is-checkable'])
                subMenu.addAction(action)

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