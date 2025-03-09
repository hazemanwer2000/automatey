
# Standard libraries
import string
import random
import os

class Generation:
    
    @staticmethod
    def String(n:int, charPool=None) -> str:
        '''
        Randomize string.
        
        By default, character-pool is lower- and upper- case ASCII letter(s) and digit(s).
        '''
        if charPool == None:
            charPool = string.ascii_letters + string.digits
        randomString = ''.join(random.choices(charPool, k=n))
        return randomString
    
    @staticmethod
    def Integer(start:int, end:int) -> int:
        '''
        Randomize integer, all-inclusive.
        '''
        return random.randint(start, end)
    
    @staticmethod
    def Float(start:float, end:float) -> float:
        '''
        Randomize float, all-inclusive.
        '''
        return random.uniform(start, end)
    
    @staticmethod
    def Bytes(N:int) -> bytes:
        '''
        Returns a random number of bytes.
        '''
        return os.urandom(N)
    
class Selection:

    @staticmethod
    def selectNUnique(iteratorLength:int, n:int):
        '''
        Selects random and unique index(es) into an iterator.
        
        Returns a list of unique index(es).
        '''
        selectedIndexes = list()
        selectionPool = list(range(iteratorLength))
        while len(selectedIndexes) < n:
            newSelectionPoolIndex = Generation.Integer(0, len(selectionPool)-1)
            newIndex = selectionPool[newSelectionPoolIndex]
            del selectionPool[newSelectionPoolIndex]
            selectedIndexes.append(newIndex)
        return selectedIndexes

    @staticmethod
    def selectNRepeat(iteratorLength:int, n:int):
        '''
        Selects random and unique index(es) into an iterator.
        
        Returns a list of unique index(es).
        '''
        selectedIndexes = list()
        while len(selectedIndexes) < n:
            newIndex = Generation.Integer(0, iteratorLength-1)
            selectedIndexes.append(newIndex)
        return selectedIndexes