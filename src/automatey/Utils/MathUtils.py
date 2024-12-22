
import copy

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

def isWithinFrame(size, referenceSize, referencePosition):
    '''
    Given a reference size and position, and (frame-)size, check if the position lies within.
    
    Returns position (i.e., within frame), or `None`.
    
    Note that,
    - All value(s) shall be `int`.
    - It is assumed that frame is
        - centered, and,
        - scaled to fit.
    '''
    # ? (Width-to-Height) Factor(s).
    referenceFactor = referenceSize[0] / referenceSize[1]
    factor = size[0] / size[1]
    
    # ? Calculate actual reference size and position.
    referenceActualSize = copy.deepcopy(referenceSize)
    referenceActualPosition = copy.deepcopy(referencePosition)
    # ? ? Case: Reference(-frame) is wider than frame.
    if referenceFactor > factor:
        stretchFactor = (referenceFactor / factor)
        referenceActualSize[0] = int(referenceActualSize[0] / stretchFactor)
        referencePositionOffset = (referenceSize[0] - referenceActualSize[0]) // 2
        referenceActualPosition[0] -= referencePositionOffset
    else:
        stretchFactor = (factor / referenceFactor)
        referenceActualSize[1] = int(referenceActualSize[1] / stretchFactor)
        referencePositionOffset = (referenceSize[1] - referenceActualSize[1]) // 2
        referenceActualPosition[1] -= referencePositionOffset
    
    # ? Calculate position.
    xFactor = referenceActualPosition[0] / referenceActualSize[0]
    yFactor = referenceActualPosition[1] / referenceActualSize[1]
    position = [
        int(xFactor * size[0]),
        int(yFactor * size[1]),
    ]
    
    # ? Check if position lie with-in frame.
    t_isWithin = lambda t_position, t_size: (t_position >= 0) and (t_position <= t_size)
    if not (t_isWithin(position[0], size[0]) and t_isWithin(position[1], size[1])):
        position = None
    
    return position