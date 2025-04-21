
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
    def Selector(iterator, indices):
        '''
        Given an iterator, and a list of indices, returns a new list (...)
        '''
        return [iterator[idx] for idx in indices]    

    class Indices:

        @staticmethod
        def NUnique(iteratorLength:int, n:int):
            '''
            Selects random and unique indices into an iterator.
            
            Returns a list of unique indices.
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
        def NRepeat(iteratorLength:int, n:int):
            '''
            Generates random and unique indices into an iterator.
            
            Returns a list of unique indices.
            '''
            selectedIndexes = list()
            while len(selectedIndexes) < n:
                newIndex = Generation.Integer(0, iteratorLength-1)
                selectedIndexes.append(newIndex)
            return selectedIndexes