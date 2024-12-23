
# Internal Libraries
import automatey.OS.FileUtils as FileUtils

# External Libraries
import csv

class Format:
    
    class HeaderAndData:
        '''
        - Header (i.e., list of column name(s)).
        - Data (i.e., list of entries, each a list of string(s)).
        '''
        def INTERNAL_fromFile(f_src:FileUtils.File, delimiter=','):
            with open(str(f_src), mode='r', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file, delimiter=delimiter)
                header = reader.fieldnames
                data = [list(row.values()) for row in reader]
                result = [header, data]
            return result
        
        def INTERNAL_saveAs(data, f_dst:FileUtils.File, delimiter=','):
            pass

    class ListOfDictionaries:
        '''
        List of dictionaries.
        '''
        def INTERNAL_fromFile(f_src:FileUtils.File, delimiter=','):
            with open(str(f_src), mode='r', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file, delimiter=delimiter)
                result = [row for row in reader]
            return result

        def INTERNAL_saveAs(data, f_dst:FileUtils.File, delimiter=','):
            pass

def fromFile(f_src:FileUtils.File, format=Format.ListOfDictionaries, delimiter=','):
    '''
    Read data from CSV file.
    '''
    return format.INTERNAL_fromFile(f_src, delimiter=delimiter)

def saveAs(data, f_dst:FileUtils.File, format=Format.ListOfDictionaries, delimiter=','):
    '''
    Write data as CSV, to file.
    '''
    return format.INTERNAL_saveAs(data, f_dst, delimiter=delimiter)