
import numpy as np

def mapValues(values, fromRange, toRange):
    '''
    Map value(s), from one range to another.
    '''
    return np.interp(values, fromRange, toRange)