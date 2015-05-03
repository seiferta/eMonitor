"""
Helper methods for pdf files
"""
import re
from collections import Counter
from PyPDF2.pdf import PdfFileReader


FIELDTYPES = {'/Tx': 'text'}  # TODO: add other types if needed


def getFormFields(filepath):
    """
    Get field information of pdf file
    :param filepath: filepath to pdf file
    :return: list with tuples of (field name, field type) as counter to find multi fields
    """
    fields = []
    with open(filepath, 'rb') as f:
        reader = PdfFileReader(f, 'rb')

        for k, v in reader.getFields().iteritems():
            if re.search('^\s*[0-9]', v['/T']):
                fields.append(("".join(v['/T'].split('_')[1:]), FIELDTYPES[v['/FT']]))
            else:
                fields.append((v['/T'], FIELDTYPES[v['/FT']]))
        return Counter(fields)


def getPDFInformation(filepath):
    """
    Read information of pdf file (title, author)
    :param filepath: filepath to pdf file
    :return: dict with title and author information
    """
    with open(filepath, 'rb') as f:
        reader = PdfFileReader(f, 'rb')
        info = reader.getDocumentInfo()
        ret = {}
        if "/Title" in info:
            ret['title'] = info['/Title']
        else:
            ret['title'] = filepath.split('/')[-1]
        if "/Author" in info:
            ret['author'] = info['/Author']
        else:
            ret['author'] = ""
        return ret
