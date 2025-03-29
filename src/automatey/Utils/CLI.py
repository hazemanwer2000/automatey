
import automatey.Utils.ColorUtils as ColorUtils
import automatey.Utils.TimeUtils as TimeUtils
import automatey.Utils.RandomUtils as RandomUtils
import automatey.Abstract.Graphics as Graphics
import automatey.Utils.Validation as Validation
import automatey.Utils.ExceptionUtils as ExceptionUtils

import click

import queue
import threading
import time

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
    Progress-bar renderer, that acts as a wrapper around an (actual) iterator.
    
    Note that,
    - A new-line is echo'ed at the end.
    '''
    
    @staticmethod
    def create(iterator, label:str):
        '''
        Usage:
        ```
        with ProgressBar.create(...) as iteratorWrapper:
            for item in iteratorWrapper:
                ...
        ```
        '''
        return click.progressbar(iterator, label=label)

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
        if len(suffix) > 0:
            echo(suffix)
    
    @staticmethod
    def skipToNextLine():
        LineOverwriter.INTERNAL.TrackedMaxMessageLength = 0
        LineOverwriter.INTERNAL.IsCurrentlyTracking = False
        echo('\n')

class VocalTimer:
    '''
    A vocal timer, for CLI application(s) with long I/O operation(s).
    
    Feature(s):
    - It runs on another thread.
    - It may be re-used.
    '''
    class INTERNAL:

        class State:
            
            def __init__(self):
                self.isHalted:bool = True
                self.referenceTime:TimeUtils.Time = None
                self.label:str = None
                self.textColor:str = None
                self.isTerminateThread:bool = False
        
        @staticmethod
        def sleep():
            time.sleep(RandomUtils.Generation.Float(0.08, 0.12))

    class Commands:
        
        class StartTimer:
            
            def __init__(self, label:str, textColor:Graphics.TextColor=None):
                self.label = label
                self.textColor = textColor
                
            def INTERNAL_stateTransition(self, state:"VocalTimer.INTERNAL.State"):
                state.isHalted = False
                state.referenceTime = TimeUtils.Time.getEpochTime()
                state.label = self.label
                state.textColor = self.textColor
        
        class StopTimer:

            def INTERNAL_stateTransition(self, state:"VocalTimer.INTERNAL.State"):
                state.isHalted = True
                LineOverwriter.skipToNextLine()
        
        class DestroyTimer:
            
            def INTERNAL_stateTransition(self, state:"VocalTimer.INTERNAL.State"):
                state.isTerminateThread = True
    
    def __init__(self):
        
        # ? Initialize large object(s).
        self.commandQueue = queue.Queue()
        self.notifyQueue = queue.Queue()
        self.thread = threading.Thread(target=self.INTERNAL_runner)
        
        # ? Start the thread.
        self.thread.start()
    
    def INTERNAL_runner(self):

        # ? Initialize working variable(s).
        state = VocalTimer.INTERNAL.State()
        
        while (True):

            # ? Check if there's a command pending in the queue.
            while not self.commandQueue.empty():
                command = self.commandQueue.get()
                command.INTERNAL_stateTransition(state)
                # ? ? Send notification back upon state-transition (i.e., a synchronous call)
                self.notifyQueue.put(None)
            
            # ? Check, if thread must be terminated.
            if state.isTerminateThread:
                break
            
            # ? If not halted, (...)
            if not state.isHalted:
                VocalTimer.INTERNAL.sleep()
                deltaTime = TimeUtils.Time.getEpochTime() - state.referenceTime
                message = state.label + '  ' + str(deltaTime)
                LineOverwriter.write(message, textColor=state.textColor)
    
    def issueCommand(self, command):
        self.commandQueue.put(command)
        self.notifyQueue.get()

class Input:
    '''
    Queries and manages input from user.
    '''

    @staticmethod
    def getString(msg:str):
        return input(msg).strip()
    
    @staticmethod
    def getFloat(msg:str):
        return Validation.asFloat(Input.getString())

    @staticmethod
    def getInt(msg:str):
        return Validation.asInt(Input.getString())

    @staticmethod
    def getBool(msg:str):
        return Validation.asBool(Input.getString())

    @staticmethod
    def getOption(msg:str, opts):
        print(msg)
        for idx, opt in enumerate(opts):
            print(f"{idx}: " + str(opt))
        selectedOpt = input('>>>')
        if selectedOpt not in opts:
            raise ExceptionUtils.ValidationError('Selected option is not a valid option.')
        return selectedOpt
