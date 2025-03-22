
import collections

class History:
    '''
    Think of the history of webpages, associated with a specific browser tab.
    '''
    
    def __init__(self, capacity:int):
        self.capacity = capacity
        self.deque = collections.deque(maxlen=capacity)
        self.idx = -1
        
    def insert(self, item):
        '''
        Insert a new item, after the current item.
        '''
        # ? Remove left-side of structure (i.e., after index).
        for workingIdx in reversed(range(self.idx + 1, len(self.deque))):
            del self.deque[workingIdx]
        # ? Insert.
        self.deque.append(item)
        self.idx = len(self.deque) - 1
    
    def previous(self):
        '''
        Navigate to previous item.
        
        If current item is the first, `None` is returned and current item becomes void (i.e., a following `insert` clears all previous history).
        '''
        # ? Go to previous item.
        if self.idx >= 0:
            self.idx -= 1
        # ? Fetch previous item.
        item = None
        if self.idx != -1:
            item = self.deque[self.idx]
        return item            
    
    def next(self):
        '''
        Navigate to next item.
        
        If current item is the last, `None` is returned and current item remains the same.
        '''
        item = None
        if (self.idx + 1) < len(self.deque):
            self.idx += 1
            item = self.deque[self.idx]
        return item        
    
    def __len__(self):
        return len(self.deque)
    
    def __str__(self):
        return str(self.deque) + ', idx=' + str(self.idx)
    
    def __repr__(self):
        return str(self)