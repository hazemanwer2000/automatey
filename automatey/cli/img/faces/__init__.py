
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

#------------------------/
# [SECTION]: Constant(s)
#------------------------/
# RGB: Black
color_fill = (0, 0, 0)

# RGB: Dark-Red
color_border = (179, 0, 0)

thickness_border = 1

#------------------------/
# [SECTION]: Global variable(s)
#------------------------/

detector = MTCNN()

isRotationRequired = False
isOutlineOnly = False
isCopyOriginal = False

cv2_reverse_rotations = {
    cv2.ROTATE_90_CLOCKWISE : cv2.ROTATE_90_COUNTERCLOCKWISE,
    cv2.ROTATE_90_COUNTERCLOCKWISE : cv2.ROTATE_90_CLOCKWISE,
    cv2.ROTATE_180 : cv2.ROTATE_180
}

#----------------------/
# [SECTION]: Helper(s)
#----------------------/

def generateOutputImage(img_rgb, outputFilePath, rotate_code=None):
    if rotate_code != None:
        img_rgb = cv2.rotate(img_rgb, rotate_code)

    faces = detector.detect_faces(img_rgb)
     # Note: If this is a rotated image, and no faces have been detected, it is discarded.
    if (rotate_code != None) and (len(faces) == 0):
        return

    for face in faces:
        x, y, width, height = face['box']
        if not isOutlineOnly:
            cv2.rectangle(img_rgb, (x, y), (x + width, y + height), color_fill, -1)
        cv2.rectangle(img_rgb, (x, y), (x + width, y + height), color_border, thickness_border)

    if rotate_code != None:
        img_rgb = cv2.rotate(img_rgb, cv2_reverse_rotations[rotate_code])

    cv2.imwrite(outputFilePath, cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR))

def generateOutputFile(inputFilePath, outputFilePath):
    img = cv2.imread(inputFilePath)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    if isCopyOriginal:
        shutil.copyfile(inputFilePath, outputFilePath)
    generateOutputImage(img_rgb, ut.FileManagement.Path.getNextIterativePath(outputFilePath, is_file=True))
    if isRotationRequired:
        for rotate_code in cv2_reverse_rotations.keys():
            generateOutputImage(img_rgb, ut.FileManagement.Path.getNextIterativePath(outputFilePath, is_file=True), rotate_code=rotate_code)

#-----------------/
# [SECTION]: Run!
#-----------------/

def run(kwargs):
    global isRotationRequired
    global isOutlineOnly
    global isCopyOriginal

    outputPathArgument = kwargs['output']
    inputPathArgument = kwargs['input']
    isRotationRequired = kwargs['rotate']
    isOutlineOnly = kwargs['outline']
    isCopyOriginal = kwargs['copy']

    # [ASSERT]: Input file, or directory exists.
    if not os.path.exists(inputPathArgument):
        cli_ut.Wrappers.click.terminate('Input file, or directory does not exist.', cli_ut.Wrappers.click.MessageType.ERROR)
    
    # [ACTION]: Get list of '(inputFilePath, outputFilePath)'.
    outputDirectoryPath, inputOutputFilePaths = cli_ut.ArgumentProcessor.mapInputToOutputPaths(inputPathArgument, outputPathArgument)
    if (outputDirectoryPath != None) and (not os.path.exists(outputDirectoryPath)):
        os.mkdir(outputDirectoryPath)

    # [ACTION]: Report statistics.
    cli_ut.Wrappers.click.log('Generating ' + str(len(inputOutputFilePaths)) + ' file(s)...', cli_ut.Wrappers.click.MessageType.INFO)
    
    # [ACTION]: Generate output file(s).
    with click.progressbar(inputOutputFilePaths) as bar:
        for inputFilePath, outputFilePath in bar:
            generateOutputFile(inputFilePath, outputFilePath)

    cli_ut.Wrappers.click.terminate('All file(s) generated successfully.', cli_ut.Wrappers.click.MessageType.INFO)