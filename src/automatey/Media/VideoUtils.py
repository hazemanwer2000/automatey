# External libraries
import cv2
import PIL
import PIL.Image
import PIL.ImageOps
import PIL.ImageEnhance
import PIL.ImageFilter
import imageio
import numpy as np

# Internal libraries
import automatey.OS.FileUtils as FileUtils
import automatey.Base.TimeUtils as TimeUtils
import automatey.OS.ProcessUtils as ProcessUtils
import automatey.Utils.StringUtils as StringUtils
import automatey.Base.ExceptionUtils as ExceptionUtils

from pprint import pprint 

class Color:
    '''
    Representation of a color.
    '''
    def __init__(self, R:int, G:int, B:int):
        self.R = R
        self.G = G
        self.B = B
        
    def asRGBTuple(self):
        return (self.R, self.G, self.B)
    
    def asBGRTuple(self):
        return (self.B, self.G, self.R)

class Colors:
    '''
    Pre-defined set of colors.
    '''
    Black = Color(0, 0, 0)
    White = Color(255, 255, 255)

class Point:
    '''
    Representation of a point.
    '''
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Border:
    '''
    Representation of a border.
    '''
    def __init__(self, thickness:int, color:Color):
        self.thickness = thickness
        self.color = color
    
class INTERNAL_Drawable:
    pass

class INTERNAL_Shape(INTERNAL_Drawable):
    '''
    (Abstract) Representation of a shape.
    '''
    def __init__(self, fillColor:Color, border:Border):
        self.fillColor = fillColor
        self.border = border
        if (self.border == None):
            self.border = Border(0, self.fillColor)

class INTERNAL_Line(INTERNAL_Drawable):
    '''
    (Abstract) Representation of a line.
    '''
    def __init__(self, thickness:int, color:Color):
        self.thickness = thickness
        self.color = color

class Drawables:

    class Rectangle(INTERNAL_Shape):
        '''
        Representation of a rectangle.
        '''
        def __init__(self, fillColor:Color, border:Border, topLeft:Point, bottomRight:Point):
            INTERNAL_Shape.__init__(self, fillColor=fillColor, border=border)
            self.topLeft = topLeft
            self.bottomRight = bottomRight

    class RectangularLine(INTERNAL_Line):
        '''
        Representation of a rectangular line.
        '''
        def __init__(self, thickness:int, color:Color, topLeft:Point, bottomRight:Point):
            INTERNAL_Line.__init__(self, thickness, color)
            self.topLeft = topLeft
            self.bottomRight = bottomRight

class INTERNAL_FrameProcessing:
    '''
    Contains wrapper(s) for different libraries, that process frame(s).
    '''

    class PillowWrapper:
        
        @staticmethod
        def brightnessContrast(imgHandler, brightness=1.0, contrast=1.0):
            '''
            Adjust brightness and contrast.
            
            Value(s) are factor(s) (i.e., '1.0' has no effect).
            '''
            brightness = float(brightness)
            contrast = float(contrast)

            if brightness != 1.0:
                imgHandler = PIL.ImageEnhance.Brightness(imgHandler).enhance(brightness)
            if contrast != 1.0:
                imgHandler = PIL.ImageEnhance.Contrast(imgHandler).enhance(contrast)
                
            return imgHandler

        @staticmethod
        def sharpen(imgHandler, factor):
            '''
            Sharpen an image.
            
            Value(s) are factor(s) (i.e., '1.0' has no effect).
            '''
            factor = float(factor)
            
            if factor != 1.0:
                imgHandler = PIL.ImageEnhance.Sharpness(imgHandler).enhance(factor)
                
            return imgHandler

        @staticmethod
        def findEdges(imgHandler):
            '''
            Finds and leaves only edges.
            '''
            imgHandler = imgHandler.filter(PIL.ImageFilter.FIND_EDGES)
            return imgHandler

        @staticmethod
        def emboss(imgHandler):
            '''
            Finds and leaves only edges.
            '''
            imgHandler = imgHandler.filter(PIL.ImageFilter.EMBOSS)
            return imgHandler

        @staticmethod
        def addBorder(imgHandler, border:Border):
            '''
            Adds a border.
            '''
            imgHandler = PIL.ImageOps.expand(imgHandler, border=border.thickness, fill=border.color.asRGBTuple())
            return imgHandler

    class CV2Wrapper:
        
        @staticmethod
        def createFromFile(f:FileUtils.File):
            return cv2.imread(str(f))
        
        @staticmethod
        def getDimensions(imgHandler):
            '''
            Returns a '(width, height)' tuple.
            '''
            shape  = imgHandler.shape
            return (shape[1], shape[0])

        @staticmethod
        def resize(imgHandler, width, height):
            '''
            Resize an image, given '(W, H)'.
            
            If either set to '-1', aspect ratio is preserved.
            '''
            orig_w, orig_h = INTERNAL_FrameProcessing.CV2Wrapper.getDimensions(imgHandler)
            aspectRatio = orig_w / orig_h
            
            if width == -1:
                width = int(height * aspectRatio)
            elif height == -1:
                height = int(width / aspectRatio)
            
            interpolation = cv2.INTER_AREA
            # Case: Up-scaling.
            if (width > orig_w) or (height > orig_h):
                interpolation = cv2.INTER_LANCZOS4

            imgHandler = cv2.resize(imgHandler, (width, height), interpolation=interpolation)
            return imgHandler

        @staticmethod
        def grayscale(imgHandler):
            '''
            Convert into grayscale.
            '''
            if len(imgHandler.shape) > 2:
                imgHandler = cv2.cvtColor(imgHandler, cv2.COLOR_BGR2GRAY)
            return imgHandler

        @staticmethod
        def blackWhite(imgHandler, threshold=0.5, kernelSize=0):
            '''
            Convert grayscale into black-and-white.
            
            Threshold range is (0, 1). A lower threshold leads to more white regions.
            
            Kernel is used for Erosion-Dilation procedure. If 0 in size, procedure does not occur.
            '''
            _, imgHandler = cv2.threshold(imgHandler, int(threshold*255), 255, cv2.THRESH_BINARY)
            if kernelSize > 0:
                kernel = (kernelSize, kernelSize)
                imgHandler = cv2.morphologyEx(imgHandler, cv2.MORPH_OPEN, kernel)
            return imgHandler

        @staticmethod
        def invert(imgHandler):
            '''
            Invert value(s).
            '''
            imgHandler = cv2.bitwise_not(imgHandler)
            return imgHandler

        sepiaToneMatrix = np.array([[0.272, 0.534, 0.131],
                                    [0.349, 0.686, 0.168],
                                    [0.393, 0.769, 0.189]])

        @staticmethod
        def sepiaTone(imgHandler):
            '''
            Applies sepia-tone (i.e., a yellow-ish, vintage effect).
            '''
            imgHandler = cv2.transform(imgHandler, INTERNAL_FrameProcessing.CV2Wrapper.sepiaToneMatrix)
            return imgHandler

        @staticmethod
        def gaussianBlur(imgHandler, kernelSize):
            '''
            Applies gaussian blur.
            
            Kernel-size must be odd.
            '''
            imgHandler = cv2.GaussianBlur(imgHandler, (kernelSize, kernelSize), sigmaX=0)
            return imgHandler
            
        @staticmethod
        def medianBlur(imgHandler, kernelSize):
            '''
            Applies median blur.
            
            Kernel-size must be odd.
            '''
            imgHandler = cv2.medianBlur(imgHandler, ksize=kernelSize)
            return imgHandler

        @staticmethod
        def bilateralFilter(imgHandler, kernelSize):
            '''
            Applies bilateral filter.
            
            Kernel-size must be odd.
            '''
            imgHandler = cv2.bilateralFilter(imgHandler, d=kernelSize, sigmaColor=75, sigmaSpace=75)
            return imgHandler

        @staticmethod
        def pixelate(imgHandler, factor):
            '''
            Pixelate.
            
            Value(s) are factor(s) (i.e., '1.0' has no effect).
            '''
            factor = 1 / factor
            orig_w, orig_h = INTERNAL_FrameProcessing.CV2Wrapper.getDimensions(imgHandler)
            width = int(orig_w * factor)
            height = int(orig_h * factor)
            imgHandler = cv2.resize(imgHandler, (width, height), interpolation=cv2.INTER_AREA)
            imgHandler = cv2.resize(imgHandler, (orig_w, orig_h), interpolation=cv2.INTER_NEAREST)
            return imgHandler

        @staticmethod
        def crop(imgHandler, topLeft:Point, bottomRight:Point):
            '''
            Crop.
            
            Note that (1, 1) specifies the pixel at the top-left corner.
            '''
            x1 = topLeft.x - 1
            x2 = bottomRight.x
            
            y1 = topLeft.y - 1
            y2 = bottomRight.y
            
            imgHandler = imgHandler[y1:y2, x1:x2]
            return imgHandler
        
        @staticmethod
        def overlayRectangle(imgHandler, rectangle:Drawables.Rectangle):
            x1 = rectangle.topLeft.x - 1
            x2 = rectangle.bottomRight.x - 1
            
            y1 = rectangle.topLeft.y - 1
            y2 = rectangle.bottomRight.y - 1
            
            imgHandler = cv2.rectangle(imgHandler, (x1, y1), (x2, y2), rectangle.border.color.asBGRTuple(), -1)
            imgHandler = cv2.rectangle(imgHandler, 
                                       (x1+rectangle.border.thickness, y1+rectangle.border.thickness),
                                       (x2-rectangle.border.thickness, y2-rectangle.border.thickness),
                                       rectangle.fillColor.asBGRTuple(), -1)
            return imgHandler
        
        @staticmethod
        def overlayRectangularLine(imgHandler, rectangularLine:Drawables.RectangularLine):
            x1 = rectangularLine.topLeft.x - 1
            x2 = rectangularLine.bottomRight.x - 1
            
            y1 = rectangularLine.topLeft.y - 1
            y2 = rectangularLine.bottomRight.y - 1
            
            imgHandler = cv2.rectangle(imgHandler, (x1, y1), (x2, y2), rectangularLine.color.asBGRTuple(), rectangularLine.thickness)
            return imgHandler
        
        @staticmethod
        def overlayDrawable(imgHandler, shape):
            '''
            Add a drawable (e.g., Rectangle).
            '''
            fcnDict = {
                Drawables.Rectangle: INTERNAL_FrameProcessing.CV2Wrapper.overlayRectangle,
                Drawables.RectangularLine: INTERNAL_FrameProcessing.CV2Wrapper.overlayRectangularLine,
            }
            return fcnDict[type(shape)](imgHandler, shape)

        @staticmethod
        def saveAs(imgHandler, f:FileUtils.File):
            '''
            Save image, into a file.
            '''
            cv2.imwrite(str(f), imgHandler)

class INTERNAL_FrameConversion:
    '''
    Contains frame-conversion method(s) between the different frame processor(s).
    '''

    @staticmethod
    def ImageIOToPillow(imgHandler):
        return PIL.Image.fromarray(imgHandler)
    
    @staticmethod
    def PillowToImageIO(imgHandler):
        return np.array(imgHandler)

    @staticmethod
    def CV2ToPillow(imgHandler):
        return PIL.Image.fromarray(cv2.cvtColor(imgHandler, cv2.COLOR_BGR2RGB))
    
    @staticmethod
    def PillowToCV2(imgHandler):
        return cv2.cvtColor(np.array(imgHandler), cv2.COLOR_RGB2BGR)
    
    @staticmethod
    def ImageIOToCV2(imgHandler):
        return cv2.cvtColor(imgHandler, cv2.COLOR_RGB2BGR)
    
    @staticmethod
    def CV2ToImageIO(imgHandler):
        return cv2.cvtColor(imgHandler, cv2.COLOR_BGR2RGB)

class INTERNAL_Action:
    pass

class INTERNAL_ActionFilter(INTERNAL_Action):
    '''
    All filter(s).
    '''
    pass

class INTERNAL_ActionTransition(INTERNAL_Action):
    '''
    All start/end transition(s).
    '''
    
    def __init__(self, durationInSeconds, isStartTransition, isEndTransition):
        self.durationInSeconds = durationInSeconds
        self.isStartTransition = isStartTransition
        self.isEndTransition = isEndTransition

class INTERNAL_ActionScalar(INTERNAL_Action):
    '''
    All scaling operation(s), including resizing and cropping.
    '''
    pass

class Actions:
    
    class Trim(INTERNAL_Action):
        '''
        Trim sequence.
        '''
        
        def __init__(self, startTime:TimeUtils.Time, endTime:TimeUtils.Time, isNearestKeyframe:bool=False, subActions=None):
            self.startTime = startTime
            self.endTime = endTime
            self.isNearestKeyframe = isNearestKeyframe
            self.subActions = subActions

    class Join(INTERNAL_Action):
        '''
        Join sequence(s).
        '''
        
        def __init__(self, *trimActions):
            self.trimActions = trimActions
            
    class GIF(INTERNAL_Action):
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
            joinAction:Actions.Join = [action for action in actions if isinstance(action, Actions.Join)][0]
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
            GIFActionList:Actions.GIF = [action for action in actions if isinstance(action, Actions.GIF)]
            if (len(GIFActionList) > 0):
                f_gifTmpDst = FileUtils.File(
                    FileUtils.File.Utils.Path.modifyName(
                        FileUtils.File.Utils.Path.randomizeName(str(f_tmpBase)),
                        extension='gif'
                    )
                )
                commandList += INTERNAL_VideoProcessing.FFMPEGWrapper.processGIFAction(f_joinTmpDst, f_gifTmpDst, GIFActionList[0], generalInfo)
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

# Uses 'CV2' as its format
class Image:
    '''
    Image handler.
    '''

    def __init__(self, f:FileUtils.File):
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.createFromFile(f)

    def getDimensions(self):
        '''
        Returns a '(width, height)' tuple.
        '''
        return INTERNAL_FrameProcessing.CV2Wrapper.getDimensions(self.imgHandler)

    def resize(self, width, height):
        '''
        Resize an image, given '(W, H)'.
        
        If either set to '-1', aspect ratio is preserved.
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.resize(self.imgHandler, width, height)

    def grayscale(self):
        '''
        Convert into grayscale.
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.grayscale(self.imgHandler)
        
    def blackWhite(self, threshold=0.5, kernelSize=0):
        '''
        Convert grayscale into black-and-white.
        
        Threshold range is (0, 1). A lower threshold leads to more white regions.
        
        Kernel is used for Erosion-Dilation procedure. If 0 in size, procedure does not occur.
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.blackWhite(self.imgHandler, threshold, kernelSize)

    def invert(self):
        '''
        Invert value(s).
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.invert(self.imgHandler)

    def sepiaTone(self):
        '''
        Applies sepia-tone (i.e., a yellow-ish, vintage effect).
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.sepiaTone(self.imgHandler)

    def brightnessContrast(self, brightness=1.0, contrast=1.0):
        '''
        Adjust brightness and contrast.
        
        Value(s) are factor(s) (i.e., '1.0' has no effect).
        '''
        pillowImgHandler = INTERNAL_FrameConversion.CV2ToPillow(self.imgHandler)
        pillowImgHandler = INTERNAL_FrameProcessing.PillowWrapper.brightnessContrast(pillowImgHandler, brightness, contrast)
        self.imgHandler = INTERNAL_FrameConversion.PillowToCV2(pillowImgHandler)

    def gaussianBlur(self, kernelSize):
        '''
        Applies gaussian blur.
        
        Kernel-size must be odd.
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.gaussianBlur(self.imgHandler, kernelSize)
        
    def medianBlur(self, kernelSize):
        '''
        Applies median blur.
        
        Kernel-size must be odd.
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.medianBlur(self.imgHandler, kernelSize)

    def bilateralFilter(self, kernelSize):
        '''
        Applies bilateral filter.
        
        Kernel-size must be odd.
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.bilateralFilter(self.imgHandler, kernelSize)

    def sharpen(self, factor):
        '''
        Sharpen an image.
        
        Value(s) are factor(s) (i.e., '1.0' has no effect).
        '''
        pillowImgHandler = INTERNAL_FrameConversion.CV2ToPillow(self.imgHandler)
        pillowImgHandler = INTERNAL_FrameProcessing.PillowWrapper.sharpen(pillowImgHandler, factor)
        self.imgHandler = INTERNAL_FrameConversion.PillowToCV2(pillowImgHandler)
    
    def findEdges(self):
        '''
        Finds and leaves only edges.
        '''
        pillowImgHandler = INTERNAL_FrameConversion.CV2ToPillow(self.imgHandler)
        pillowImgHandler = INTERNAL_FrameProcessing.PillowWrapper.findEdges(pillowImgHandler)
        self.imgHandler = INTERNAL_FrameConversion.PillowToCV2(pillowImgHandler)

    def emboss(self):
        '''
        Emboss.
        '''
        pillowImgHandler = INTERNAL_FrameConversion.CV2ToPillow(self.imgHandler)
        pillowImgHandler = INTERNAL_FrameProcessing.PillowWrapper.emboss(pillowImgHandler)
        self.imgHandler = INTERNAL_FrameConversion.PillowToCV2(pillowImgHandler)

    def pixelate(self, factor):
        '''
        Pixelate.
        
        Value(s) are factor(s) (i.e., '1.0' has no effect).
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.pixelate(self.imgHandler, factor)

    def addBorder(self, border:Border):
        '''
        Adds a border.
        '''
        pillowImgHandler = INTERNAL_FrameConversion.CV2ToPillow(self.imgHandler)
        pillowImgHandler = INTERNAL_FrameProcessing.PillowWrapper.addBorder(pillowImgHandler, border)
        self.imgHandler = INTERNAL_FrameConversion.PillowToCV2(pillowImgHandler)
    
    def crop(self, topLeft:Point, bottomRight:Point):
        '''
        Crop.
        
        Note that (1, 1) specifies the pixel at the top-left corner.
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.crop(self.imgHandler, topLeft, bottomRight)
        
    def overlayDrawable(self, shape):
        '''
        Add a drawable (e.g., Rectangle).
        '''
        self.imgHandler = INTERNAL_FrameProcessing.CV2Wrapper.overlayDrawable(self.imgHandler, shape)
    
    def saveAs(self, f:FileUtils.File):
        '''
        Save image, into a file.
        '''
        INTERNAL_FrameProcessing.CV2Wrapper.saveAs(self.imgHandler, f)

    class Utils:
        
        SupportedExtensions = ['jpeg', 'jpg', 'png']
        
        @staticmethod
        def isImage(f:FileUtils.File):
            return f.getExtension() in Image.Utils.SupportedExtensions

# Uses 'ImageIO' as its format (Like CV2's, but in 'RGB' instead of 'BGR')
class GIF:
    '''
    GIF-handler.
    '''

    def __init__(self, f:FileUtils.File):
        reader = imageio.get_reader(str(f))
        self.frames = []
        totalDuration = 0
        for i, frame in enumerate(reader):
            meta = reader.get_meta_data(i)
            self.frames.append(frame)
            frameDuration = meta.get("duration", 0)
            totalDuration += frameDuration
        self.fps = len(self.frames) / (totalDuration / 1000)
    
    def getFrameCount(self):
        '''
        Get frame count.
        '''
        return len(self.frames)
    
    def getFPS(self):
        '''
        Get FPS.
        '''
        return self.fps

    def selectFrames(self, ranges):
        '''
        Select specific range(s) of frame(s).
        
        Note that backward range(s) are supported.
        
        Note that frame(s) are '1'-indexed.
        '''
        newFrames = []
        for _range in ranges:
            start = _range[0] - 1
            stop = _range[1] - 1
            step = -1 if (stop < start) else 1
            for i in range(start, (stop + step), step):
                copiedFrame = np.copy(self.frames[i])
                newFrames.append(copiedFrame)
        self.frames = newFrames

    def INTERNAL_CV2Applier(self, fcn, *args, **kwargs):
        for i in range(len(self.frames)):
            cv2ImgHandler = INTERNAL_FrameConversion.ImageIOToCV2(self.frames[i])
            cv2ImgHandler = fcn(cv2ImgHandler, *args, **kwargs)
            self.frames[i] = INTERNAL_FrameConversion.CV2ToImageIO(cv2ImgHandler)

    def INTERNAL_PillowApplier(self, fcn, *args, **kwargs):
        for i in range(len(self.frames)):
            pillowImgHandler = INTERNAL_FrameConversion.ImageIOToPillow(self.frames[i])
            pillowImgHandler = fcn(pillowImgHandler, *args, **kwargs)
            self.frames[i] = INTERNAL_FrameConversion.PillowToImageIO(pillowImgHandler)

    def getDimensions(self):
        '''
        Returns a '(width, height)' tuple.
        '''
        return INTERNAL_FrameProcessing.CV2Wrapper.getDimensions(self.frames[0])

    def resize(self, width, height):
        '''
        Resize an image, given '(W, H)'.
        
        If either set to '-1', aspect ratio is preserved.
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.resize, width, height)

    def grayscale(self):
        '''
        Convert into grayscale.
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.grayscale)

    def blackWhite(self, threshold=0.5, kernelSize=0):
        '''
        Convert grayscale into black-and-white.
        
        Threshold range is (0, 1). A lower threshold leads to more white regions.
        
        Kernel is used for Erosion-Dilation procedure. If 0 in size, procedure does not occur.
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.blackWhite, threshold, kernelSize)

    def invert(self):
        '''
        Invert value(s).
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.invert)

    def sepiaTone(self):
        '''
        Applies sepia-tone (i.e., a yellow-ish, vintage effect).
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.sepiaTone)

    def brightnessContrast(self, brightness=1.0, contrast=1.0):
        '''
        Adjust brightness and contrast.
        
        Value(s) are factor(s) (i.e., '1.0' has no effect).
        '''
        self.INTERNAL_PillowApplier(INTERNAL_FrameProcessing.PillowWrapper.brightnessContrast, brightness, contrast)

    def gaussianBlur(self, kernelSize):
        '''
        Applies gaussian blur.
        
        Kernel-size must be odd.
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.gaussianBlur, kernelSize)
        
    def medianBlur(self, kernelSize):
        '''
        Applies median blur.
        
        Kernel-size must be odd.
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.medianBlur, kernelSize)

    def bilateralFilter(self, kernelSize):
        '''
        Applies bilateral filter.
        
        Kernel-size must be odd.
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.bilateralFilter, kernelSize)

    def sharpen(self, factor):
        '''
        Sharpen an image.
        
        Value(s) are factor(s) (i.e., '1.0' has no effect).
        '''
        self.INTERNAL_PillowApplier(INTERNAL_FrameProcessing.PillowWrapper.sharpen, factor)
    
    def findEdges(self):
        '''
        Finds and leaves only edges.
        '''
        self.INTERNAL_PillowApplier(INTERNAL_FrameProcessing.PillowWrapper.findEdges)

    def emboss(self):
        '''
        Emboss.
        '''
        self.INTERNAL_PillowApplier(INTERNAL_FrameProcessing.PillowWrapper.emboss)

    def pixelate(self, factor):
        '''
        Pixelate.
        
        Value(s) are factor(s) (i.e., '1.0' has no effect).
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.pixelate, factor)

    def addBorder(self, border:Border):
        '''
        Adds a border.
        '''
        self.INTERNAL_PillowApplier(INTERNAL_FrameProcessing.PillowWrapper.addBorder, border)
    
    def crop(self, topLeft:Point, bottomRight:Point):
        '''
        Crop.
        
        Note that (1, 1) specifies the pixel at the top-left corner.
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.crop, topLeft, bottomRight)

    def overlayDrawable(self, shape):
        '''
        Add a drawable (e.g., Rectangle).
        '''
        self.INTERNAL_CV2Applier(INTERNAL_FrameProcessing.CV2Wrapper.overlayShape, shape)
        
    def overlayDrawablePerFrame(self, callout):
        '''
        Add a drawable (e.g., Rectangle).
        
        Callout receives the current frame index (1 to FRAME-COUNT), and returns a shape.
        '''
        # Cannot use CV2Applier, must do it manually.
        for i in range(len(self.frames)):
            cv2ImgHandler = INTERNAL_FrameConversion.ImageIOToCV2(self.frames[i])
            cv2ImgHandler = INTERNAL_FrameProcessing.CV2Wrapper.overlayDrawable(cv2ImgHandler, callout(i+1))
            self.frames[i] = INTERNAL_FrameConversion.CV2ToImageIO(cv2ImgHandler)

    def saveAs(self, f:FileUtils.File, fps=None):
        '''
        Save into file.
        '''
        if fps == None:
            fps = self.fps
        
        writer = imageio.get_writer(str(f), fps=fps)
        for frame in self.frames:
            writer.append_data(frame)
        writer.close()

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
        
    def registerAction(self, action):
        '''
        Register an action.
        
        Note,
        - Only a single 'Join' (mandatory) and a 'GIF' (optional) are supported.
        - Other action(s) may be applied to 'Trim'.
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
