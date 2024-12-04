# External libraries
# ...

# Internal libraries
import automatey.OS.FileUtils as FileUtils
import automatey.Base.TimeUtils as TimeUtils
import automatey.OS.ProcessUtils as ProcessUtils
import automatey.Utils.StringUtils as StringUtils
import automatey.Base.ExceptionUtils as ExceptionUtils

from pprint import pprint 

class Action:
    pass

class Actions:
    
    class Trim(Action):
        '''
        Trim sequence.
        '''
        
        def __init__(self, startTime:TimeUtils.Time, endTime:TimeUtils.Time, isNearestKeyframe:bool=False, subActions=None):
            self.startTime = startTime
            self.endTime = endTime
            self.isNearestKeyframe = isNearestKeyframe
            self.subActions = subActions

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
        
        CommandTemplates = {
            'VideoTrim' : ProcessUtils.CommandTemplate(
                r'ffmpeg',
                r'-hide_banner',
                r'-loglevel error',
                r'-i {{{INPUT-FILE}}}',
                r'{{{START-TIME: -ss {{{TIME}}} :}}}',
                r'{{{END-TIME: -to {{{TIME}}} :}}}',
                r'-crf {{{CRF}}}',
                r'-c:v libx264',
                r'-c:a aac',
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
            result = StringUtils.Normalize.asSentence(result)
            fields = result.split(' ')
            for field in fields:
                fieldName, fieldValue = field.split('=')
                fieldSpecification = INTERNAL_VideoProcessing.FFMPEGWrapper.GeneralInfoFieldSpecification[fieldName]
                generalInfoDict[fieldSpecification['label']] = fieldSpecification['formatter'](fieldValue)
            
            return generalInfoDict
        
        @staticmethod
        def processTrimAction(f_src:FileUtils.File, f_tmpDst:FileUtils.File, trimAction:Actions.Trim, generalInfo:dict) -> list:
            
            command_VideoTrim = INTERNAL_VideoProcessing.FFMPEGWrapper.CommandTemplates['VideoTrim'].createFormatter()
            
            command_VideoTrim.assertParameter('input-file', str(f_src))
            command_VideoTrim.assertParameter('output-file', str(f_tmpDst))
            
            if trimAction.startTime != None:
                command_VideoTrim.assertSection('start-time', {'time' : trimAction.startTime.toString(precision=3)})
            else:
                command_VideoTrim.excludeSection('start-time')
                
            if trimAction.endTime != None:
                command_VideoTrim.assertSection('end-time', {'time' : trimAction.endTime.toString(precision=3)})
            else:
                command_VideoTrim.excludeSection('end-time')
                
            command_VideoTrim.assertParameter('crf', '15')
            
            return [str(command_VideoTrim)]
        
        @staticmethod
        def processJoinAction(f_joinList:list, f_tmpDst:FileUtils.File, joinAction:Actions.Join, generalInfo:dict) -> list:

            # Create listing (text) file
            f_txtTmpDst = FileUtils.File(
                FileUtils.File.Utils.Path.modifyName(
                    FileUtils.File.Utils.Path.randomizeName(str(f_tmpDst)),
                    extension='txt'
                )
            )
            with f_txtTmpDst.openFile('wt') as f_txtTmpDstHandler:
                for f in f_joinList:
                    f_txtTmpDstHandler.writeLine("file '" + str(f) + "'")
            
            # Create 'Concat' command
            command_VideoConcat = INTERNAL_VideoProcessing.FFMPEGWrapper.CommandTemplates['VideoConcat'].createFormatter()
            command_VideoConcat.assertParameter('list-file', str(f_txtTmpDst))
            command_VideoConcat.assertParameter('output-file', str(f_tmpDst))
            
            return [
                str(command_VideoConcat)
            ]
            
        @staticmethod
        def processGIFAction(f_src:FileUtils.File, f_tmpDst:FileUtils.File, GIFAction:Actions.GIF, generalInfo:dict) -> list:
            # Create 'GIFGenerate' command
            command_GIFGenerate = INTERNAL_VideoProcessing.FFMPEGWrapper.CommandTemplates['GIFGenerate'].createFormatter()
            
            command_GIFGenerate.assertParameter('input-file', str(f_src))
            command_GIFGenerate.assertParameter('output-file', str(f_tmpDst))
            
            captureFPS = GIFAction.captureFPS
            PTSFactor = 1 / GIFAction.playbackFactor
            width = GIFAction.width
            height = GIFAction.height
            
            command_GIFGenerate.assertParameter('capture-fps', f"{captureFPS:.3f}")
            command_GIFGenerate.assertParameter('pts-factor', f"{PTSFactor:.3f}")
            command_GIFGenerate.assertParameter('width', str(width))
            command_GIFGenerate.assertParameter('height', str(height))
            
            return [str(command_GIFGenerate)]
        
        @staticmethod
        def processActions(f_src:FileUtils.File, f_dst:FileUtils.File, actions:list, generalInfo:dict):
            f_tmpDir = FileUtils.File.Utils.getTemporaryDirectory()
            f_tmpBase = f_tmpDir.traverseDirectory(f_src.getName())
            commandList = []
            f_joinList = []
            
            # Find 'Join' action, and process each associated 'Trim' action.
            joinAction:Actions.Join = actions[0]
            for trimAction in joinAction.trimActions:
                f_tmpDst = FileUtils.File(FileUtils.File.Utils.Path.randomizeName(str(f_tmpBase)))
                commandList += INTERNAL_VideoProcessing.FFMPEGWrapper.processTrimAction(f_src, f_tmpDst, trimAction, generalInfo)
                f_joinList.append(f_tmpDst)
            
            # Process 'Join' action.
            if len(f_joinList) > 1:
                f_joinTmpDst = FileUtils.File(FileUtils.File.Utils.Path.randomizeName(str(f_tmpBase)))
                commandList += INTERNAL_VideoProcessing.FFMPEGWrapper.processJoinAction(f_joinList, f_joinTmpDst, joinAction, generalInfo)
            else:
                f_joinTmpDst = f_joinList[0]
            
            # Find, and process 'GIF' action, if present.
            if (len(actions) > 1):
                GIFAction = actions[1]
                f_gifTmpDst = FileUtils.File(
                    FileUtils.File.Utils.Path.modifyName(
                        FileUtils.File.Utils.Path.randomizeName(str(f_tmpBase)),
                        extension='gif'
                    )
                )
                commandList += INTERNAL_VideoProcessing.FFMPEGWrapper.processGIFAction(f_joinTmpDst, f_gifTmpDst, GIFAction, generalInfo)
                f_finalTmpDst = f_gifTmpDst
            else:
                f_finalTmpDst = f_joinTmpDst
                
            #pprint(commandList, width=400)
            #return
            
            # Execute command-list.
            INTERNAL_VideoProcessing.FFMPEGWrapper.executeCommands(commandList)
            
            # Copy into (actual) destination, and delete temporary directory.
            FileUtils.File.Utils.copyFile(f_finalTmpDst, f_dst)
            FileUtils.File.Utils.recycle(f_tmpDir)
            
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
        - Other action(s) may be applied to 'Trim'.
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
