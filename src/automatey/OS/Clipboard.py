
import pyperclip

def copy(text:str):
    '''
    Copy text to clipboard.
    '''
    pyperclip.copy(text)

def paste() -> str:
    '''
    Get text from clipboard.
    '''
    return pyperclip.paste()