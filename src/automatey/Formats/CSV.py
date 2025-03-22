
# Internal Libraries
import automatey.OS.FileUtils as FileUtils
import automatey.Utils.ExceptionUtils as ExceptionUtils

# External Libraries
import csv

class Format:
    
    class HeaderAndData:
        '''
        - Header (i.e., list of column name(s)).
        - Entries (i.e., list of entries, each a list of string(s)).
        '''

        @staticmethod
        def fromDictionaries(data):
            header = list(data[0].keys())
            entries = [list(x.values()) for x in data]
            return (header, entries)

        @staticmethod
        def toDictionaries(header, entries):
            return [dict(zip(header, entry)) for entry in entries]

    class ListOfDictionaries:
        '''
        List of dictionaries.
        '''
        @staticmethod
        def INTERNAL_fromFile(f_src:FileUtils.File, delimiter=','):
            with open(str(f_src), mode='r', encoding='utf-8', newline='') as csv_file:
                reader = csv.DictReader(csv_file, delimiter=delimiter)
                data = [row for row in reader]
            return data

        @staticmethod
        def INTERNAL_saveAs(data, f_dst:FileUtils.File, delimiter=','):
            with open(str(f_dst), mode='w', encoding='utf-8', newline='') as csv_file:
                header = data[0].keys()
                writer = csv.DictWriter(csv_file, fieldnames=header, delimiter=delimiter)
                writer.writeheader()
                writer.writerows(data)

def fromFile(f_src:FileUtils.File, format=Format.ListOfDictionaries, delimiter=','):
    '''
    Read data from CSV file.

    Note that,
    - Format used by default is `ListOfDictionaries`.
    '''
    return Format.ListOfDictionaries.INTERNAL_fromFile(f_src, delimiter=delimiter)

def saveAs(data, f_dst:FileUtils.File, format=Format.ListOfDictionaries, delimiter=','):
    '''
    Write data as CSV, to file.
    
    Note that,
    - Format used by default is `ListOfDictionaries`.
    '''
    if f_dst.isExists():
        raise ExceptionUtils.ValidationError('Destination file must not exist.')
    return Format.ListOfDictionaries.INTERNAL_saveAs(data, f_dst, delimiter=delimiter)
