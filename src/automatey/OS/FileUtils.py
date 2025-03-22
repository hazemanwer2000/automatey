# Standard libraries
import os
import pathlib
import typing
import tempfile
import shutil

# External libraries
from send2trash import send2trash

# Internal libraries
import automatey.Utils.RandomUtils as RandomUtils
import automatey.Utils.ExceptionUtils as ExceptionUtils

class INTERNAL_Constants:
    
    MINIMUM_RANDOM_LENGTH = 7
    MINIMUM_ITERATOR_LENGTH = 6
    
class File:
    '''
    Immutable representation of a file/directory.
    '''

    def __init__(self, *paths: str):
        joinedPath = os.path.join(*paths)
        self.path = os.path.normpath(joinedPath)
    
    def __str__(self):
        return self.path.replace('\\', '/')
    
    def __repr__(self):
        return str(self)

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
    
    def isEmptyDirectory(self) -> bool:
        '''
        Check if directory is empty.
        '''
        return os.path.isdir(self.path) and (len(os.listdir(self.path)) == 0)
    
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
        return File(os.path.join(self.path, *paths))
    
    def getExtension(self) -> str:
        '''
        Get extension of a file (e.g., 'mp4').
        
        Returns *None*, if there is no extension.        
        '''
        extension = os.path.splitext(self.path)[1]
        extension = None if (extension == '') else extension[1:].lower()
        return extension
    
    def getName(self) -> str:
        '''
        Get name of file/directory. 
        '''
        return os.path.split(self.path)[1]
    
    def getNameWithoutExtension(self) -> str:
        '''
        Get name of file/directory, without an extension (if present).
        '''
        pathWithoutExt = os.path.splitext(self.path)[0]
        return os.path.split(pathWithoutExt)[-1]

    def getSize(self) -> int:
        '''
        Get the size, in bytes, of a file or directory.
        
        Note that,
        - Size of a directory is the sum of the size(s) of all file(s) within.
        '''
        size = None
        if self.isDirectory():
            size = sum(f.stat().st_size for f in pathlib.Path(str(self)).glob('**/*') if f.is_file())
        else:
            size = os.path.getsize(str(self))
        return size

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

    def quickRead(self, mode:str):
        '''
        Read all, without having to open and close.
        
        Mode(s):
            'b' - Binary
            't' - Text
        '''
        self.openFile('r' + mode)
        data = self.readAny()
        self.closeFile()
        return data

    def quickWrite(self, data, mode:str):
        '''
        Write all, without having to open and close.
        
        Mode(s):
            'b' - Binary
            't' - Text
        '''
        self.openFile('w' + mode)
        self.writeAny(data)
        self.closeFile()

    def __enter__(self):
        return self
    
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

    class Utils:
        
        @staticmethod
        def getWorkingDirectory() -> "File":
            '''
            Returns the working directory, in *absolute* form.
            '''
            return File(os.getcwd())
        
        @staticmethod
        def getTemporaryDirectory() -> "File":
            '''
            Returns a *File* object, of the temporary directory.
            '''
            baseTmpDir = File(tempfile.gettempdir())
            newTmpDirName = RandomUtils.Generation.String(INTERNAL_Constants.MINIMUM_RANDOM_LENGTH)
            newTmpDir = baseTmpDir.traverseDirectory(newTmpDirName)
            newTmpDir.makeDirectory()
            return newTmpDir

        @staticmethod
        def getTemporaryFile(extension:str, prefix:str='') -> "File":
            '''
            Returns a *File* object, of the temporary directory.
            
            Note that,
            - Extension does not include a `.`.
            '''
            baseTmpDir = File(tempfile.gettempdir())
            newTmpFileName = prefix + RandomUtils.Generation.String(INTERNAL_Constants.MINIMUM_RANDOM_LENGTH) + '.' + extension
            newTmpFile = baseTmpDir.traverseDirectory(newTmpFileName)
            return newTmpFile
        
        @staticmethod
        def copy(srcFile, dstFile):
            '''
            Copy a *File* object, into another.
            '''
            # ? Assert: Destination file does not exist.
            if dstFile.isExists():
                raise ExceptionUtils.ValidationError('Destination file/directory already exists.')
            
            # ? Assert: Source file exists.
            if not srcFile.isExists():
                raise ExceptionUtils.ValidationError('Source file/directory does not exist.')
            
            # ? Copy (...)
            if srcFile.isDirectory():
                shutil.copytree(str(srcFile), str(dstFile))
            else:
                shutil.copy(str(srcFile), str(dstFile))
        
        @staticmethod
        def move(srcFile, dstFile):
            '''
            Move a *File* object, to a different location.
            '''
            # ? Assert: Destination file does not exist.
            if dstFile.isExists():
                raise ExceptionUtils.ValidationError('Destination file/directory already exists.')
            
            # ? Assert: Source file exists.
            if not srcFile.isExists():
                raise ExceptionUtils.ValidationError('Source file/directory does not exist.')
            
            # ? Move (...)
            os.rename(str(srcFile), str(dstFile))

        @staticmethod
        def rename(srcFile, newName):
            '''
            Rename a *File* object, to a new name.
            
            Note,
            - Name should not contain extension.
            '''
            dstFile = File(File.Utils.Path.modifyName(str(srcFile), name=newName))
            File.Utils.move(srcFile, dstFile)

        @staticmethod
        def recycle(f):
            '''
            Move file/directory to 'Recycle Bin' (or, equivalent).
            '''
            if f.isExists():
                # (!) OS-specific (Windows-OS)
                send2trash(str(f).replace('/', '\\'))
        
        @staticmethod
        def replicateDirectoryStructure(srcDir:"File", dstDir:"File"):
            '''
            Creates all the sub-directories, recursive, of a source directory, under the destination directory.
            '''
            dstDir.makeDirectory()
            resultList = srcDir.listDirectoryRelatively(isRecursive=True, conditional=lambda x: x.isDirectory())
            for subDirRelPath in resultList:
                newSubDir = dstDir.traverseDirectory(subDirRelPath)
                newSubDir.makeDirectory()

        @staticmethod
        def removeEmptySubDirectories(dir:"File"):
            '''
            Remove all the empty sub-directories, recursive.
            '''
            emptyDirs = dir.listDirectory(isRecursive=True, conditional=lambda f: f.isEmptyDirectory())
            for emptyDir in emptyDirs:
                os.rmdir(str(emptyDir))
        
        class Path:
            
            @staticmethod
            def join(*paths):
                '''
                Concatenates multiple path(s).
                '''
                return os.path.abspath(os.path.join(*paths))
            
            @staticmethod
            def modifyName(path, name=None, suffix=None, extension=None):
                '''
                Modify name (e.g., replace extension, add suffix).
                
                Note that,
                - If `extension` is `''`, it is removed.
                '''
                split = os.path.split(path)
                splitExt = os.path.splitext(split[1])
                
                parentDir = split[0]
                name = name if (name != None) else (splitExt[0])
                extension = ('.' + extension) if (extension != None) else splitExt[1]
                extension = '' if (extension == '.') else extension
                suffix = suffix if (suffix != None) else ''
                
                return os.path.join(parentDir, name + suffix + extension)
                
            @staticmethod
            def randomizeName(path, fileNameLength=INTERNAL_Constants.MINIMUM_RANDOM_LENGTH, charPool=None):
                '''
                Randomize name, preserving the extension (if present).
                '''
                randomName = RandomUtils.Generation.String(fileNameLength, charPool)
                return File.Utils.Path.modifyName(path, name=randomName)
            
            @staticmethod
            def iterateName(path, suffix='-', iteratorLength=INTERNAL_Constants.MINIMUM_ITERATOR_LENGTH):
                '''
                Adds an iterator value to name, incrementally, stopping if it does not exist. 
                '''
                iterator = 1
                while (True):
                    currentSuffix = suffix + str(iterator).zfill(iteratorLength)
                    returnPath = File.Utils.Path.modifyName(path, suffix=currentSuffix)
                    if not os.path.exists(returnPath): break
                    iterator += 1
                return returnPath