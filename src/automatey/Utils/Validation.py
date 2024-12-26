
def asFloat(value) -> float:
    try:
        result = float(value)
    except:
        result = None
    return result

def asInt(value) -> int:
    try:
        result = int(value)
    except:
        result = None
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
    return result
