
# External Libraries
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui
import PyQt6.QtCore as QtCore

import automatey.Utils.ExceptionUtils as ExceptionUtils
import automatey.Utils.MathUtils as MathUtils

class QThread(QtCore.QThread):
    
    notifySignal = QtCore.pyqtSignal(dict)
    
    def __init__(self, mainFcn, mainFcnArgs, notifyFcn):
        QtCore.QThread.__init__(self)
        self.mainFcn = mainFcn
        self.mainFcnArgs = mainFcnArgs
        self.notifySignal.connect(notifyFcn)

    def WNotify(self, data:dict):
        self.notifySignal.emit(data)

    @QtCore.pyqtSlot()
    def run(self):
        self.mainFcn(*self.mainFcnArgs)

class QSlider(QtWidgets.QSlider):
    
    def __init__(self):
        QtWidgets.QSlider.__init__(self)
        self.mousePressEventFcn = None
        self.mouseMoveEventFcn = None
         
    def mousePressEvent(self, event):
        if self.mousePressEventFcn != None:
            self.mousePressEventFcn(event)
    
    def mouseMoveEvent(self, event):
        if self.mouseMoveEventFcn != None:
            self.mouseMoveEventFcn(event)

class QFrame(QtWidgets.QFrame):
    
    def __init__(self):
        QtWidgets.QFrame.__init__(self)
        self.keyPressEventFcn = None
        self.enterEventFcn = None
        self.contextMenuEventFcn = None
        self.mouseMoveEventFcn = None
        self.wheelEventFcn = None
         
    def enterEvent(self, event):
        if self.enterEventFcn != None:
            self.enterEventFcn(event)

    def keyPressEvent(self, event):
        if self.keyPressEventFcn != None:
            self.keyPressEventFcn(event)
    
    def contextMenuEvent(self, event):
        if self.contextMenuEventFcn != None:
            self.contextMenuEventFcn(event)
            
    def mouseMoveEvent(self, event):
        if self.mouseMoveEventFcn != None:
            self.mouseMoveEventFcn(event)
    
    def wheelEvent(self, event):
        if self.wheelEventFcn != None:
            self.wheelEventFcn(event)

class QLabel(QtWidgets.QLabel):
    
    def __init__(self):
        QtWidgets.QLabel.__init__(self)
        self.contextMenuEventFcn = None
        self.mouseMoveEventFcn = None

    def contextMenuEvent(self, event):
        if self.contextMenuEventFcn != None:
            self.contextMenuEventFcn(event)

    def mouseMoveEvent(self, event):
        if self.mouseMoveEventFcn != None:
            self.mouseMoveEventFcn(event)

class QLineEdit(QtWidgets.QLineEdit):
    
    def __init__(self):
        QtWidgets.QLineEdit.__init__(self)
        self.keyPressEventFcn = None
        
    def keyPressEvent(self, event):
        if self.keyPressEventFcn != None:
            if (self.keyPressEventFcn(event) != 0):
                QtWidgets.QLineEdit.keyPressEvent(self, event)

class QPlainTextEdit(QtWidgets.QPlainTextEdit):
    
    def __init__(self):
        QtWidgets.QPlainTextEdit.__init__(self)
        self.keyPressEventFcn = None
        self.mousePressEventFcn = None
        
    def keyPressEvent(self, event):
        if self.keyPressEventFcn != None:
            if (self.keyPressEventFcn(event) != 0):
                QtWidgets.QPlainTextEdit.keyPressEvent(self, event)

    def mousePressEvent(self, event):
        if self.mousePressEventFcn != None:
            self.mousePressEventFcn(event)

class QListWidget(QtWidgets.QListWidget):

    def __init__(self):
        QtWidgets.QListWidget.__init__(self)
        self.dropEventFcn = None

    def dropEvent(self, event):
        if self.dropEventFcn != None:
            self.dropEventFcn(event)
        QtWidgets.QListWidget.dropEvent(self, event)

class QWidget(QtWidgets.QWidget):
    
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.mousePressEventFcn = None
        
    def mousePressEvent(self, event):
        if self.mousePressEventFcn != None:
            self.mousePressEventFcn(event)

class QFlowLayout(QtWidgets.QLayout):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def count(self):
        return len(self.itemList)

    def addItem(self, item):
        self.itemList.append(item)

    def insertItem(self, item, idx):
        self.itemList.insert(idx, item)

    def insertWidget(self, idx, widget):
        self.insertItem(QtWidgets.QWidgetItem(widget), idx)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]

        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        
        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.__doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.__doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        return QtCore.QSize(0, 0)

    def __doLayout(self, rect, is_no_effect_mode:bool):
        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(left, top, -right, -bottom)

        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0
        spacing = self.spacing()

        for item in self.itemList:
            style = item.widget().style()
            layout_spacing_x = style.layoutSpacing(
                QtWidgets.QSizePolicy.ControlType.PushButton, QtWidgets.QSizePolicy.ControlType.PushButton,
                QtCore.Qt.Orientation.Horizontal
            )
            layout_spacing_y = style.layoutSpacing(
                QtWidgets.QSizePolicy.ControlType.PushButton, QtWidgets.QSizePolicy.ControlType.PushButton,
                QtCore.Qt.Orientation.Vertical
            )
            space_x = spacing + layout_spacing_x
            space_y = spacing + layout_spacing_y
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not is_no_effect_mode:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        total_height = (y + line_height + bottom) - rect.y()
        return total_height

class QStatusBarEventFilter(QtCore.QObject):
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Type.StatusTip:
            return True
        return super().eventFilter(obj, event)

class QStatusBar(QtWidgets.QStatusBar):

    def __init__(self, parent=None):
        super().__init__(parent)

class QApplication(QtWidgets.QApplication):
    
    def __init__(self, argv):
        super().__init__(argv)

        self.INTERNAL_qStatusBarEventFilter = QStatusBarEventFilter()
        self.installEventFilter(self.INTERNAL_qStatusBarEventFilter)

class Custom:

    class QHexViewer(QtWidgets.QAbstractScrollArea):
        '''
        Display byte(s) at specific address(es).
        '''

        SPACES_BEFORE_ADDRESS = 1
        SPACES_AFTER_ADDRESS = 2
        SPACES_BETWEEN_DATA = 1
        SPACES_AFTER_DATA = 4

        HEADER_OFFSET = 0.5
        
        NON_DATA_LINES = 2

        def __init__(self, dataBytes:bytes, startAddress:int, bytesPerLine:int, bytesPerAddress:int, parent=None):
            super().__init__(parent)

            if not MathUtils.isPowerOfTwo(bytesPerLine):
                raise ExceptionUtils.ValidationError("Bytes-Per-Line must be a power of 2.")
            
            if not MathUtils.isPowerOfTwo(bytesPerAddress):
                raise ExceptionUtils.ValidationError("Bytes-Per-Address must be a power of 2.")

            self.dataBytes = dataBytes
            self.bytesPerLine = bytesPerLine
            self.bytesPerAddress = bytesPerAddress
            self.offsetBytesCount = (startAddress % bytesPerLine)
            self.startAddress = startAddress
            self.endAddress = self.startAddress + len(self.dataBytes)
            self.initialAddress = startAddress - self.offsetBytesCount
            self.headerBytes = range(self.bytesPerLine)

            self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
            self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

            self.setFont(QtGui.QFont("Courier New", 10))
            self.lineHeight = self.fontMetrics().height()
            self.characterWidth = self.fontMetrics().horizontalAdvance("0")

            # ? Offset(s).
            self.dataHorizontalOffset = self.characterWidth * (self.SPACES_BEFORE_ADDRESS + (2 * self.bytesPerAddress) + self.SPACES_AFTER_ADDRESS)
            self.addressHorizontalOffset = self.characterWidth * (self.SPACES_BEFORE_ADDRESS)

            self.setFixedWidth(self.INTERNAL_calculateFixedWidth())

        def INTERNAL_calculateFixedWidth(self):

            marginCharacterCount = self.SPACES_BEFORE_ADDRESS + self.SPACES_AFTER_ADDRESS + self.SPACES_BETWEEN_DATA * (self.bytesPerLine - 1) + self.SPACES_AFTER_DATA
            actualCharacterCount = 2 * (self.bytesPerAddress + self.bytesPerLine)

            return self.characterWidth * (marginCharacterCount + actualCharacterCount)

        def INTERNAL_updateScrollbars(self):
            totalLines = (len(self.dataBytes) + self.bytesPerLine - 1) // self.bytesPerLine
            pageLines = (self.viewport().height() // self.lineHeight) - self.NON_DATA_LINES
            self.verticalScrollBar().setRange(0, max(0, totalLines - pageLines))
            self.verticalScrollBar().setPageStep(pageLines)

        def resizeEvent(self, event):
            super().resizeEvent(event)
            self.INTERNAL_updateScrollbars()

        def paintEvent(self, event):
            
            painter = QtGui.QPainter(self.viewport())

            palette = self.palette()
            backgroundColor = palette.color(palette.ColorRole.Base)
            foregroundColor = palette.color(palette.ColorRole.Text)

            defaultFont = self.font()
            boldFont = self.font()
            boldFont.setBold(True)

            scrollbar = self.verticalScrollBar()

            firstLine = scrollbar.value()
            pageLines = (self.viewport().height() // self.lineHeight) - self.NON_DATA_LINES
            totalLines = (len(self.dataBytes) + self.bytesPerLine - 1) // self.bytesPerLine
            lastLine = min(firstLine + pageLines, totalLines)

            # ? Paint.

            painter.fillRect(event.rect(), backgroundColor)

            painter.setPen(foregroundColor)

            # ? ? Paint header.

            painter.setFont(boldFont)

            horizontalOffset = self.dataHorizontalOffset
            for headerByte in self.headerBytes:
                painter.drawText(horizontalOffset, self.lineHeight, f"{headerByte:02X}")
                horizontalOffset += self.characterWidth * (self.SPACES_BETWEEN_DATA + 2)

            # ? ? Paint lines.

            y = int(self.lineHeight * (1 + self.HEADER_OFFSET))

            for line in range(firstLine, lastLine):

                # ? Paint address.

                lineAddress = self.initialAddress + (line * self.bytesPerLine)
                textLineAddress = f"{lineAddress:0{self.bytesPerAddress * 2}X}"

                painter.setFont(boldFont)
                painter.drawText(self.addressHorizontalOffset, y + self.lineHeight, textLineAddress)

                # ? Paint data.

                painter.setFont(defaultFont)

                horizontalOffset = self.dataHorizontalOffset

                for i in range(self.bytesPerLine):

                    byteAddress = lineAddress + i

                    if (byteAddress < self.endAddress):

                        dataByte = self.dataBytes[byteAddress - self.initialAddress]

                        painter.drawText(horizontalOffset, y + self.lineHeight, f"{dataByte:02X}")
                    
                    horizontalOffset += self.characterWidth * (self.SPACES_BETWEEN_DATA + 2)

                y += self.lineHeight
