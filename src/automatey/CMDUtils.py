
import pprint

def printf(anything, width=80):
    '''
    Replaces Python default 'print' API.
    '''
    pprint.pprint(anything)