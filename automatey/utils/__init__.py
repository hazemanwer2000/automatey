
import random
import string
import re
import os

class FileManagement:

    @staticmethod
    def readTextFile(path:str) -> str:
        """
        Read all from a (text-)file.

        Parameters
        ----------
        path : str
            Path to (text-)file.

        Returns
        -------
        txt : str
            Text.
        """
        with open(path, 'r') as f:
            txt = f.read()
        return txt
    
    @staticmethod
    def writeTextFile(path:str, txt:str):
        """
        Write text to a file.
        
        *Note:* If missing, file is created. If existing, file is overwritten.

        Parameters
        ----------
        path : str
            Path to file.
        txt : str
            Text.
        """
        with open(path, 'w') as f:
            f.write(txt)
    
    @staticmethod
    def readFile(path:str) -> bytes:
        """
        Read all (bytes) from a file.

        Parameters
        ----------
        path : str
            Path to file.

        Returns
        -------
        bin : bytes
            Bytes.
        """
        with open(path, 'rb') as f:
            bin = f.read()
        return bin

    @staticmethod 
    def writeFile(path:str, bin:bytes):
        """
        Write bytes to a file.
        
        *Note:* If missing, file is created. If existing, file is overwritten.

        Parameters
        ----------
        path : str
            Path to file.
        bin : bytes
            Bytes.
        """
        with open(path, 'wb') as f:
            f.write(bin)

    class Path:

        @staticmethod
        def getNextIterativePath(path:str, separator:str='#', suffix:str='', alt_ext:str=None, is_file:bool=None) -> str:
            """
            Get the next iterative path, that does not exist.

            For example, for **img.png**, if only **img-1.png** exists, **img-2.png** is returned.

            Parameters
            ----------
            path : str
                Path to file, or directory.
            separator : str
                In the example above, '-' is the separator.
            suffix : str
                In the example above, if suffix '_edit' is specified, **img_edit-2.png** is returned.
            alt_ext : str
                If a file is specified, this replaces the current file-extension.
                It must be without a dot.
            is_file : bool
                If specified, path does not need to point to an existing file, or directory.
                
            Returns
            -------
            new_path : str
                Constructed path.
            """
            is_file = is_file if (is_file != None) else os.path.isfile(path)

            if is_file:
                path_no_ext, ext = os.path.splitext(path)
                ext = ext if alt_ext == None else ('.' + alt_ext)
            else:
                path_no_ext = path
                ext = ''
            i = 1
            while True:
                new_path = path_no_ext + suffix + separator + str(i) + ext
                if not os.path.exists(new_path):
                    break
                i += 1
            return new_path

        @staticmethod
        def getNextRandomPath(path:str, name_len:int=8, alt_ext:str=None, is_file:bool=None) -> str:
            '''
            Get the next random path.

            Parameters
            ----------
            path : str
                Path to file, or directory.
            alt_ext : str
                If a file is specified, this replaces the current file-extension.
                It must be without a dot.
            name_len : str
                Length of the file-name, not including the extension (if present).
            is_file : bool
                If specified, path does not need to point to an existing file, or directory.

            Returns
            -------
            new_path : str
                Constructed path.
            '''
            is_file = is_file if (is_file != None) else os.path.isfile(path)

            if is_file:
                _, ext = os.path.splitext(path)
                ext = ext if alt_ext == None else ('.' + alt_ext)
            else:
                ext = ''
            parent_dir_path = os.path.dirname(path)
            return os.path.join(parent_dir_path, Random.getRandomString(name_len) + ext)

class Random:

    @staticmethod
    def getRandomText(len:int) -> str:
        """
        Generate random text, consisting only of upper-case letter(s) and digit(s).

        Parameters
        ----------
        len : int
            Expected length of text.

        Returns
        -------
        txt : str
            Random text.
        """
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(len))
    
class StringManipulation:
    
    @staticmethod
    def regexReplaceAll(expr_match, expr_replace, txt):
        """
        Replace all (RegEx-)matches to an expression, with another expression.

        Parameters
        ----------
        expr_match : str
            RegEx expression to match.
        expr_match : str
            RegEx expression to use for replacement.
        txt : str
            Text to search within.

        Returns
        -------
        res_txt : str
            Modified text.
        """
        return re.sub(expr_match, expr_replace, txt)
    
    @staticmethod
    def regexFindAll(expr_match:str, txt:str) -> list:
        """
        Find all (RegEx-)matches to an expression.

        Parameters
        ----------
        expr_match : str
            RegEx expression to match.
        txt : str
            Text to search within.

        Returns
        -------
        res : str
            A list of all matches. If more than one capture group is used, each match is a tuple.
        """
        res = re.findall(expr_match, txt)
        if res == None:
            res = []
        return res

class ProcessManagement:

    pass