
# External Libraries
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui
import PyQt6.QtCore as QtCore

class Utils:
    
    @staticmethod
    def Element2Layout(element):
        layout = QtWidgets.QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setRowStretch(0, 1)
        layout.setColumnStretch(0, 1)
        layout.addWidget(element, 0, 0, 1, 1)
        return layout

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