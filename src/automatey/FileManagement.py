
import os
import pathlib
import typing

class Path:
    
    @staticmethod
    def join(*args):
        return os.path.join(*args)
    
class File:
    '''
        Immutable.
    '''

    def __init__(self, path: str):
        self.path = os.path.abspath(path)
    
    def __str__(self) -> bool:
        return self.path
    
    def __repr__(self) -> bool:
        return self.path

    def isExists(self) -> bool:
        return os.path.exists(self.path)
    
    def isDirectory(self) -> bool:
        return os.path.isdir(self.path)
    
    def isFile(self) -> bool:
        return os.path.isfile(self.path)
    
    def listDirectory(self, isRecursive:bool=False, conditional=None) -> typing.List[typing.Self]:
        conditional = (lambda x: True) if (conditional == None) else conditional
        pathObject = pathlib.Path(self.path)
        iterator = pathObject.rglob("*") if isRecursive else pathObject.iterdir()
        resultList = []
        for element in iterator:
            f = File(str(element))
            if conditional(f):
                resultList.append(f)
        return resultList

    def traverseDirectory(self, *paths):
        '''
            Returns a *File*, that points to a path, that is a traversal from the current path.
        '''
        return File(Path.join(self.path, *paths))
    
    def getExtension(self) -> str:
        '''
            Returns *None*, if there is no extension.        
        '''
        extension = os.path.splitext(self.path)[1]
        extension = None if (extension == '') else extension[1:]
        return extension
    
    def getName(self) -> str:
        return os.path.split(self.path)[1]

    def openFile(self, mode:str) -> typing.Self:
        '''
            Orthogonal Mode(s):
                Set #1:
                    'r' - Read
                    'w' - Write
                    'a' - Append
                Set #2:
                    'b' - Binary
                    't' - Text
        '''
        encoding = None if ('t' not in mode) else 'utf-8' 
        self.handler = open(self.path, mode=mode, encoding=encoding)
        return self
    
    def readLine(self) -> str:
        '''
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
            Writes a line (i.e., appends '\n').
        '''
        self.handler.write(line + '\n')
    
    def writeAny(self, writeable):
        self.handler.write(writeable)
    
    def closeFile(self):
        self.handler.close()
        self.handler = None

    def __enter__(self):
        pass
    
    def __exit__(self, cls, obj, traceback):
        self.closeFile()
        return True

    def makeDirectory(self):
        pathObject = pathlib.Path(self.path)
        pathObject.mkdir(exist_ok=True, parents=False)