
# External Libraries
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui
import PyQt6.QtCore as QtCore

class Utils:
    
    @staticmethod
    def QWidget2QLayout(qWidget):
        qLayout = QtWidgets.QGridLayout()
        qLayout.setSpacing(0)
        qLayout.setContentsMargins(0, 0, 0, 0)
        qLayout.setRowStretch(0, 1)
        qLayout.setColumnStretch(0, 1)
        qLayout.addWidget(qWidget, 0, 0, 1, 1)
        return qLayout

    @staticmethod
    def QLayout2QWidget(qLayout):
        qWidget = QtWidgets.QWidget()
        qWidget.setLayout(qLayout)
        return qWidget

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