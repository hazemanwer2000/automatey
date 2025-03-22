
# Internal Libraries
import automatey.OS.FileUtils as FileUtils
import automatey.Utils.ExceptionUtils as ExceptionUtils

# Standard Libraries
import typing

# External Libraries
import PyPDF2

def merge(f_list: typing.List[FileUtils.File], f_dst:FileUtils.File):
    '''
    Merge file(s).
    '''
    if f_dst.isExists():
        raise ExceptionUtils.ValidationError('Destination file must not exist.')
    
    pdfMerger = PyPDF2.PdfMerger()
    for f in f_list:
        pdfMerger.append(str(f))
    pdfMerger.write(str(f_dst))
    pdfMerger.close()

def trim(f_src: typing.List[FileUtils.File], ranges:typing.List[typing.List[int]], f_dst:FileUtils.File):
    '''
    Trim file(s).
    
    Note that,
    - Range(s) are all-inclusive, and one-indexed.
    '''
    if f_dst.isExists():
        raise ExceptionUtils.ValidationError('Destination file must not exist.')
    
    pdfReader = PyPDF2.PdfReader(open(str(f_src), 'rb'))
    pdfWriter = PyPDF2.PdfWriter()
    
    # ? Add (selected) page(s) to PDF-writer.
    for _range in ranges:
        for i in range((_range[0] - 1), _range[1]):
            pdfWriter.add_page(pdfReader.pages[i])
    
    # ? Write PDF-writer to destination file.
    with open(str(f_dst), 'wb') as f_open:
        pdfWriter.write(f_open)
