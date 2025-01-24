
import automatey.OS.FileUtils as FileUtils

import hashlib

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

class Hash:
    
    class Algorithms:
        
        SHA1 = 0
        SHA256 = 1
        SHA512 = 2
    
    INTERNAL_Algorithm2HashObject = {
        Algorithms.SHA1: hashlib.sha1,
        Algorithms.SHA256: hashlib.sha256,
        Algorithms.SHA512: hashlib.sha512,
    }
    
    @staticmethod
    def generate(feed:Feed, algorithm=Algorithms.SHA256) -> bytes:
        '''
        Generate a hash, based on a feed.
        '''
        hashObject = Hash.INTERNAL_Algorithm2HashObject[algorithm]()
        while (feedBytes := feed.feed()):
            hashObject.update(feedBytes)
        return bytes.fromhex(hashObject.hexdigest())
