
import click
import sys
import os
import automatey.utils as ut
import automatey.cli.utils.constants as cli_ut_constants

class ClickWrapper:

    class MessageType:

        ERROR = 'ERROR'
        INFO = 'INFO'
        WARNING = 'WARNING'

    @staticmethod
    def terminate(msg:str, msg_type:str):
        """
        Terminate application with message.

        Parameters
        ----------
        msg : str
            Error message.
        msg_type : str
            Any 'MessageType.<..>' may be used.
        """
        error_code = 0 if (msg_type != ClickWrapper.MessageType.ERROR) else 1 
        complete_msg = '[' + msg_type + ']: ' + msg

        click.echo(complete_msg)
        sys.exit(error_code)

    @staticmethod
    def terminate(msg:str):
        """
        Terminate application with an error message.

        Parameters
        ----------
        msg : str
            Error message.
        """
        click.echo('[Info]: ' + msg)
        sys.exit(1)

class ArgumentProcessor:

    @staticmethod
    def mapInputToOutputPaths(inputPathArgument:str, outputPathArgument:str, File):
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
        randomFileOrDirectoryName = ut.Random.getRandomText(cli_ut_constants.randomFileNameLength)

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