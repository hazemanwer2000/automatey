
import automatey.utils as ut
import automatey.cli.utils as cli_ut
import os

#------------------------/
# [SECTION]: Constant(s)
#------------------------/

randomFileOrDirectoryName = ut.Random.getRandomText(10)

#----------------------/
# [SECTION]: Helper(s)
#----------------------/

def processPaths(inputPathArgument, outputPathArgument):
    inputOutputFilePaths = []
    outputDirectoryPath = None

    # [CASE]: File as input.
    if os.path.isfile(inputPathArgument):
        inputFileExtension = os.path.splitext(inputPathArgument)[1]
        outputFilePath = outputPathArgument if (outputPathArgument != None) else (randomFileOrDirectoryName + inputFileExtension)
        inputOutputFilePaths.append([inputPathArgument, outputFilePath])

    # [CASE]: Directory as input.
    else:
        outputDirectoryPath = outputPathArgument if (outputPathArgument != None) else randomFileOrDirectoryName
        for inputFileName in os.listdir(inputPathArgument):
            inputFilePath = os.path.join(inputPathArgument, inputFileName)
            outputFilePath = os.path.join(outputDirectoryPath, inputFileName)
            inputOutputFilePaths.append([inputFilePath, outputFilePath])
    
    return outputDirectoryPath, inputOutputFilePaths

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
    
    print(outputDirectoryPath)
    print(inputOutputFilePaths)