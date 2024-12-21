
# Internal Libraries
import automatey.OS.FileUtils as FileUtils

# External Libraries
from importlib import resources

def resolve(f_relative:FileUtils.File):
    '''
    Resolves file, from relative (e.g., `Video/video-name.ext`) to absolute.
    '''
    packagePath = 'automatey.Resources.' + '.'.join(str(f_relative).split('/')[:-1])
    fileName = f_relative.getName()
    with resources.path(packagePath, fileName) as path:
        f_absolute = FileUtils.File(str(path))
    return f_absolute