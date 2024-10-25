
import click
import sys
import os

class ClickWrapper:

    @staticmethod
    def terminate(msg:str):
        click.echo('[Error]: ' + msg)
        sys.exit(1)

class ArgumentProcessor:

    @staticmethod
    def mapInputToOutputPaths(inputPathArgument:str, outputPathArgument:str):
        """
        Map input file-path(s) to output file-path(s).

        Parameters
        ----------
        inputPathArgument : str
            Input file, or directory path.
        OutputPathArgument : str
            Output file, or directory path.

        Returns
        -------
        outputDirectoryPath, outputDirectoryPath : (str, list)
            Output directory path, if applicable, along with a list of '(inputFilePath, outputFilePath)'.
        """
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