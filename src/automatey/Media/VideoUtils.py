# External libraries
# ...

# Internal libraries
import automatey.OS.FileUtils as FileUtils
import automatey.Base.TimeUtils as TimeUtils
import automatey.OS.ProcessUtils as ProcessUtils
import automatey.Utils.StringUtils as StringUtils
import automatey.Base.ExceptionUtils as ExceptionUtils

from pprint import pprint 

class Quality:
    
    class HIGH: pass
    class AVERAGE: pass

class Action:
    pass

class Modifier:
    pass

class Filter(Modifier):
    pass

class Transition(Modifier):
    pass

class Scalar(Modifier):
    pass

class AudioModifier:
    pass

class AudioTransition(AudioModifier):
    pass

class Actions:

    class Modifiers:
        
        class Filters:
            
            class SepiaTone(Filter):
                pass
            
            class Grayscale(Filter):
                pass

    class Trim(Action):
        '''
        Trim sequence.
        '''
        
        def __init__(self, startTime:TimeUtils.Time, 
                     endTime:TimeUtils.Time,
                     isMute=False,
                     isNearestKeyframe:bool=False,
                     quality=Quality.HIGH,
                     modifiers=None):
            self.startTime = startTime
            self.endTime = endTime
            self.isMute = isMute
            self.isNearestKeyframe = isNearestKeyframe
            self.quality = quality
            self.modifiers = [] if (modifiers == None) else modifiers

    class Join(Action):
        '''
        Join sequence(s).
        '''
        
        def __init__(self, *trimActions):
            self.trimActions = trimActions
            
    class GIF(Action):
        '''
        Output is a GIF.
        
        Note,
        - Capture FPS specifies the FPS at which frame(s) are sampled.
        '''
        
        def __init__(self, captureFPS, playbackFactor=1.0, width=-1, height=-1):
            self.captureFPS = captureFPS
            self.playbackFactor = playbackFactor
            self.width=width
            self.height=height

class INTERNAL_VideoProcessing:
    
    class FFMPEGWrapper:
        
        Constants = {
            'AverageCRF' : 17,
            'HighCRF' : 12,
        }
        
        CommandTemplates = {
            'VideoTrimNearestKeyframe' : ProcessUtils.CommandTemplate(
                r'ffmpeg',
                r'-hide_banner',
                r'-loglevel error',
                r'-noaccurate_seek',
                r'{{{START-TIME: -ss {{{TIME}}} :}}}',
                r'-i {{{INPUT-FILE}}}',
                r'{{{DURATION: -to {{{TIME}}} :}}}',
                r'-vcodec copy',
                r'-acodec copy',
                r'-avoid_negative_ts make_zero',
                r'{{{OUTPUT-FILE}}}',
            ),
            'VideoTrim' : ProcessUtils.CommandTemplate(
                r'ffmpeg',
                r'-hide_banner',
                r'-loglevel error',
                r'{{{START-TIME: -ss {{{TIME}}} :}}}',
                r'-i {{{INPUT-FILE}}}',
                r'{{{DURATION: -to {{{TIME}}} :}}}',
                r'-crf {{{CRF}}}',
                r'-c:v libx264',
                r'-c:a aac',
                r'{{{VIDEO-FILTER: -vf {{{VALUE}}} :}}}',
                r'{{{AUDIO-FILTER: -af {{{VALUE}}} :}}}',
                r'{{{OUTPUT-FILE}}}',
            ),
            'VideoMute' : ProcessUtils.CommandTemplate(
                r'ffmpeg',
                r'-hide_banner',
                r'-loglevel error',
                r'-i {{{INPUT-FILE}}}',
                r'-c copy',
                r'-an',
                r'{{{OUTPUT-FILE}}}',
            ),
            'VideoConcat' : ProcessUtils.CommandTemplate(
                r'ffmpeg',
                r'-hide_banner',
                r'-loglevel error',
                r'-f concat',
                r'-safe 0',
                r'-i {{{LIST-FILE}}}',
                r'-c copy',
                r'{{{OUTPUT-FILE}}}',
            ),
            'GIFGenerate' : ProcessUtils.CommandTemplate(
                r'ffmpeg',
                r'-hide_banner',
                r'-loglevel error',
                r'-i {{{INPUT-FILE}}}',
                r'-vf fps={{{CAPTURE-FPS}}},scale={{{WIDTH}}}:{{{HEIGHT}}}:flags=lanczos,setpts={{{PTS-FACTOR}}}*PTS[v]',
                r'-loop 0',
                r'{{{OUTPUT-FILE}}}',
            ),
            'QueryGeneralInfo' : ProcessUtils.CommandTemplate(
                r'ffprobe',
                r'-v error',
                r'-select_streams v:0',
                r'-show_entries stream=avg_frame_rate,width,height',
                r'-of default=noprint_wrappers=1',
                r'{{{INPUT-FILE}}}',
            )
        }
        
        @staticmethod
        def queryInfo(f_src:FileUtils.File, commandName) -> str:
            '''
            Executes a command, with a single `input-file`, and meant to extract info.
            '''
            
            # Format command.
            command_QueryInfo = INTERNAL_VideoProcessing.FFMPEGWrapper.CommandTemplates[commandName].createFormatter()
            command_QueryInfo.assertParameter('input-file', str(f_src))
            
            # Execute.
            proc = ProcessUtils.Process(str(command_QueryInfo))
            proc.run()
            
            return proc.STDOUT()
        
        GeneralInfoFieldSpecification = {
            'width' : {
                'label' : 'width',
                'formatter' : lambda x: int(eval(x))
            },
            'height' : {
                'label' : 'height',
                'formatter' : lambda x: int(eval(x))
            },
            'avg_frame_rate' : {
                'label' : 'fps',
                'formatter' : lambda x: float(eval(x))
            }
        }
        
        @staticmethod
        def queryGeneralInfo(f_src:FileUtils.File) -> float:
            '''
            Returns a dictionary, with,
            
            - Width, as `width`
            - Height, as `height`
            - FPS, as `fps`
            '''
            
            generalInfoDict = {}
            
            # Fetch, and extract info from result.
            result = INTERNAL_VideoProcessing.FFMPEGWrapper.queryInfo(f_src, 'QueryGeneralInfo')
            result = result.strip()
            result = StringUtils.Regex.replaceAll(r'\s+', ' ', result)
            fields = result.split(' ')
            for field in fields:
                fieldName, fieldValue = field.split('=')
                fieldSpecification = INTERNAL_VideoProcessing.FFMPEGWrapper.GeneralInfoFieldSpecification[fieldName]
                generalInfoDict[fieldSpecification['label']] = fieldSpecification['formatter'](fieldValue)
            
            return generalInfoDict

        class VideoFilterConstructors:
            
            @staticmethod
            def SepiaTone():
                return ''

        @staticmethod
        def deriveVideoFilters(modifiers):
            return ''
        
        @staticmethod
        def deriveAudioFilters(modifiers):
            return ''
        
        QualityToCRF = {
            Quality.AVERAGE : Constants['AverageCRF'],
            Quality.HIGH : Constants['HighCRF'],
        }
        
        @staticmethod
        def processTrimAction(f_src:FileUtils.File, f_tmpBase:FileUtils.File, trimAction:Actions.Trim, generalInfo:dict) -> list:
            commandList = []
            
            if (trimAction.isNearestKeyframe):
                command_VideoTrim = INTERNAL_VideoProcessing.FFMPEGWrapper.CommandTemplates['VideoTrimNearestKeyframe'].createFormatter()
            else:
                command_VideoTrim = INTERNAL_VideoProcessing.FFMPEGWrapper.CommandTemplates['VideoTrim'].createFormatter()

            command_VideoTrim.assertParameter('input-file', str(f_src))
            
            if trimAction.startTime != None:
                startTime = trimAction.startTime
                command_VideoTrim.assertSection('start-time', {'time' : startTime.toString(precision=3)})
            else:
                startTime = TimeUtils.Time(0)
                command_VideoTrim.excludeSection('start-time')
                
            if trimAction.endTime != None:
                duration = trimAction.endTime - startTime
                command_VideoTrim.assertSection('duration', {'time' : duration.toString(precision=3)})
            else:
                command_VideoTrim.excludeSection('end-time')
            
            # If trimming is not at nearest key-frame, then it is possible to specify filter(s), and CRF value.
            if not (trimAction.isNearestKeyframe):
                # Deriving CRF value.
                CRFValue = INTERNAL_VideoProcessing.FFMPEGWrapper.QualityToCRF[trimAction.quality]
                command_VideoTrim.assertParameter('crf', str(CRFValue))
                
                # Processing modifier(s).
                modifiers = [modifier for modifier in trimAction.modifiers if issubclass(modifier, Modifier)]
                audioModifiers = [modifier for modifier in trimAction.modifiers if issubclass(modifier, AudioModifier)]
                
                videoFilters:str = INTERNAL_VideoProcessing.FFMPEGWrapper.deriveVideoFilters(modifiers)
                audioFilters:str = INTERNAL_VideoProcessing.FFMPEGWrapper.deriveAudioFilters(audioModifiers)
                
                if videoFilters == '':
                    command_VideoTrim.excludeSection('video-filter')
                else:
                    command_VideoTrim.assertSection('video-filter', {'value': videoFilters})
                    
                if audioFilters == '':
                    command_VideoTrim.excludeSection('audio-filter')
                else:
                    command_VideoTrim.assertSection('audio-filter', {'value': audioFilters})
            
            lastCommand = command_VideoTrim
            
            # Check if mute'ing is necessary.
            if trimAction.isMute:
                f_tmpDst = FileUtils.File(FileUtils.File.Utils.Path.randomizeName(str(f_tmpBase)))
                lastCommand.assertParameter('output-file', str(f_tmpDst))
                commandList.append(str(lastCommand))
                
                command_VideoMute = INTERNAL_VideoProcessing.FFMPEGWrapper.CommandTemplates['VideoMute'].createFormatter()
                command_VideoMute.assertParameter('input-file', str(f_tmpDst))
                lastCommand = command_VideoMute
            
            # Finalization.
            f_tmpDst = FileUtils.File(FileUtils.File.Utils.Path.randomizeName(str(f_tmpBase)))
            lastCommand.assertParameter('output-file', str(f_tmpDst))
            commandList.append(str(lastCommand))
            
            return commandList, f_tmpDst
        
        @staticmethod
        def processJoinAction(f_src:FileUtils.File, f_tmpBase:FileUtils.File, joinAction:Actions.Join, generalInfo:dict) -> list:
            commandList = []
            f_joinList = []

            # Process each associated 'Trim' action.
            for trimAction in joinAction.trimActions:
                newCommandList, f_trimTmpDst = INTERNAL_VideoProcessing.FFMPEGWrapper.processTrimAction(f_src, f_tmpBase, trimAction, generalInfo)
                commandList += newCommandList
                f_joinList.append(f_trimTmpDst)
            
            # Join video file(s), if necessary.
            if len(f_joinList) > 1:
                # Create listing (text) file
                f_txtTmpDst = FileUtils.File(
                    FileUtils.File.Utils.Path.modifyName(
                        FileUtils.File.Utils.Path.randomizeName(str(f_tmpBase)),
                        extension='txt'
                    )
                )
                with f_txtTmpDst.openFile('wt') as f_txtTmpDstHandler:
                    for f in f_joinList:
                        f_txtTmpDstHandler.writeLine("file '" + str(f) + "'")
                
                # Create 'Concat' command
                f_joinTmpDst = FileUtils.File(FileUtils.File.Utils.Path.randomizeName(str(f_tmpBase)))
                command_VideoConcat = INTERNAL_VideoProcessing.FFMPEGWrapper.CommandTemplates['VideoConcat'].createFormatter()
                command_VideoConcat.assertParameter('list-file', str(f_txtTmpDst))
                command_VideoConcat.assertParameter('output-file', str(f_joinTmpDst))
                
                commandList.append(str(command_VideoConcat))
                f_finalTmpDst = f_joinTmpDst
            else:
                f_finalTmpDst = f_joinList[0]
            
            return commandList, f_finalTmpDst
            
        @staticmethod
        def processGIFAction(f_src:FileUtils.File, f_tmpBase:FileUtils.File, GIFAction:Actions.GIF, generalInfo:dict) -> list:
            
            f_gifTmpDst = FileUtils.File(
                FileUtils.File.Utils.Path.modifyName(
                    FileUtils.File.Utils.Path.randomizeName(str(f_tmpBase)),
                    extension='gif'
                )
            )
            
            command_GIFGenerate = INTERNAL_VideoProcessing.FFMPEGWrapper.CommandTemplates['GIFGenerate'].createFormatter()
            
            command_GIFGenerate.assertParameter('input-file', str(f_src))
            command_GIFGenerate.assertParameter('output-file', str(f_gifTmpDst))
            
            captureFPS = GIFAction.captureFPS
            PTSFactor = 1 / GIFAction.playbackFactor
            width = GIFAction.width
            height = GIFAction.height
            
            command_GIFGenerate.assertParameter('capture-fps', f"{captureFPS:.3f}")
            command_GIFGenerate.assertParameter('pts-factor', f"{PTSFactor:.3f}")
            command_GIFGenerate.assertParameter('width', str(width))
            command_GIFGenerate.assertParameter('height', str(height))
            
            return [str(command_GIFGenerate)], f_gifTmpDst
        
        @staticmethod
        def processActions(f_src:FileUtils.File, f_dst:FileUtils.File, actions:list, generalInfo:dict):
            f_tmpDir = FileUtils.File.Utils.getTemporaryDirectory()
            f_tmpBase = f_tmpDir.traverseDirectory(f_src.getName())
            commandList = []
            
            # Process (mandatory) 'Join' action.
            joinAction = actions[0]
            newCommandList, f_joinTmpDst = INTERNAL_VideoProcessing.FFMPEGWrapper.processJoinAction(f_src, f_tmpBase, joinAction, generalInfo)
            commandList += newCommandList
            
            # Find, and process 'GIF' action, if present.
            if (len(actions) > 1):
                GIFAction = actions[1]
                newCommandList, f_gifTmpDst = INTERNAL_VideoProcessing.FFMPEGWrapper.processGIFAction(f_joinTmpDst, f_tmpBase, GIFAction, generalInfo)
                commandList += newCommandList
                f_finalTmpDst = f_gifTmpDst
            else:
                f_finalTmpDst = f_joinTmpDst
            
            pprint(commandList, width=400)
            
            try:
                # Execute command-list.
                INTERNAL_VideoProcessing.FFMPEGWrapper.executeCommands(commandList)
                
                # Copy into (actual) destination, and delete temporary directory.
                FileUtils.File.Utils.copyFile(f_finalTmpDst, f_dst)
                FileUtils.File.Utils.recycle(f_tmpDir)
                
            except ExceptionUtils.BackendError as e:
                # Delete temporary directory, before propagating error.
                FileUtils.File.Utils.recycle(f_tmpDir)
                raise
            
        @staticmethod
        def executeCommands(commandList):
            for command in commandList:
                print(command)
                proc = ProcessUtils.Process(str(command))
                if (proc.run() != 0):
                    raise ExceptionUtils.BackendError(proc.STDERR())

# Deals in 'Action'(s) and General-Info
class Video:
    '''
    Video-handler.
    
    Note, currently only 'mp4' format is supported.
    '''

    def __init__(self, f:FileUtils.File):
        self.f_src = f
        self.actions = []
        self.generalInfo = INTERNAL_VideoProcessing.FFMPEGWrapper.queryGeneralInfo(self.f_src)
        
    def getFPS(self):
        return self.generalInfo['fps']

    def getDimensions(self):
        return (self.generalInfo['width'], self.generalInfo['height'])
        
    def registerAction(self, action:Action):
        '''
        Register an action.
        
        Note,
        - Only a single 'Join' (mandatory), which consists of one or more 'Trim' action(s), and a 'GIF' (optional) are supported.
        - Modifier(s) may be applied to 'Trim' action(s).
        - All action(s) are order sensitive.
        '''
        self.actions.append(action)
    
    def saveAs(self, f_dst:FileUtils.File):
        '''
        Processes registered action(s), and save end-file.
        '''
        INTERNAL_VideoProcessing.FFMPEGWrapper.processActions(self.f_src, f_dst, self.actions, self.generalInfo)
    
    def clearActions(self):
        '''
        Clears all registered action(s)
        '''
        self.actions.clear()
        
    class Utils:
        
        @staticmethod
        def isVideo(f:FileUtils.File):
            '''
            Check if file is a video.
            
            Note, currently only 'mp4' format is supported.
            '''
            return f.getExtension() == 'mp4'