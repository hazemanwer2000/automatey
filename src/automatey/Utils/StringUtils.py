
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
