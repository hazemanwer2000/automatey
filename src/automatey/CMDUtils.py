
import pprint

def printf(anything):
    '''
    Replaces Python default 'print' API.
    '''
    pprint.pprint(anything)