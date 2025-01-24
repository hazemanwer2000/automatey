
# Standard libraries
import datetime
import time

class Constants:
    US_IN_HOUR = 3600000000
    US_IN_MINUTE = 60000000
    US_IN_SECOND = 1000000
    US_IN_MS = 1000
    MS_IN_SECOND = 1000

class Time:
    '''
    Representation of time, in micro-seconds.
    
    Note that,
    - Negative value(s) are not supported.
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
        diff = self.microseconds - obj.microseconds
        return Time(max(diff, 0))
    
    def __truediv__(self, n:int):
        return Time(int(self.microseconds / n))
    
    def __eq__(self, obj):
        return self.microseconds == obj.microseconds

    def __ne__(self, obj):
        return self.microseconds != obj.microseconds

    def __lt__(self, obj):
        return self.microseconds < obj.microseconds

    def __le__(self, obj):
        return self.microseconds <= obj.microseconds

    def __gt__(self, obj):
        return self.microseconds > obj.microseconds

    def __ge__(self, obj):
        return self.microseconds >= obj.microseconds
    
    @staticmethod
    def createFromString(formattedString:str):
        '''
        Create from string representation (HH:MM:SS.xxx)
        '''
        timeObj = datetime.datetime.strptime(formattedString, "%H:%M:%S.%f").time()
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
    
    @staticmethod
    def getEpochTime():
        '''
        Gets the (current) Epoch time.
        '''
        return Time(int(time.time() * 1_000_000))

class Date:
    '''
    Representation of a date (e.g., '20250123').
    '''
    
    class INTERNAL:
        
        ReferenceDateTime = datetime.datetime(1, 1, 1)
        
        FormatSyntax = "%Y%m%d"
    
    def __init__(self, daysSince):
        self.daysSince = daysSince
    
    @staticmethod
    def createFromString(formattedString:str):
        datetimeObj = datetime.datetime.strptime(formattedString, Date.INTERNAL.FormatSyntax)
        return Date((datetimeObj - Date.INTERNAL.ReferenceDateTime).days)
    
    def toString(self):
        datetimeObj = Date.INTERNAL.ReferenceDateTime + datetime.timedelta(days=self.daysSince)
        return datetimeObj.strftime(Date.INTERNAL.FormatSyntax)
    
    def toUnits(self):
        datetimeObj = Date.INTERNAL.ReferenceDateTime + datetime.timedelta(days=self.daysSince)
        return datetimeObj.year, datetimeObj.month, datetimeObj.day 

    def __add__(self, obj):
        if isinstance(obj, int):
            return Date(self.daysSince + obj)

    def __sub__(self, obj):
        if isinstance(obj, int):
            return Date(self.daysSince - obj)
        elif isinstance(obj, Date):
            return int(self.daysSince - obj.daysSince)

    def __str__(self) -> str:
        return self.toString()
    
    def __repr__(self) -> str:
        return str(self)

class DateTime:
    '''
    Representation of a date-time (e.g., '20250123-121500-000000').
    
    It supports addition operation(s) with 'Time' object(s).
    '''
    
    class INTERNAL:
        
        ReferenceDateTime = datetime.datetime(1, 1, 1)
        
        FormatSyntax = "%Y%m%d-%H%M%S-%f"
    
    def __init__(self, microsecondsSince):
        self.microsecondsSince = microsecondsSince
    
    @staticmethod
    def createFromString(formattedString:str):
        datetimeObj = datetime.datetime.strptime(formattedString, DateTime.INTERNAL.FormatSyntax)
        datetimeDiffObj = (datetimeObj - Date.INTERNAL.ReferenceDateTime)
        totalMicroseconds = (int(datetimeDiffObj.total_seconds()) * Constants.US_IN_SECOND) + datetimeDiffObj.microseconds
        return DateTime(totalMicroseconds)
    
    def toString(self):
        datetimeObj = Date.INTERNAL.ReferenceDateTime + datetime.timedelta(microseconds=self.microsecondsSince)
        return datetimeObj.strftime(DateTime.INTERNAL.FormatSyntax)

    def __add__(self, obj):
        if isinstance(obj, Time):
            return DateTime(self.microsecondsSince + obj.microseconds)

    def __sub__(self, obj):
        if isinstance(obj, Time):
            return DateTime(self.microsecondsSince - obj.microseconds)

    def __str__(self) -> str:
        return self.toString()
    
    def __repr__(self) -> str:
        return str(self)
