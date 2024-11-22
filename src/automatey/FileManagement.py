
import os
import pathlib
import typing
    
class File:
    '''
        Immutable representation of a file/directory.
    '''

    def __init__(self, *paths: str):
        joinedPath = Path.join(*paths)
        self.path = os.path.abspath(joinedPath)
    
    def __str__(self) -> bool:
        return self.path
    
    def __repr__(self) -> bool:
        return self.path

    def isExists(self) -> bool:
        '''
            Check if file/directory exists.
        '''
        return os.path.exists(self.path)
    
    def isDirectory(self) -> bool:
        '''
            Check if it exists, and is a directory.
        '''
        return os.path.isdir(self.path)
    
    def isFile(self) -> bool:
        '''
            Check if it exists, and is a file.
        '''
        return os.path.isfile(self.path)
    
    def listDirectory(self, isRecursive:bool=False, conditional=None) -> typing.List[typing.Self]:
        '''
            For a directory, returns a list of *File* object(s), that represent the directory's listing.
        '''
        conditional = (lambda x: True) if (conditional == None) else conditional
        pathObject = pathlib.Path(self.path)
        iterator = pathObject.rglob("*") if isRecursive else pathObject.iterdir()
        resultList = []
        for element in iterator:
            print(element)
            f = File(str(element))
            if conditional(f):
                resultList.append(f)
        return resultList
    
    def listDirectoryRelatively(self, isRecursive:bool=False, conditional=None) -> typing.List[str]:
        '''
            For a directory, returns a list of string(s), that represent the directory's relative listing.
        '''
        resultList = self.listDirectory(isRecursive=isRecursive, conditional=conditional)
        relativeResultList = []
        selfPathObject = pathlib.Path(self.path)
        for f in resultList:
            pathObject = pathlib.Path(f.path)
            relativePath = pathObject.relative_to(selfPathObject)
            relativeResultList.append(str(relativePath))
        return relativeResultList

    def traverseDirectory(self, *paths):
        '''
            Returns a *File* object, that is a traversal from the current *File* object.
            
            For example, '..' returns the parent directory of this file/directory. 
        '''
        return File(Path.join(self.path, *paths))
    
    def getExtension(self) -> str:
        '''
            Get extension of a file (e.g., 'mp4').
            
            Returns *None*, if there is no extension.        
        '''
        extension = os.path.splitext(self.path)[1]
        extension = None if (extension == '') else extension[1:]
        return extension
    
    def getName(self) -> str:
        '''
            Get name of file/directory. 
        '''
        return os.path.split(self.path)[1]

    def openFile(self, mode:str) -> typing.Self:
        '''
            Opens a file, for read/write operation(s).
        
            Orthogonal mode(s):
                Set #1:
                    'r' - Read
                    'w' - Write
                    'a' - Append
                Set #2:
                    'b' - Binary
                    't' - Text
        '''
        self.handler = open(self.path, mode=mode)
        return self
    
    def readLine(self) -> str:
        '''
            Read a single line, without a new-line character.
        
            Returns *None* if EOF has been reached.
        '''
        line = self.handler.readline()
        line = None if (line == '') else (line[:-1])
        return line        
    
    def readAny(self, count=-1):
        '''
            Read *n* bytes, or character(s).
        '''
        return self.handler.read(count)
    
    def writeLine(self, line:str):
        '''
            Writes a line, appending a new-line character.
        '''
        self.handler.write(line + '\n')
    
    def writeAny(self, writeable):
        '''
            Write byte(s), or character(s).
        '''
        self.handler.write(writeable)
    
    def closeFile(self):
        '''
            Close file.
        '''
        self.handler.close()
        self.handler = None

    def __enter__(self):
        pass
    
    def __exit__(self, cls, obj, traceback):
        self.closeFile()
        return True

    def makeDirectory(self):
        '''
            if directory, and does not exist, creates it.
        '''
        pathObject = pathlib.Path(self.path)
        pathObject.mkdir(exist_ok=True, parents=False)
    
    def makeAncestorDirectories(self):
        '''
            if any ancestor directories, of this *File* object, do not exist, creates them all.
        '''
        parentDirectory = self.traverseDirectory('..')
        pathObject = pathlib.Path(parentDirectory.path)
        pathObject.mkdir(exist_ok=True, parents=True)

    class Path:
        
        @staticmethod
        def join(*args):
            '''
            Concatenates multiple path(s).
            '''
            return os.path.abspath(os.path.join(*args))