
# External Libraries
import PyQt6.QtWidgets as QtWidgets

# Internal Libraries
import automatey.GUI.GUtils as GUtils

class GLayouts:

    class GGridLayout(QtWidgets.QGridLayout):
        '''
        A grid (e.g., 2x2) layout. 
        '''
        
        def __init__(self):
            super().__init__()

class GApplication(QtWidgets.QApplication):
    '''
    Only one instance of 'Application' is required.
    
    Note:
    - An 'Application' instance must be the first construction, before any element.
    '''
    
    qStyle = None
    
    def __init__(self):
        super().__init__([])
        
        # PyQt6: A lot of library call(s) depend on the 'QStyle' instance of the 'QApplication'.
        GApplication.qStyle = self.style()
        
    def GRun(self):
        '''
        Runs the GUI event-loop.
        '''
        self.exec()

class GWindow(QtWidgets.QMainWindow):
    '''
    Multiple window(s) may be created.
    '''
    
    def __init__(self, title:str, icon:GUtils.GIcon, minimumSize, rootLayout):
        super().__init__()
        
        # ? Setting root layout.
        # PyQt: A layout must be attached to a 'QWidget' instance.
        self.rootWidget = QtWidgets.QWidget()
        self.rootWidget.setLayout(rootLayout)
        self.setCentralWidget(self.rootWidget)
        
        # ? All other settings.
        self.setMinimumSize(minimumSize[0], minimumSize[1])
        self.setWindowTitle(title)
        self.setWindowIcon(icon.qIcon)
    
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