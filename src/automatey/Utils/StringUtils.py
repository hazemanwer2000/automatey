
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
    def asParagraph(text:str):
        '''
        Strip, and remove all lines that are empty, or with white-space character(s) only.
        '''
        strippedText = text.strip()
        normalizedText = Regex.replaceAll(r'\n\s*\n', '\n', strippedText)
        return normalizedText
