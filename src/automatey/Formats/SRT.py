
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

    def __init__(self, pysrt_subtitle):
        self.pysrt_subtitle = pysrt_subtitle

    def __str__(self):
        return f'Subtitle({self.getStartTime()}, {self.getEndTime()}, "{self.getText()}")'
    
    def __repr__(self):
        return str(self)
    
    def getStartTime(self) -> TimeUtils.Time:
        return TimeUtils.Time.createFromMilliseconds(self.pysrt_subtitle.start.ordinal)
    
    def getEndTime(self) -> TimeUtils.Time:
        return TimeUtils.Time.createFromMilliseconds(self.pysrt_subtitle.end.ordinal)

    def getDuration(self) -> TimeUtils.Time:
        return (self.getEndTime() - self.getStartTime())
    
    def getText(self) -> str:
        return self.pysrt_subtitle.text

    def setText(self, text) -> str:
        self.pysrt_subtitle.text = text

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
        return [Subtitle(x) for x in self.pysrt_subtitles]
    
    def shift(self, offset:TimeUtils.Time, sign:int=1):
        '''
        Shift all timestamps by an offset.
        '''
        self.pysrt_subtitles.shift(milliseconds=int(offset.toMilliseconds()) * sign)
    
    def saveAs(self, f:FileUtils.File):
        self.pysrt_subtitles.sort()
        self.pysrt_subtitles.save(str(f), encoding='utf-8')
