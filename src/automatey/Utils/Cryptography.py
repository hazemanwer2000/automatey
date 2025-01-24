
import automatey.OS.FileUtils as FileUtils

class Feed:
    '''
    A feed encapsulates bytes, behind a `feed` call.
    
    Note that,
    - `feed` MUST be called, until it returns `None`.
    '''
    
    def __init__(self, bytesPerRead=1024):
        self.bytesPerRead = bytesPerRead
        
    def feed(self):
        '''
        (Interface) Returns `None` if feed is empty.
        '''
        pass

class Feeds:
    
    class FileFeed(Feed):
        '''
        Encapsulates bytes of a file.
        '''
        
        def __init__(self, f:FileUtils.File, bytesPerRead=1024):
            super().__init__(bytesPerRead=bytesPerRead)
            self.f = f
            self.f.openFile('rb')
        
        def feed(self):
            '''
            Returns `None` if feed is empty.
            '''
            readBytes = self.f.readAny(self.bytesPerRead)
            if len(readBytes) == 0:
                readBytes = None
                self.f.closeFile()
            return readBytes
    
    class BytesFeed(Feed):
        '''
        Encapsulates bytes.
        '''
        def __init__(self, data:bytes, bytesPerRead=1024):
            super().__init__(bytesPerRead=bytesPerRead)
            self.data = data
            self.dataLength = len(self.data)
            self.idx = 0
        
        def feed(self):
            '''
            Returns `None` if feed is empty.
            '''
            readBytes = None
            if self.idx != self.dataLength:
                endIdx = min(self.idx + self.bytesPerRead, self.dataLength)
                readBytes = self.data[self.idx:endIdx]
                self.idx = endIdx
            return readBytes

