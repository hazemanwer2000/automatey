
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import automatey.utils as ut
import automatey.cli.utils as cli_ut

#------------------------/
# [SECTION]: Constant(s)
#------------------------/
# ...

#----------------------/
# [SECTION]: Helper(s)
#----------------------/

def generateOutputFile(inputFilePath, outputFilePath):
    print(inputFilePath)

#-----------------/
# [SECTION]: Run!
#-----------------/

def run(kwargs):
    outputPathArgument = kwargs['output']
    inputPathArgument = kwargs['input']
    IsRotationRequired = kwargs['rotate']

    # [ASSERT]: Input file, or directory exists.
    if not os.path.exists(inputPathArgument):
        cli_ut.ClickWrapper.terminate('Input file, or directory does not exist.')
    
    # [ACTION]: Get list of '(inputFilePath, outputFilePath)'.
    outputDirectoryPath, inputOutputFilePaths = cli_ut.ArgumentProcessor.mapInputToOutputPaths(inputPathArgument, outputPathArgument)
    if (outputDirectoryPath != None) and (not os.path.exists(outputDirectoryPath)):
        os.mkdir(outputDirectoryPath)
    
    # [ACTION]: Generate output file(s).
    for inputFilePath, outputFilePath in inputOutputFilePaths:
        generateOutputFile(inputFilePath, outputFilePath)
