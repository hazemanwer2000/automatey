
import automatey.Base.ExceptionUtils as ExceptionUtils

def asFloat(value) -> float:
    try:
        result = float(value)
    except:
        raise ExceptionUtils.ValidationError('Failed to convert to float.')
    return result

def asInt(value) -> int:
    try:
        result = int(value)
    except:
        raise ExceptionUtils.ValidationError('Failed to convert to integer.')
    return result

def asBool(value) -> bool:
    '''
    Note,
    - Succeeds only if value is a `true`, or `false` `str` (case irrelevant), `int`, or `bool`. 
    '''
    result = None
    typeOfValue = type(value)

    if typeOfValue == bool:
        result = value
    elif typeOfValue == int:
        result = bool(value)
    elif typeOfValue == str:
        value = value.lower()
        if value == 'true':
            result = True
        elif value == 'false':
            result = False
    
    if result is None:
        raise ExceptionUtils.ValidationError('Failed to convert to boolean.')
    
    return result
