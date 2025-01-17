
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
