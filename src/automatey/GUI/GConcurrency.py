
# External Libraries
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui
import PyQt6.QtCore as QtCore

class GThread(QtCore.QThread):
    '''
    A thread, with two handler(s):
    - Main handler, that is called once only, when thread is ran.
        - Note that, it receives this (thread) instance as argument.
    - Notify handler, that is called from the GUI thread, with every `GNotify` call from this thread's context.
        - Note that, it receives a `dict` as argument.
    '''
    
    notifySignal = QtCore.pyqtSignal(dict)
    
    def __init__(self, mainFcn, notifyFcn):
        QtCore.QThread.__init__(self)
        self.mainFcn = mainFcn
        self.notifySignal.connect(notifyFcn)
    
    def GRun(self):
        '''
        Run thread.
        '''
        self.start()
    
    def GNotify(self, data:dict):
        '''
        Notify (with data).
        '''
        self.notifySignal.emit(data)

    @QtCore.pyqtSlot()
    def run(self):
        self.mainFcn(self)

class GQueue:
    '''
    A thread-safe queue.
    '''
    
    def __init__(self):
        self.queue = []
        self.mutex = QtCore.QMutex()
        self.condition = QtCore.QWaitCondition()
    
    def GEnqueue(self, data):
        '''
        Enqueue data.
        '''
        self.mutex.lock()
        self.queue.append(data)
        self.condition.wakeOne()
        self.mutex.unlock()

    def GDequeue(self):
        '''
        Dequeue data.
        '''
        self.mutex.lock()
        while len(self.queue) == 0:
            self.condition.wait(self.mutex)
        data = self.queue.pop(0)
        self.mutex.unlock()
        return data
    
    def GTryDequeue(self):
        '''
        Dequeue data, if data is available.
        '''
        self.mutex.lock()
        data = None
        if len(self.queue) > 0:
            data = self.queue.pop(0)
        self.mutex.unlock()
        return data