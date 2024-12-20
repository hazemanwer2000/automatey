
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

def keepAspectRatio(size, referenceSize):
    '''
    Given a reference size, modify the size to keep the aspect ratio.
    
    Note,
    - All value(s) shall be `int`.
    - The dimension to be modified shall be `-1`.
    '''
    referenceFactor = referenceSize[0] / referenceSize[1]
    if size[0] == -1:
        size[0] = int(size[1] * referenceFactor)
    elif size[1] == -1:
        size[1] = int(size[0] / referenceFactor)