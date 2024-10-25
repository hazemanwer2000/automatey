
# [SECTION]: Macro(s)

def stage_getOutputDirectoryPath(outputDirectoryPathArgument):
    if outputDirectoryPathArgument == None:
        print('X')
    else:
        print('Y')

def run(kwargs):
    outputDirectoryPath = stage_getOutputDirectoryPath(kwargs['output'])
