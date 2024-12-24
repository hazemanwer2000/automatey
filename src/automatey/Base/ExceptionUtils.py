
class Error(Exception):
    '''
    (Abstract) Base-class for all exception(s).
    '''
    pass

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

class ImplementationError(Error):
    '''
    To be raised when the implementation is itself faulty.
    '''
    pass
