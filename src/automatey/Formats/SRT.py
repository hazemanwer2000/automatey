
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
        self.text = text

    def __str__(self):
        return f'Subtitle({self.startTime}, {self.endTime}, "{self.text}")'
    
    def __repr__(self):
        return str(self)
    
    def getStartTime(self) -> TimeUtils.Time:
        return self.startTime
    
    def getEndTime(self) -> TimeUtils.Time:
        return self.endTime

    def getDuration(self) -> TimeUtils.Time:
        return (self.endTime - self.startTime)
    
    def getText(self) -> str:
        return self.text

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
        subtitles = []
        for pysrt_subtitle in self.pysrt_subtitles:
            startTime = TimeUtils.Time.createFromMilliseconds(pysrt_subtitle.start.ordinal)
            endTime = TimeUtils.Time.createFromMilliseconds(pysrt_subtitle.end.ordinal)
            text = pysrt_subtitle.text
            subtitle = Subtitle(startTime, endTime, text)
            subtitles.append(subtitle)
        return subtitles
