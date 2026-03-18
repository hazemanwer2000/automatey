
import automatey.Utils.ExceptionUtils as ExceptionUtils

import platform

class OSType:

    Linux = 0
    Windows = 1

class INTERNAL:

    System2OSType = {
        'Linux' : OSType.Linux,
        'Windows' : OSType.Windows
    }

def GetOSType():
    '''
    Returns the type of OS, as `OSType.<...>`, whether:
    - `Linux`
    - `Windows`
    '''
    osType = INTERNAL.System2OSType.get(platform.system(), None)
    if osType is None:
        raise ExceptionUtils.ImplementationError("Missing support for the current OS.")
    return osType
