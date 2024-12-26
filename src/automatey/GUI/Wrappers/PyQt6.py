
# External Libraries
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui
import PyQt6.QtCore as QtCore

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
        
    def keyPressEvent(self, event):
        if self.keyPressEventFcn != None:
            if (self.keyPressEventFcn(event) != 0):
                QtWidgets.QPlainTextEdit.keyPressEvent(self, event)

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
        QtWidgets.QPlainTextEdit.__init__(self)
        self.mousePressEventFcn = None
        
    def mousePressEvent(self, event):
        if self.mousePressEventFcn != None:
            self.mousePressEventFcn(event)