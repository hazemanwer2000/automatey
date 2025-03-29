
# Standard libraries
import re

class Indent:
    '''
    Add indentation to each line within a text.
    '''
    
    @staticmethod
    def prepend(text:str, indentation:str):
        return indentation + text.replace('\n', indentation + '\n')

    @staticmethod
    def append(text:str, indentation:str):
        return text.replace('\n', '\n' + indentation) + indentation

class Regex:

    @staticmethod
    def replaceAll(expr_match, expr_replace, txt, count=0):
        """
        Replace all (RegEx-)matches to an expression, with another expression.
        """
        return re.sub(expr_match, expr_replace, txt, count=count)

    @staticmethod
    def findAll(expr_match:str, txt:str) -> list:
        """
        Find all (RegEx-)matches to an expression.

        Returns a list of all matches. If more than one capture group is used, each match is a tuple.
        """
        res = re.findall(expr_match, txt)
        if res == None:
            res = []
        return res

class Normalize:
    
    @staticmethod
    def asSentence(text:str):
        '''
        Strip, and replace multiple, consecutive occurences of white-space character(s), with a single space.
        '''
        strippedText = text.strip()
        normalizedText = Regex.replaceAll(r'\s+', ' ', strippedText)
        return normalizedText

    @staticmethod
    def asParagraph(text:str, INTERNAL_newLine:str='\n'):
        '''
        Remove all lines that are empty, or with white-space character(s) only, then normalize each line as sentence.
        '''
        # ? Remove all lines that are empty.
        strippedText = text.strip()
        normalizedText = Regex.replaceAll(r'\n\s*\n', INTERNAL_newLine, strippedText)
        # ? Strip each line.
        lines = normalizedText.split('\n')
        for i in range(len(lines)):
            lines[i] = Normalize.asSentence(lines[i])
        return '\n'.join(lines)

    @staticmethod
    def asParagraphs(text:str):
        '''
        Similar to `asParagraph`, but consecutive empty-line(s) are replaced with a single empty-line.
        '''
        return Normalize.asParagraph(text, INTERNAL_newLine='\n\n')
    
class EmptyLine:
    
    @staticmethod
    def lstripLines(text:str):
        '''
        Remove all line(s) at the beginning that are empty, or with white-space character(s) only.
        '''
        textLines = text.split('\n')
        
        # ? Remove lines at the beginning.
        while len(textLines) > 0:
            if textLines[0].strip() == '':
                del textLines[0]
            else:
                break
        
        return '\n'.join(textLines)
    
    @staticmethod
    def rstripLines(text:str):
        '''
        Remove all line(s) at the end that are empty, or with white-space character(s) only.
        '''
        textLines = text.split('\n')
        
        # ? Remove lines at the end.
        while len(textLines) > 0:
            if textLines[-1].strip() == '':
                del textLines[-1]
            else:
                break
        
        return '\n'.join(textLines)

    @staticmethod
    def stripLines(text:str):
        '''
        Combines both `lstripLines` and `rstripLines`.
        '''
        return EmptyLine.rstripLines(EmptyLine.lstripLines(text))
    
    @staticmethod
    def removeEmptyLines(text:str, INTERNAL_newLine='\n'):
        '''
        Remove all lines that are empty, or with white-space character(s) only.
        '''
        strippedText = EmptyLine.stripLines(text)
        return Regex.replaceAll(r'\n\s*\n', INTERNAL_newLine, strippedText)

    @staticmethod
    def removeConsecutiveEmptyLines(text:str):
        '''
        Similar to `asParagraph`, but consecutive empty-line(s) are replaced with a single empty-line.
        '''
        return EmptyLine.removeEmptyLines(text, INTERNAL_newLine='\n\n')

class Split:
    
    def atWords(text:str):
        '''
        Given a concatenated string of words (e.g., `GIFForExample`), returns a list of words (e.g., `['GIF', 'For', 'Example']`).
        '''
        return Regex.findAll(r'[A-Z]+(?=[A-Z][a-z]|$)|[A-Z][a-z]*', text)

class Case:

    @staticmethod
    def Pascal2Snake(text:str, character:str='-'):
        return character.join([x.lower() for x in Split.atWords(text)])

    @staticmethod
    def Snake2Pascal(text:str, character:str='-'):
        return ''.join([x.capitalize() for x in text.split(character)])

class MakePretty:
    
    @staticmethod
    def Size(sizeInBytes:int):
        for unit in ['', 'KB', 'MB', 'GB', 'TB', 'PB']:
            if sizeInBytes < 1024:
                return f"{sizeInBytes:.2f} {unit}"
            sizeInBytes /= 1024

class HexString:
    
    @staticmethod
    def fromBytes(_bytes:bytes) -> str:
        return _bytes.hex()

    @staticmethod
    def toBytes(hexStr:bytes) -> bytes:
        return bytes.fromhex(hexStr)
    
    @staticmethod
    def fromCArray(text:str) -> str:
        hexBytesList = Regex.findAll(r'0[xX]([a-fA-F0-9]{1,2})', text)
        for idx, hexByte in enumerate(hexBytesList):
            if len(hexByte) == 1:
                hexBytesList[idx] = '0' + hexBytesList[idx]
        return ''.join(hexBytesList).lower()
    
    @staticmethod
    def toCArray(text:str, bytesPerLine:int=8) -> str:
        text = text.lower()
        hexBytesList = [('0x' + text[i:i+2]) for i in range(0, len(text), 2)]
        chunks = []
        for i in range(0, len(hexBytesList), bytesPerLine):
            chunkList = hexBytesList[i:i+bytesPerLine]
            chunk = ', '.join(chunkList)
            chunks.append(chunk)
        return ',\n'.join(chunks)

class Writer:
    '''
    To be used to write text, in a more clean way.
    '''
    
    def __init__(self):
        self.text = ''
        
    def write(self, newText, indentation:str=None, isAppendNewLine:bool=True):
        if indentation is not None:
            newText = Indent.prepend(newText, indentation)
        if isAppendNewLine:
            newText += '\n'
        self.text += newText
    
    def writeLines(self, lines, indentation:str=None, isAppendNewLine:bool=True):
        self.write('\n'.join(lines), indentation, isAppendNewLine)
        
    def newLine(self):
        self.text += '\n'
        
    def clear(self):
        self.text = ''
    
    def __str__(self):
        return self.text
    
    def __repr__(self):
        return str(self)

class Verbose:
    '''
    Operation(s) that are simple, but are better verbalized.
    '''

    @staticmethod
    def quote(text:str):
        return f"'{text}'"

    @staticmethod
    def doubleQuote(text:str):
        return f'"{text}"'
