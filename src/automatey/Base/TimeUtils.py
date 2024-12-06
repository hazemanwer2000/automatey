
# Standard libraries
from datetime import datetime

class Constants:
    US_IN_HOUR = 3600000000
    US_IN_MINUTE = 60000000
    US_IN_SECOND = 1000000
    US_IN_MS = 1000

class Time:
    '''
    Representation of time, in micro-seconds.
    '''
    
    def __init__(self, microseconds:int):
        self.microseconds = microseconds
    
    def __int__(self) -> int:
        return self.microseconds
    
    def __str__(self) -> str:
        return self.toString()
    
    def __repr__(self) -> str:
        return str(self)
        
    def toString(self, precision:int=3) -> str:
        '''
        Returns string representation (HH:MM:SS.xxx).
        
        Precision denotes number of digits.
        '''
        hours, minutes, seconds, microseconds = self.toTimeUnits()
        formattedString = f"{hours:02}:{minutes:02}:{seconds:02}"
        
        if precision > 0:
            decimalPart =  f"{microseconds:06}"
            formattedString += '.' + decimalPart[0:precision]
            
        return formattedString
    
    def toTimeUnits(self):
        '''
        Returns a tuple of '(hours, minutes, seconds, microseconds)'
        '''
        remaining_us = self.microseconds
        
        hours = remaining_us // Constants.US_IN_HOUR
        remaining_us -= hours * Constants.US_IN_HOUR
        
        minutes = remaining_us // Constants.US_IN_MINUTE
        remaining_us -= minutes * Constants.US_IN_MINUTE
        
        seconds = remaining_us // Constants.US_IN_SECOND
        remaining_us -= seconds * Constants.US_IN_SECOND
        
        return  (hours, minutes, seconds, remaining_us)
    
    def toSeconds(self) -> float:
        return (self.microseconds / Constants.US_IN_SECOND)

    def toMilliseconds(self) -> float:
        return (self.microseconds / Constants.US_IN_MS)
    
    def __add__(self, obj):
        return Time(self.microseconds + obj.microseconds)
    
    def __sub__(self, obj):
        return Time(self.microseconds - obj.microseconds)
    
    @staticmethod
    def createFromString(formattedString:str):
        '''
        Create from string representation (HH:MM:SS.xxx)
        '''
        timeObj = datetime.strptime(formattedString, "%H:%M:%S.%f").time()
        return Time.createFromTimeUnits(timeObj.hour, timeObj.minute, timeObj.second, timeObj.microsecond)
    
    @staticmethod
    def createFromTimeUnits(hours:int, minutes:int, seconds:int, microseconds:int):
        '''
        Create from Time-unit(s).
        '''
        total_us = int((((((hours * 60) + minutes) * 60) + seconds) * Constants.US_IN_SECOND) + microseconds)
        return Time(total_us)

    @staticmethod
    def createFromSeconds(seconds:float):
        '''
        Create from second(s).
        '''
        total_us = int(seconds*Constants.US_IN_SECOND)
        return Time(total_us)

    @staticmethod
    def createFromMilliseconds(milliseconds:float):
        '''
        Create from milli-second(s).
        '''
        total_us = int(milliseconds*Constants.US_IN_MS)
        return Time(total_us)