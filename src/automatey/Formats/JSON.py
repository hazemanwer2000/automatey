
# Internal Libraries
import automatey.OS.FileUtils as FileUtils

# External Libraries
import json

def fromFile(f_src:FileUtils.File):
    '''
    Read JSON data from file, as either `dict` or `list`.
    '''
    with open(str(f_src), mode='r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data

def saveAs(data, f_dst:FileUtils.File, isMinified=False, indent:int=4):
    '''
    Write JSON data to file, from either `dict` or `list`.
    '''
    with open(str(f_dst), mode='w', encoding='utf-8') as json_file:
        kwargs = {}
        if isMinified:
            kwargs['indent'] = None
            kwargs['separators'] = (',', ':')
        else:
            kwargs['indent'] = indent
        json.dump(data, json_file, **kwargs)
