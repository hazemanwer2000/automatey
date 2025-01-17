
import automatey.Base.ColorUtils as ColorUtils
import automatey.Abstract.Graphics as Graphics

import click

class INTERNAL:
    
    class ClickWrapper:
        
        Color2Color = {
            ColorUtils.Colors.WHITE: 'white',
            ColorUtils.Colors.BLACK: 'black',
            
            ColorUtils.Colors.RED: 'red',
            ColorUtils.Colors.YELLOW: 'yellow',
            
            ColorUtils.Colors.BLUE: 'blue',
            
            ColorUtils.Colors.PURPLE: 'magenta',
        }

def echo(message:str, textColor:Graphics.TextColor=None):
    '''
    Echo a string.
    
    Note that,
    - Supported colors are `WHITE`, `BLACK`, `RED`, `YELLOW`, `BLUE`, and `PURPLE`.
    '''
    kwargs = {}
    kwargs['nl'] = False
    if textColor != None:
        kwargs['fg'] = INTERNAL.ClickWrapper.Color2Color[textColor.foreground]
        kwargs['bg'] = INTERNAL.ClickWrapper.Color2Color[textColor.background]
    click.secho(message, **kwargs)

class ProgressBar:
    '''
    Progress-bar renderer, that calls `fcn` with `i` in range `0` to `N-1`, inclusive.
    
    Note that,
    - A new-line is echo'ed at the end.
    '''
    def __init__(self, fcn, N:int, label:str):
        self.fcn = fcn
        self.iterations = N
        self.label = label
        
    def render(self):
        '''
        Renders the progress-bar.
        '''
        with click.progressbar(range(self.iterations), label=self.label) as bar:
            for i in bar:
                self.fcn(i)

class LineOverwriter:
    '''
    Overwrites previous message with every call, until is skipped to next line.
    
    Note that,
    - To work properly, message may not contain a new-line character.
    '''
    class INTERNAL:
        
        TrackedMaxMessageLength = 0
        IsCurrentlyTracking = False
    
    @staticmethod
    def write(message:str, textColor:Graphics.TextColor=None):
        
        # ? (...)
        currentMessageLength = len(message)
        
        # ? Contruct prefix and suffix.
        prefix = ''
        suffix = ''
        if LineOverwriter.INTERNAL.IsCurrentlyTracking:
            prefix = ('\b' * LineOverwriter.INTERNAL.TrackedMaxMessageLength)
            CurrentDeltaLength = (LineOverwriter.INTERNAL.TrackedMaxMessageLength - currentMessageLength)
            if CurrentDeltaLength > 0:
                suffix = (' ' * CurrentDeltaLength)
            
        # ? Update tracked maximum message length.
        LineOverwriter.INTERNAL.IsCurrentlyTracking = True
        LineOverwriter.INTERNAL.TrackedMaxMessageLength = max(LineOverwriter.INTERNAL.TrackedMaxMessageLength, currentMessageLength)

        # ? Echo (all).
        echo(prefix + message, textColor=textColor)
        echo(suffix)
    
    @staticmethod
    def skipToNextLine():
        LineOverwriter.INTERNAL.TrackedMaxMessageLength = 0
        LineOverwriter.INTERNAL.IsCurrentlyTracking = False
        echo('\n')
