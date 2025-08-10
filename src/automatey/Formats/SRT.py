
# Internal Libraries
import automatey.OS.FileUtils as FileUtils
import automatey.Utils.TimeUtils as TimeUtils

# Standard Libraries
import typing

# External Libraries
import pysrt

class Subtitle:
    '''
    Specifies a single entry (i.e., start-time, end-time, and associated text).
    '''

    def __init__(self,
                 startTime:TimeUtils.Time,
                 endTime:TimeUtils.Time,
                 text:str):
        self.startTime = startTime
        self.endTime = endTime
        self.text = self.text

    def __str__(self):
        return self.text
    
    def __repr__(self):
        return str(self)
    
    def getStartTime(self) -> TimeUtils.Time:
        return self.startTime
    
    def getEndTime(self) -> TimeUtils.Time:
        return self.endTime

    def getDuration(self) -> TimeUtils.Time:
        return (self.endTime - self.startTime)

class Parser:

    '''
    SRT representation.
    '''

    def __init__(self, f:FileUtils.File):
        self.pysrt_subtitles = pysrt.open(str(f), encoding='utf-8')

    def getSubtitles(self) -> typing.List['Subtitle']:
        '''
        Returns a list of 'Subtitle' objects.
        '''
        for pysrt_subtitle in self.pysrt_subtitles:
            text = pysrt_subtitle.text
            startTime = TimeUtils.Time.createFromMilliseconds(pysrt_subtitle.start.ordinal)
            print(startTime)