# External libraries
# ...

# Internal libraries
import automatey.OS.FileUtils as FileUtils
import automatey.Base.TimeUtils as TimeUtils
import automatey.OS.ProcessUtils as ProcessUtils
import automatey.Utils.StringUtils as StringUtils
import automatey.Base.ExceptionUtils as ExceptionUtils
import automatey.Abstract.Graphics as AbstractGraphics
import automatey.Base.ColorUtils as ColorUtils
import automatey.Utils.Validation as Validation
import automatey.Resources as Resources

class INTERNAL_Utils:    

    class Action:
        pass
    
    class Modifier:
        pass
    
    class Filter(Modifier):
        pass
    
    class Transition(Modifier):
        pass

    class Transformation(Modifier):
        pass

    class AudioModifier:
        pass

    class AudioTransition(AudioModifier):
        pass

class Actions:

    class Trim(INTERNAL_Utils.Action):
        '''
        Trim sequence.
        '''
        
        def __init__(self, startTime:TimeUtils.Time, 
                     endTime:TimeUtils.Time,
                     isMute=False,
                     isNearestKeyframe:bool=False,
                     CRF:int=None,
                     modifiers=None):
            self.startTime = startTime
            self.endTime = endTime
            self.isMute = isMute
            self.isNearestKeyframe = isNearestKeyframe
            self.CRF = CRF
            self.modifiers = [] if (modifiers is None) else modifiers

    class Join(INTERNAL_Utils.Action):
        '''
        Join sequence(s).
        '''
        
        def __init__(self, *trimActions):
            self.trimActions = trimActions
            
    class GIF(INTERNAL_Utils.Action):
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

class Modifiers:
    
    class Filters:
    
        class SepiaTone(INTERNAL_Utils.Filter):
            pass
        
        class Grayscale(INTERNAL_Utils.Filter):
            pass
        
        class Brightness(INTERNAL_Utils.Filter):
            '''
            Adjust brightness, contrast, and saturation.
            
            Value(s) are factor(s) (i.e., '1.0' has no effect).
            '''
            def __init__(self, brightness=1.0, contrast=1.0, saturation=1.0):
                self.brightness = brightness
                self.contrast = contrast
                self.saturation = saturation
        
        class GaussianBlur(INTERNAL_Utils.Filter):
            '''
            Applies gaussian blur.
            '''
            def __init__(self, kernelSize):
                self.kernelSize = kernelSize
                
        class Sharpen(INTERNAL_Utils.Filter):
            '''
            Sharpen.
            
            Value(s) are factor(s) (i.e., '1.0' has no effect).
            
            (Optional) Kernel-size must be odd.
            '''
            def __init__(self, factor, kernelSize=5):
                self.factor = factor
                self.kernelSize = kernelSize
                
        class Pixelate(INTERNAL_Utils.Filter):
            '''
            Pixelate.
            
            Value(s) are factor(s) (i.e., '1' has no effect).
            
            Note that, value(s) should be integer(s).
            '''
            def __init__(self, factor):
                self.factor = factor

        class Noise(INTERNAL_Utils.Filter):
            '''
            Add noise.
            
            Value(s) are factor(s) (i.e., '1.0' has no effect).
            
            Note that, factor must be `>= 1.0`.
            '''
            def __init__(self, factor):
                self.factor = factor
                
        class AddBorder(INTERNAL_Utils.Filter):
            '''
            Adds a border.
            '''
            def __init__(self, border:AbstractGraphics.Border):
                self.border = border
                
        class Crop(INTERNAL_Utils.Filter):
            '''
            Crop.
            
            Note that (1, 1) specifies the pixel at the top-left corner.
            '''
            def __init__(self, topLeft:AbstractGraphics.Point, bottomRight:AbstractGraphics.Point):
                self.topLeft = topLeft
                self.bottomRight = bottomRight

        class Resize(INTERNAL_Utils.Filter):
            '''
            Resize an image, given '(W, H)'.
            
            If either set to '-1', aspect ratio is preserved.
            '''
            def __init__(self, width=-1, height=-1):
                self.width = width
                self.height = height

    class Transitions:
        
        class FadeIn(INTERNAL_Utils.Transition):
            '''
            Apply fade-in (from black) effect.
            '''
            def __init__(self, duration:TimeUtils.Time):
                self.duration = duration

        class FadeOut(INTERNAL_Utils.Transition):
            '''
            Apply fade-out (to black) effect.
            '''
            def __init__(self, duration:TimeUtils.Time):
                self.duration = duration

    class Transformations:
        
        class Rotate(INTERNAL_Utils.Transformation):
            '''
            Apply rotation.
            
            Note that,
            - Only `90` degree multiple(s) are supported.
            '''
            def __init__(self, rotation:AbstractGraphics.Rotation):
                self.rotation = rotation
        
        class Mirror(INTERNAL_Utils.Transformation):
            '''
            Mirror, either vertically or horizontally.
            '''
            def __init__(self, mirror):
                self.mirror = mirror

class AudioModifiers:
    
    class Transitions:
        
        class FadeIn(INTERNAL_Utils.AudioTransition):
            '''
            Apply fade-in effect.
            '''
            def __init__(self, duration:TimeUtils.Time):
                self.duration = duration

        class FadeOut(INTERNAL_Utils.AudioTransition):
            '''
            Apply fade-out effect.
            '''
            def __init__(self, duration:TimeUtils.Time):
                self.duration = duration

class ThumbnailTimestampAttributes:
    
    '''
    All attributes related to a timestamp, for a thumbnail.
    '''
    
    def __init__(self,
                 textColor:ColorUtils.Color,
                 cornerAlignment):
        self.textColor = textColor
        self.cornerAlignment = cornerAlignment

class INTERNAL_VideoProcessing:
    
    class FFMPEGWrapper:
        
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
                r'-show_entries stream=avg_frame_rate,width,height,duration',
                r'-of default=noprint_wrappers=1',
                r'{{{INPUT-FILE}}}',
            ),
            'QueryKeyframes' : ProcessUtils.CommandTemplate(
                r'ffprobe',
                r'-v error',
                r'-select_streams v:0',
                r'-show_entries frame=pts_time,pict_type',
                r'-of csv=print_section=0',
                r'-skip_frame nokey',
                r'{{{INPUT-FILE}}}',
            ),
            'ThumbnailGenerate' : ProcessUtils.CommandTemplate(
                r'ffmpeg',
                r'-hide_banner',
                r'-loglevel error',
                r'-i {{{INPUT-FILE}}}',
                r"{{{TIMESTAMP: -vf drawtext=text='%{pts\:hms}':{{{LOCATION}}}:fontsize={{{TEXT-SIZE}}}*h:fontcolor={{{TEXT-COLOR}}}:fontfile={{{FONT-PATH}}} :}}}",
                r'-ss {{{TIME}}}',
                r'-vframes 1',
                r'{{{OUTPUT-FILE}}}',
            ),
            'ThumbnailsGenerate' : ProcessUtils.CommandTemplate(
                r'ffmpeg',
                r'-hide_banner',
                r'-loglevel error',
                r'-i {{{INPUT-FILE}}}',
                r'-vf fps={{{CAPTURE-FPS}}}',
                r'{{{OUTPUT-DIRECTORY}}}/%03d.png',
            ),
        }
        
        ThumbnailTimestampDefaults = {
            'Offset' : {
                'X' : 10,
                'Y' : 10,
            },
            # Note: Text size is specified in percentage of thumbnail height.
            'TextSize' : 0.05,
            'FontFile' : Resources.resolve(FileUtils.File('font/texgyrecursor/texgyrecursor-regular.otf')) 
        }
        
        ThumbnailTimestampLocationTemplates = {
            AbstractGraphics.Alignment.Corner.TopLeft : ProcessUtils.CommandTemplate(
                r'x={{{X}}}:y={{{Y}}}',
            ),
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
                'formatter' : lambda x: int(x)
            },
            'height' : {
                'label' : 'height',
                'formatter' : lambda x: int(x)
            },
            'avg_frame_rate' : {
                'label' : 'fps',
                'formatter' : lambda x: float(eval(x))
            },
            'duration' : {
                'label' : 'duration',
                'formatter' : lambda x: TimeUtils.Time.createFromSeconds(float(x))
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
        def queryKeyframes(f_src:FileUtils.File) -> list:
            '''
            Get a list of all key-frame(s).
            '''

            # Fetch, and extract info from result.
            result = INTERNAL_VideoProcessing.FFMPEGWrapper.queryInfo(f_src, 'QueryKeyframes')
            result = StringUtils.Normalize.asSentence(result)
            resultList = result.split(' ')
            
            keyframes = []
            for resultItem in resultList:
                floatAsString = resultItem.split(',')[0]
                try:
                    floatValue = Validation.asFloat(floatAsString)
                except:
                    continue
                keyframes.append(TimeUtils.Time.createFromSeconds(floatValue))
            
            return keyframes

        @staticmethod
        def formatThumbnailTimestampAttributes(command:ProcessUtils.CommandTemplate.Formatter, timestampAttribs:ThumbnailTimestampAttributes):
            if timestampAttribs is not None:
                timestampLocationFormatter = INTERNAL_VideoProcessing.FFMPEGWrapper.ThumbnailTimestampLocationTemplates[timestampAttribs.cornerAlignment].createFormatter()
                timestampLocationFormatter.assertParameter('X', str(INTERNAL_VideoProcessing.FFMPEGWrapper.ThumbnailTimestampDefaults['Offset']['X']))
                timestampLocationFormatter.assertParameter('Y', str(INTERNAL_VideoProcessing.FFMPEGWrapper.ThumbnailTimestampDefaults['Offset']['Y']))
                command.assertSection('timestamp', params={
                    'location' : str(timestampLocationFormatter),
                    'text-size' : str(INTERNAL_VideoProcessing.FFMPEGWrapper.ThumbnailTimestampDefaults['TextSize']),
                    'text-color' : '#' + str(timestampAttribs.textColor),
                    'font-path' : str(INTERNAL_VideoProcessing.FFMPEGWrapper.ThumbnailTimestampDefaults['FontFile'])
                })
            else:
                command.excludeSection('timestamp')

        @staticmethod
        def generateThumbnail(f_src:FileUtils.File, f_dst:FileUtils.File, time:TimeUtils.Time, timestampAttribs:ThumbnailTimestampAttributes):
            '''
            Generate thumbnail at a specific timestamp.
            '''
            
            # Format command.
            command_GenerateThumbnail = INTERNAL_VideoProcessing.FFMPEGWrapper.CommandTemplates['ThumbnailGenerate'].createFormatter()
            command_GenerateThumbnail.assertParameter('input-file', str(f_src))
            command_GenerateThumbnail.assertParameter('output-file', str(f_dst))
            command_GenerateThumbnail.assertParameter('time', str(time))
            INTERNAL_VideoProcessing.FFMPEGWrapper.formatThumbnailTimestampAttributes(command_GenerateThumbnail, timestampAttribs)
            
            proc = ProcessUtils.Process(str(command_GenerateThumbnail))
            proc.run()

        @staticmethod
        def generateThumbnails(f_src:FileUtils.File, f_dstDir:FileUtils.File, N:int, isWithTimestamp:bool, generalInfo:dict):
            '''
            Generate N thumbnails, at equidistant timestamps.
            '''
            
            captureFPS = 1 / (generalInfo['duration'].toSeconds() / N)
            
            # Format command.
            command_GenerateThumbnails = INTERNAL_VideoProcessing.FFMPEGWrapper.CommandTemplates['ThumbnailsGenerate'].createFormatter()
            command_GenerateThumbnails.assertParameter('input-file', str(f_src))
            command_GenerateThumbnails.assertParameter('output-directory', str(f_dstDir))
            command_GenerateThumbnails.assertParameter('capture-fps', f"{captureFPS:.6f}")
            
            proc = ProcessUtils.Process(str(command_GenerateThumbnails))
            proc.run()

        class VideoFilterConstructors:
            
            FilterTemplates = {
                # Filter(s)
                'SepiaTone' : ProcessUtils.CommandTemplate(r'colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131'),
                'Grayscale' : ProcessUtils.CommandTemplate(r'format=gray'),
                'Brightness' : ProcessUtils.CommandTemplate(r'eq=brightness={{{BRIGHTNESS}}}:contrast={{{CONTRAST}}}:saturation={{{SATURATION}}}'),
                'GaussianBlur' : ProcessUtils.CommandTemplate(r'gblur=sigma={{{SIGMA}}}'),
                'Sharpen' : ProcessUtils.CommandTemplate(r'unsharp=luma_msize_x={{{KERNEL-SIZE}}}:luma_msize_y={{{KERNEL-SIZE}}}:luma_amount={{{FACTOR}}}'),
                'Pixelate' : ProcessUtils.CommandTemplate(r'pixelize=width={{{PIXEL-SIZE}}}:height={{{PIXEL-SIZE}}}'),
                'Noise' : ProcessUtils.CommandTemplate(r'noise=alls={{{FACTOR}}}:allf=t+u'),
                'AddBorder' : ProcessUtils.CommandTemplate(r'pad=iw+{{{THICKNESS}}}*2:ih+{{{THICKNESS}}}*2:{{{THICKNESS}}}:{{{THICKNESS}}}:color={{{COLOR}}}'),
                'Crop' : ProcessUtils.CommandTemplate(r'crop={{{WIDTH}}}:{{{HEIGHT}}}:{{{X}}}:{{{Y}}}'), 
                'Resize' : ProcessUtils.CommandTemplate(r'scale={{{WIDTH}}}:{{{HEIGHT}}}'),
                # Transition(s)
                'FadeIn' : ProcessUtils.CommandTemplate(r'fade=t=in:st=0:d={{{DURATION}}}'),
                'FadeOut' : ProcessUtils.CommandTemplate(r"fade=t=out:st={{{OFFSET}}}:d={{{DURATION}}}"),
                # Transformation(s)
                'Rotate-90-CW' : ProcessUtils.CommandTemplate(r'transpose=1'),
                'Rotate-90-CCW' : ProcessUtils.CommandTemplate(r'transpose=2'),
                'Rotate-180' : ProcessUtils.CommandTemplate(r'hflip,vflip'),
                'MirrorVertical' : ProcessUtils.CommandTemplate(r'vflip'),
                'MirrorHorizontal' : ProcessUtils.CommandTemplate(r'hflip'),
            }
            
            @staticmethod
            def SepiaTone(modifier:Modifiers.Filters.SepiaTone, generalInfo, specificInfo):
                formatter = INTERNAL_VideoProcessing.FFMPEGWrapper.VideoFilterConstructors.FilterTemplates['SepiaTone'].createFormatter()
                return str(formatter)
            
            @staticmethod
            def Grayscale(modifier:Modifiers.Filters.Grayscale, generalInfo, specificInfo):
                formatter = INTERNAL_VideoProcessing.FFMPEGWrapper.VideoFilterConstructors.FilterTemplates['Grayscale'].createFormatter()
                return str(formatter)
            
            @staticmethod
            def Brightness(modifier:Modifiers.Filters.Brightness, generalInfo, specificInfo):
                formatter = INTERNAL_VideoProcessing.FFMPEGWrapper.VideoFilterConstructors.FilterTemplates['Brightness'].createFormatter()
                formatter.assertParameter('brightness', f"{modifier.brightness-1:.3f}")
                formatter.assertParameter('contrast', f"{modifier.contrast:.3f}")
                formatter.assertParameter('saturation', f"{modifier.saturation:.3f}")
                return str(formatter)
            
            @staticmethod
            def GaussianBlur(modifier:Modifiers.Filters.GaussianBlur, generalInfo, specificInfo):
                formatter = INTERNAL_VideoProcessing.FFMPEGWrapper.VideoFilterConstructors.FilterTemplates['GaussianBlur'].createFormatter()
                # Sigma value is calibrated (Kernel-Size=3, Sigma-Value=0.5)
                sigmaValue = modifier.kernelSize * (0.5 / 3)
                formatter.assertParameter('sigma', f"{sigmaValue:.3f}")
                return str(formatter)
            
            @staticmethod
            def Sharpen(modifier:Modifiers.Filters.Sharpen, generalInfo, specificInfo):
                formatter = INTERNAL_VideoProcessing.FFMPEGWrapper.VideoFilterConstructors.FilterTemplates['Sharpen'].createFormatter()
                formatter.assertParameter('kernel-size', f"{modifier.kernelSize:d}")
                formatter.assertParameter('factor', f"{modifier.factor:.3f}")
                return str(formatter)

            @staticmethod
            def Pixelate(modifier:Modifiers.Filters.Pixelate, generalInfo, specificInfo):
                formatter = INTERNAL_VideoProcessing.FFMPEGWrapper.VideoFilterConstructors.FilterTemplates['Pixelate'].createFormatter()
                formatter.assertParameter('pixel-size', f"{modifier.factor:d}")
                return str(formatter)

            @staticmethod
            def Noise(modifier:Modifiers.Filters.Noise, generalInfo, specificInfo):
                formatter = INTERNAL_VideoProcessing.FFMPEGWrapper.VideoFilterConstructors.FilterTemplates['Noise'].createFormatter()
                normalizedFactor = round((modifier.factor - 1) * 20.0)
                formatter.assertParameter('factor', f"{normalizedFactor:d}")
                return str(formatter)
            
            @staticmethod
            def AddBorder(modifier:Modifiers.Filters.AddBorder, generalInfo, specificInfo):
                formatter = INTERNAL_VideoProcessing.FFMPEGWrapper.VideoFilterConstructors.FilterTemplates['AddBorder'].createFormatter()
                formatter.assertParameter('thickness', f"{modifier.border.thickness:d}")
                formatter.assertParameter('color', '0x' + modifier.border.color.asHEX())
                return str(formatter)
            
            @staticmethod
            def Crop(modifier:Modifiers.Filters.Crop, generalInfo, specificInfo):
                formatter = INTERNAL_VideoProcessing.FFMPEGWrapper.VideoFilterConstructors.FilterTemplates['Crop'].createFormatter()
                
                x = modifier.topLeft.x - 1
                y = modifier.topLeft.y - 1
                width = modifier.bottomRight.x - modifier.topLeft.x + 1
                height = modifier.bottomRight.y - modifier.topLeft.y + 1
                
                formatter.assertParameter('width', str(width))
                formatter.assertParameter('height', str(height))
                formatter.assertParameter('x', str(x))
                formatter.assertParameter('y', str(y))
                
                return str(formatter)
            
            @staticmethod
            def Resize(modifier:Modifiers.Filters.Resize, generalInfo, specificInfo):
                formatter = INTERNAL_VideoProcessing.FFMPEGWrapper.VideoFilterConstructors.FilterTemplates['Resize'].createFormatter()
                formatter.assertParameter('width', str(modifier.width))
                formatter.assertParameter('height', str(modifier.height))
                return str(formatter)

            @staticmethod
            def FadeIn(modifier:Modifiers.Transitions.FadeIn, generalInfo, specificInfo):
                formatter = INTERNAL_VideoProcessing.FFMPEGWrapper.VideoFilterConstructors.FilterTemplates['FadeIn'].createFormatter()
                durationInSeconds = modifier.duration.toSeconds()
                formatter.assertParameter('duration', f"{durationInSeconds:.3f}")
                return str(formatter)
            
            @staticmethod
            def FadeOut(modifier:Modifiers.Transitions.FadeOut, generalInfo, specificInfo):
                formatter = INTERNAL_VideoProcessing.FFMPEGWrapper.VideoFilterConstructors.FilterTemplates['FadeOut'].createFormatter()
                
                offsetTime:TimeUtils.Time = specificInfo['duration'] - modifier.duration
                offsetInSeconds = offsetTime.toSeconds()
                durationInSeconds = modifier.duration.toSeconds()
                
                formatter.assertParameter('offset', f"{offsetInSeconds:.3f}")
                formatter.assertParameter('duration', f"{durationInSeconds:.3f}")
                
                return str(formatter)
            
            Degrees2FilterTemplateName = {
                90 : 'Rotate-90-CW',
                270 : 'Rotate-90-CCW',
                180 : 'Rotate-180',
            }
    
            @staticmethod
            def Rotate(modifier:Modifiers.Transformations.Rotate, generalInfo, specificInfo):
                
                # ? Validate degree(s).
                degrees = int(modifier.rotation)
                if degrees % 90 != 0:
                    raise ExceptionUtils.ValidationError(f'Rotation must be a 90-degree(s) multiple. {degrees:d} given.')
                
                # ? Acquire and format filter.
                filterTemplateName = INTERNAL_VideoProcessing.FFMPEGWrapper.VideoFilterConstructors.Degrees2FilterTemplateName[degrees]
                formatter = INTERNAL_VideoProcessing.FFMPEGWrapper.VideoFilterConstructors.FilterTemplates[filterTemplateName].createFormatter()
                return str(formatter)

            Mirror2FilterTemplateName = {
                AbstractGraphics.Mirror.Vertical : 'MirrorVertical',
                AbstractGraphics.Mirror.Horizontal: 'MirrorHorizontal',
            }

            @staticmethod
            def Mirror(modifier:Modifiers.Transformations.Mirror, generalInfo, specificInfo):
                
                # ? Acquire and format filter.
                filterTemplateName = INTERNAL_VideoProcessing.FFMPEGWrapper.VideoFilterConstructors.Mirror2FilterTemplateName[modifier.mirror]
                formatter = INTERNAL_VideoProcessing.FFMPEGWrapper.VideoFilterConstructors.FilterTemplates[filterTemplateName].createFormatter()
                return str(formatter)
    
        ModifierToVideoFilter = {
            # Filter(s)
            Modifiers.Filters.SepiaTone : VideoFilterConstructors.SepiaTone,
            Modifiers.Filters.Grayscale : VideoFilterConstructors.Grayscale,
            Modifiers.Filters.Brightness : VideoFilterConstructors.Brightness,
            Modifiers.Filters.GaussianBlur : VideoFilterConstructors.GaussianBlur,
            Modifiers.Filters.Sharpen : VideoFilterConstructors.Sharpen,
            Modifiers.Filters.Pixelate : VideoFilterConstructors.Pixelate,
            Modifiers.Filters.Noise : VideoFilterConstructors.Noise,
            Modifiers.Filters.AddBorder : VideoFilterConstructors.AddBorder,
            Modifiers.Filters.Crop : VideoFilterConstructors.Crop,
            Modifiers.Filters.Resize : VideoFilterConstructors.Resize,
            # Transition(s)
            Modifiers.Transitions.FadeIn : VideoFilterConstructors.FadeIn,
            Modifiers.Transitions.FadeOut : VideoFilterConstructors.FadeOut,
            # Transformation(s)
            Modifiers.Transformations.Rotate : VideoFilterConstructors.Rotate,
            Modifiers.Transformations.Mirror : VideoFilterConstructors.Mirror,
        }

        @staticmethod
        def deriveVideoFilters(modifiers, generalInfo, specificInfo):
            filters = []
            for modifier in modifiers:
                filterConstructor = INTERNAL_VideoProcessing.FFMPEGWrapper.ModifierToVideoFilter[type(modifier)]
                filters.append(filterConstructor(modifier, generalInfo, specificInfo))
            return ','.join(filters)

        class AudioFilterConstructors:
            
            FilterTemplates = {
                # Transition(s)
                'FadeIn' : ProcessUtils.CommandTemplate(r'afade=t=in:st=0:d={{{DURATION}}}'),
                'FadeOut' : ProcessUtils.CommandTemplate(r"afade=t=out:st={{{OFFSET}}}:d={{{DURATION}}}"),
            }

            @staticmethod
            def FadeIn(modifier:AudioModifiers.Transitions.FadeIn, generalInfo, specificInfo):
                formatter = INTERNAL_VideoProcessing.FFMPEGWrapper.AudioFilterConstructors.FilterTemplates['FadeIn'].createFormatter()
                durationInSeconds = modifier.duration.toSeconds()
                formatter.assertParameter('duration', f"{durationInSeconds:.3f}")
                return str(formatter)
            
            @staticmethod
            def FadeOut(modifier:AudioModifiers.Transitions.FadeOut, generalInfo, specificInfo):
                formatter = INTERNAL_VideoProcessing.FFMPEGWrapper.AudioFilterConstructors.FilterTemplates['FadeOut'].createFormatter()
                
                offsetTime:TimeUtils.Time = specificInfo['duration'] - modifier.duration
                offsetInSeconds = offsetTime.toSeconds()
                durationInSeconds = modifier.duration.toSeconds()
                
                formatter.assertParameter('offset', f"{offsetInSeconds:.3f}")
                formatter.assertParameter('duration', f"{durationInSeconds:.3f}")
                
                return str(formatter)
    
        ModifierToAudioFilter = {
            # Transition(s)
            AudioModifiers.Transitions.FadeIn : AudioFilterConstructors.FadeIn,
            AudioModifiers.Transitions.FadeOut : AudioFilterConstructors.FadeOut,
        }
        
        @staticmethod
        def deriveAudioFilters(modifiers, generalInfo, specificInfo):
            filters = []
            for modifier in modifiers:
                filterConstructor = INTERNAL_VideoProcessing.FFMPEGWrapper.ModifierToAudioFilter[type(modifier)]
                filters.append(filterConstructor(modifier, generalInfo, specificInfo))
            return ','.join(filters)
        
        @staticmethod
        def processTrimAction(f_src:FileUtils.File, f_tmpBase:FileUtils.File, trimAction:Actions.Trim, generalInfo:dict) -> list:
            commandList = []
            
            if (trimAction.isNearestKeyframe):
                command_VideoTrim = INTERNAL_VideoProcessing.FFMPEGWrapper.CommandTemplates['VideoTrimNearestKeyframe'].createFormatter()
            else:
                command_VideoTrim = INTERNAL_VideoProcessing.FFMPEGWrapper.CommandTemplates['VideoTrim'].createFormatter()

            command_VideoTrim.assertParameter('input-file', str(f_src))
            
            if not(trimAction.startTime is None):
                startTime = trimAction.startTime
                command_VideoTrim.assertSection('start-time', {'time' : startTime.toString(precision=3)})
            else:
                startTime = TimeUtils.Time(0)
                command_VideoTrim.excludeSection('start-time')
                
            if not(trimAction.endTime is None):
                duration = trimAction.endTime - startTime
                command_VideoTrim.assertSection('duration', {'time' : duration.toString(precision=3)})
            else:
                duration = generalInfo['duration'] - startTime
                command_VideoTrim.excludeSection('duration')
            
            # If trimming is not at nearest key-frame, then it is possible to specify filter(s), and CRF value.
            if not (trimAction.isNearestKeyframe):
                # Deriving CRF value.
                command_VideoTrim.assertParameter('crf', str(trimAction.CRF))
                
                # Processing modifier(s).
                modifiers = [modifier for modifier in trimAction.modifiers if issubclass(type(modifier), INTERNAL_Utils.Modifier)]
                audioModifiers = [modifier for modifier in trimAction.modifiers if issubclass(type(modifier), INTERNAL_Utils.AudioModifier)]
                
                # Used to pass specific info (i.e., info specific to this cut of the video).
                specificInfo = {
                    'duration' : duration
                }
                
                videoFilters:str = INTERNAL_VideoProcessing.FFMPEGWrapper.deriveVideoFilters(modifiers, generalInfo, specificInfo)
                audioFilters:str = INTERNAL_VideoProcessing.FFMPEGWrapper.deriveAudioFilters(audioModifiers, generalInfo, specificInfo)
                
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

            # Check if trim-action(s) demand re-encoding. In this case, (force-)use '.mp4' extension as output.
            isNearestKeyframe = False
            for trimAction in joinAction.trimActions:
                isNearestKeyframe = isNearestKeyframe or trimAction.isNearestKeyframe
            if not isNearestKeyframe:
                f_tmpBase = FileUtils.File(FileUtils.File.Utils.Path.modifyName(str(f_tmpBase), extension='mp4'))

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
        
        # 'Trim' action not included, since it is technically a sub-action.
        ActionToProcessor = {
            Actions.Join : processJoinAction,
            Actions.GIF : processGIFAction,
        }
        
        @staticmethod
        def processActions(f_src:FileUtils.File, f_dst:FileUtils.File, actions:list, generalInfo:dict):
            f_tmpDir = FileUtils.File.Utils.getTemporaryDirectory()
            f_tmpBase = f_tmpDir.traverseDirectory(f_src.getName())
            commandList = []
            
            f_finalTmpDst = f_src
            for action in actions:
                actionProcessor = INTERNAL_VideoProcessing.FFMPEGWrapper.ActionToProcessor[type(action)]
                newCommandList, f_finalTmpDst = actionProcessor(f_finalTmpDst, f_tmpBase, action, generalInfo)
                commandList += newCommandList
            
            try:
                # Execute command-list.
                INTERNAL_VideoProcessing.FFMPEGWrapper.executeCommands(commandList)
                
                # Copy into (actual) destination, and delete temporary directory.
                FileUtils.File.Utils.copy(f_finalTmpDst, f_dst)
                FileUtils.File.Utils.recycle(f_tmpDir)
                
            except ExceptionUtils.BackendError as e:
                # Delete temporary directory, before propagating error.
                FileUtils.File.Utils.recycle(f_tmpDir)
                raise
            
        @staticmethod
        def executeCommands(commandList):
            for command in commandList:
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

    def getDuration(self) -> TimeUtils.Time:
        return self.generalInfo['duration']

    def getKeyframes(self):
        '''
        Get a list of all key-frame(s).
        '''
        return INTERNAL_VideoProcessing.FFMPEGWrapper.queryKeyframes(self.f_src)

    def getDimensions(self):
        '''
        Returns a '(width, height)' tuple.
        '''
        return (self.generalInfo['width'], self.generalInfo['height'])
        
    def registerAction(self, action):
        '''
        Register an action.
        
        Note,
        - Only a single 'Join' (mandatory), which consists of one or more 'Trim' action(s), and a 'GIF' (optional) are supported.
        - Modifier(s) may be applied to 'Trim' action(s).
        - All action(s) and modifier(s) are order-sensitive.
        '''
        self.actions.append(action)
    
    def saveAs(self, f_dst:FileUtils.File):
        '''
        Processes registered action(s), and save end-file.
        '''
        if f_dst.isExists():
            raise ExceptionUtils.ValidationError('Destination file must not exist.')
        INTERNAL_VideoProcessing.FFMPEGWrapper.processActions(self.f_src, f_dst, self.actions, self.generalInfo)
    
    def clearActions(self):
        '''
        Clears all registered action(s)
        '''
        self.actions.clear()
    
    def generateThumbnails(self, f_dstDir:FileUtils.File, N:int):
        '''
        Generate thumb-nails at equi-distant interval(s).
        '''
        if f_dstDir.isExists():
            raise ExceptionUtils.ValidationError('Destination directory must not exist.')
        
        # ? Create directory.
        f_dstDir.makeDirectory()
        
        # ? Generate thumbnail(s).
        INTERNAL_VideoProcessing.FFMPEGWrapper.generateThumbnails(self.f_src, f_dstDir, N, self.generalInfo)

    def generateThumbnail(self, f_dst:FileUtils.File, time:TimeUtils.Time, timestampAttribs:ThumbnailTimestampAttributes=None):
        '''
        Generate thumb-nail at a specific time-stamp.
        '''
        if f_dst.isExists():
            raise ExceptionUtils.ValidationError('Destination file must not exist.')

        # ? Generate thumbnail.
        INTERNAL_VideoProcessing.FFMPEGWrapper.generateThumbnail(self.f_src, f_dst, time, timestampAttribs)
    
    class Utils:
        
        SupportedExtensions = [
            'mp4',
            'mkv',
            'wmv',
            'mov',
            'avi',
            'webm',
            'flv',
            'mpeg',
            'rm', 'rmvb',
        ]
        
        @staticmethod
        def isVideo(f:FileUtils.File):
            '''
            Check if file is a video.
            
            Note, currently only 'mp4' format is supported.
            '''
            return f.getExtension() in Video.Utils.SupportedExtensions
