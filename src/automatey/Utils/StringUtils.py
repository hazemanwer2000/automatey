
# Standard libraries
import re

class Regex:

    @staticmethod
    def replaceAll(expr_match, expr_replace, txt):
        """
        Replace all (RegEx-)matches to an expression, with another expression.
        """
        return re.sub(expr_match, expr_replace, txt)

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
