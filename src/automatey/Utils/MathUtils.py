
import copy
import bisect
import collections

def correlate(x, p1, p2):
    '''
    Given two points, use `y = mx + c` to get `y` for `x`.
    '''
    m = (p2[1] - p1[1]) / (p2[0] - p1[0])
    c = p1[1] - (m * p1[0])
    return (m * x) + c    

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

def findNearestValues(value, orderedValues):
    '''
    Returns a tuple `(x, y)`, where,
    - `x` is the smallest value from `orderedValues`, larger than `value`.
    - `y` is the largest value from `orderedValues`, smaller than `value`.
    
    If, for example, `value` is larger than all value(s) in `orderedValues`, `None` is returned.
    '''
    x = None
    y = None

    insertIdx = bisect.bisect_left(orderedValues, value)
    if insertIdx > 0:
        x = orderedValues[insertIdx - 1]

    insertIdx = bisect.bisect_right(orderedValues, value)
    if insertIdx < len(orderedValues):
        y = orderedValues[insertIdx]
        
    return (x, y)

class MediaSpecific:

    @staticmethod
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

    class BoundingBox:

        @staticmethod
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

class CollectionSpecific:
    
    def countOccurrences(iterable, key=None):
        '''
        Given an iterable, returns a dictionary, with,
        - each key mapping to an item, and,
        - each value mapping to the number of occurrences of that item.
        
        Note that,
        - If key is not `None`, iterable is first transformed into a list of `key(item) for item in iterable`. 
        '''
        if key is not None:
            iterable = [key(item) for item in iterable]
        return dict(collections.Counter(iterable))
