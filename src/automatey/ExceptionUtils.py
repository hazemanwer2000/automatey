
import traceback

class Error(Exception):
    '''
    (Abstract) Base-class for all exception(s).
    '''
    def getStackTrace(self):
        return traceback.format_exc()

class BackendError(Error):
    '''
    To be raised when a backend fails.
    '''
    pass

class ValidationError(Error):
    '''
    To be raised in complex validation failure(s).
    '''
    pass
