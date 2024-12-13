
def mapValue(value, rangeFrom, rangeTo):
    '''
    Map a (float-)value from one range to another.
    '''
    to_min, to_max = rangeTo
    from_min, from_max = rangeFrom
    return to_min + ((value - from_min) / (from_max - from_min)) * (to_max - to_min)

def clampValue(value, minValue, maxValue):
    '''
    Clamp a (float-)value between a minimum, and a maximum (all-inclusive).
    '''
    return min(maxValue, max(minValue, value))
