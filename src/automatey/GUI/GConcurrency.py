
# External Libraries
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui
import PyQt6.QtCore as QtCore
import automatey.GUI.Wrappers.PyQt6 as PyQt6Wrapper

# Internal Libraries
import automatey.Base.TimeUtils as TimeUtils

class Thread:
    '''
    A thread, with two handler(s):
    - Main handler, that is called once only, when thread is ran.
        - Note that, it receives this (thread) instance as argument.
    - Notify handler, that is called from the GUI thread, with every `GNotify` call from this thread's context.
        - Note that, it receives a `dict` as argument.
    '''
    
    def __init__(self, mainFcn, notifyFcn):
        
        self.qThread = PyQt6Wrapper.QThread(mainFcn, notifyFcn)
        
    def run(self):
        '''
        Run thread.
        '''
        self.qThread.start()
    
    def notify(self, data:dict):
        '''
        Notify (with data).
        '''
        self.qThread.WNotify(data)

class Queue:
    '''
    A thread-safe queue.
    '''
    
    def __init__(self):
        self.queue = []
        self.mutex = QtCore.QMutex()
        self.condition = QtCore.QWaitCondition()
    
    def enqueue(self, data):
        '''
        Enqueue data.
        '''
        self.mutex.lock()
        self.queue.append(data)
        self.condition.wakeOne()
        self.mutex.unlock()

    def dequeue(self):
        '''
        Dequeue data.
        '''
        self.mutex.lock()
        while len(self.queue) == 0:
            self.condition.wait(self.mutex)
        data = self.queue.pop(0)
        self.mutex.unlock()
        return data
    
    def tryDequeue(self):
        '''
        Dequeue data, if data is available.
        '''
        self.mutex.lock()
        data = None
        if len(self.queue) > 0:
            data = self.queue.pop(0)
        self.mutex.unlock()
        return data

class Timer:
    
    '''
    Timer, that keeps executing a runnable, as long as it returns `0`.
    '''
    
    def __init__(self, fcn, period:TimeUtils.Time):
        
        self.qTimer = QtCore.QTimer()
        
        self.qTimer.timeout.connect(self.INTERNAL_runnable)
        
        self.fcn = fcn
        self.qTimer.start(int(period.toMilliseconds()))
    
    def INTERNAL_runnable(self):
        if self.fcn() != 0:
            self.qTimer.stop()
