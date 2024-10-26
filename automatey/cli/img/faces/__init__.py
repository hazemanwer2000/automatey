
import os
import shutil

# Note: An environment variable is introduced, to disable all 'Tensor-flow' CMD print(s).  
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import automatey.utils as ut
import automatey.cli.utils as cli_ut
import click
import time
from mtcnn import MTCNN
import cv2
import PIL
import numpy as np

#------------------------/
# [SECTION]: Enum(s)
#------------------------/

class FileType:
    VID = 'VID'
    IMG = 'IMG'
    GIF = 'GIF'

class RotationType:
    DEG_90_CW = 'DEG_90_CW'
    DEG_90_CCW = 'DEG_90_CCW'
    DEG_180 = 'DEG_180'
    DEG_0 = 'DEG_0'
    ALL = 'ALL'

#----------------------------/
# [SECTION]: Constant(s)
#----------------------------/

map_CliRotationValue2RotationType = {
    90 : RotationType.DEG_90_CW,
    -90 : RotationType.DEG_90_CCW,
    180 : RotationType.DEG_180,
    0 : RotationType.DEG_0,
    -1 : RotationType.ALL
}

cv2_map_RotateCode2ReverseRotateCode = {
    cv2.ROTATE_90_CLOCKWISE : cv2.ROTATE_90_COUNTERCLOCKWISE,
    cv2.ROTATE_90_COUNTERCLOCKWISE : cv2.ROTATE_90_CLOCKWISE,
    cv2.ROTATE_180 : cv2.ROTATE_180
}

cv2_map_RotationType2RotateCode = {
    RotationType.DEG_0 : None,
    RotationType.DEG_180 : cv2.ROTATE_180,
    RotationType.DEG_90_CW : cv2.ROTATE_90_CLOCKWISE,
    RotationType.DEG_90_CCW : cv2.ROTATE_90_COUNTERCLOCKWISE
}

detector = MTCNN()

#------------------------/
# [SECTION]: Setting(s)
#------------------------/
# RGB: Black
color_fill = (0, 0, 0)

# RGB: Dark-Red
color_border = (179, 0, 0)

thickness_border_thin = 1
thickness_border_thick = 2

isOverrideImageExtension = True
overridingImageExtension = '.png'

imageExtensionList = ['.jpg', '.jpeg', '.png']
videoExtensionList = ['.mp4']

#-------------------------------/
# [SECTION]: Global variable(s)
#-------------------------------/

requiredRotation = None
requiredRotateCodes = None
isOutlineOnly = False
isCopyOriginal = False
thicknessBorder = 0

#----------------------/
# [SECTION]: Helper(s)
#----------------------/

def getFileType(file_path):
    _, file_ext = os.path.splitext(file_path)
    file_type = None

    if file_ext in imageExtensionList:
        file_type = FileType.IMG
    elif file_ext in videoExtensionList:
        file_type = FileType.VID
    elif file_ext == '.gif':
        file_type = FileType.GIF

    return file_type, file_ext

def processImage(img_rgb, rotate_code=None):
    if rotate_code != None:
        img_rgb = cv2.rotate(img_rgb, rotate_code)

    faces = detector.detect_faces(img_rgb)
    is_faces_detected = (len(faces) != 0)

    for face in faces:
        x, y, width, height = face['box']
        if not isOutlineOnly:
            cv2.rectangle(img_rgb, (x, y), (x + width, y + height), color_fill, -1)
        cv2.rectangle(img_rgb, (x, y), (x + width, y + height), color_border, thicknessBorder)

    if rotate_code != None:
        img_rgb = cv2.rotate(img_rgb, cv2_map_RotateCode2ReverseRotateCode[rotate_code])

    return img_rgb, is_faces_detected

def generateOutputImage(inputFilePath, outputFilePath):
    img = cv2.imread(inputFilePath)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    for rotateCode in requiredRotateCodes:
        modifiedOutputFilePath = ut.FileManagement.Path.getNextIterativePath(outputFilePath, is_file=True)
        processed_img_rgb, is_faces_detected = processImage(img_rgb, rotateCode)
        if is_faces_detected:
            cv2.imwrite(modifiedOutputFilePath, cv2.cvtColor(processed_img_rgb, cv2.COLOR_RGB2BGR))

def generateOutputVideo(inputFilePath, outputFilePath):
    pass

def generateOutputGIF(inputFilePath, outputFilePath):

    with PIL.Image.open(inputFilePath) as img_gif:

        for rotateCode in requiredRotateCodes:

            # [ACTION]: Loop on all frames.
            frames = []
            for frame in PIL.ImageSequence.Iterator(img_gif):
                frame_cv2 = np.array(frame.convert("RGB"))
                processed_frame_cv2, _ = processImage(frame_cv2, rotateCode)
                processed_frame = PIL.Image.fromarray(processed_frame_cv2)
                frames.append(processed_frame)
            
            # [ACTION]: Save processed frames as GIF.
            modifiedOutputFilePath = ut.FileManagement.Path.getNextIterativePath(outputFilePath, is_file=True)
            frames[0].save(
                modifiedOutputFilePath,
                save_all=True,
                append_images=frames[1:],

                # Note: Preserve original frame rate.
                duration=img_gif.info['duration'],
                # Note: Preserve original loop setting.          
                loop=img_gif.info.get('loop', 0)
            )

def generateOutputFile(inputFilePath, outputFilePath, fileType):
    if isCopyOriginal:
        shutil.copyfile(inputFilePath, outputFilePath)
    lookupTable_generateFcn[fileType](inputFilePath, outputFilePath)

lookupTable_generateFcn = {
    FileType.IMG : generateOutputImage,
    FileType.VID : generateOutputVideo,
    FileType.GIF : generateOutputGIF
}

#-----------------/
# [SECTION]: Run!
#-----------------/

def run(kwargs):
    # [ASSERT]: Rotation angle specified is a right-angle.
    if kwargs['rotate'] not in map_CliRotationValue2RotationType.keys():
        cli_ut.Wrappers.click.terminate('Non-right angle rotation specified.', cli_ut.Wrappers.click.MessageType.ERROR)

    global requiredRotation
    global requiredRotateCodes
    global isOutlineOnly
    global isCopyOriginal
    global thicknessBorder

    outputPathArgument = kwargs['output']
    inputPathArgument = kwargs['input']
    requiredRotation = map_CliRotationValue2RotationType[kwargs['rotate']]
    isOutlineOnly = kwargs['outline']
    isCopyOriginal = kwargs['copy']
    thicknessBorder = thickness_border_thick if isOutlineOnly else thickness_border_thin

    # [SET]: Set the required CV2 'Rotate-Codes', based on required rotation (argument).
    requiredRotateCodes = [cv2_map_RotationType2RotateCode[requiredRotation]] if (requiredRotation != RotationType.ALL) else cv2_map_RotationType2RotateCode.values()

    # [ASSERT]: Input file, or directory exists.
    if not os.path.exists(inputPathArgument):
        cli_ut.Wrappers.click.terminate('Input file, or directory does not exist.', cli_ut.Wrappers.click.MessageType.ERROR)
    
    # [ACTION]: Get list of '(inputFilePath, outputFilePath)'.
    outputDirectoryPath, inputOutputFilePaths = cli_ut.ArgumentProcessor.mapInputToOutputPaths(inputPathArgument, outputPathArgument)
    if (outputDirectoryPath != None) and (not os.path.exists(outputDirectoryPath)):
        os.mkdir(outputDirectoryPath)

    # [ACTION]: Report statistics.
    cli_ut.Wrappers.click.log('Processing ' + str(len(inputOutputFilePaths)) + ' file(s)...', cli_ut.Wrappers.click.MessageType.INFO)

    # [ACTION]: Loop on each...
    for inputOutputFilePath in inputOutputFilePaths:
        
        # [ACTION]: Determine file-type.
        fileType, file_ext = getFileType(inputOutputFilePath[0])
        if fileType == None:
            cli_ut.Wrappers.click.terminate('Unsupported file extension/format. [' + file_ext + ']', cli_ut.Wrappers.click.MessageType.ERROR)
        inputOutputFilePath.append(fileType)

        # [ACTION]: Override image-file extension.
        if isOverrideImageExtension and (fileType == FileType.IMG):
            file_name, _ = os.path.splitext(inputOutputFilePath[1])
            inputOutputFilePath[1] = file_name + overridingImageExtension

    # [ACTION]: Generate output file(s).
    with click.progressbar(inputOutputFilePaths) as bar:
        for inputFilePath, outputFilePath, fileType in bar:
            generateOutputFile(inputFilePath, outputFilePath, fileType)

    cli_ut.Wrappers.click.terminate('All file(s) generated successfully.', cli_ut.Wrappers.click.MessageType.INFO)