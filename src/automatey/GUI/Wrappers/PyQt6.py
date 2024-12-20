
# External Libraries
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui
import PyQt6.QtCore as QtCore

# Internal Libraries
import automatey.Abstract.Graphics as Graphics

class QThread(QtCore.QThread):
    
    notifySignal = QtCore.pyqtSignal(dict)
    
    def __init__(self, mainFcn, notifyFcn):
        QtCore.QThread.__init__(self)
        self.mainFcn = mainFcn
        self.notifySignal.connect(notifyFcn)

    def WNotify(self, data:dict):
        self.notifySignal.emit(data)

    @QtCore.pyqtSlot()
    def run(self):
        self.mainFcn(self)

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

class QLineEdit(QtWidgets.QLineEdit):
    
    def __init__(self):
        QtWidgets.QLineEdit.__init__(self)
        self.keyPressEventFcn = None
        
    def keyPressEvent(self, event):
        if self.keyPressEventFcn != None:
            if (self.keyPressEventFcn(event) != 0):
                QtWidgets.QLineEdit.keyPressEvent(self, event)
