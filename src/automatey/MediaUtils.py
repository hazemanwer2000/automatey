
from automatey.FileManagement import File

class Image:
    '''
    Representation of an image file.
    '''
    def __init__(self, f:File):
        pass
    
    class Utils:
        
        SupportedExtensions = ['jpeg', 'jpg', 'png']
        
        def isImage(f:File):
            return f.getExtension() in Image.Utils.SupportedExtensions