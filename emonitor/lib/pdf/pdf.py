"""
Helper methods for pdf files
"""
import os
import re
from collections import Counter, OrderedDict
from PyPDF2.pdf import PdfFileReader
import random
import tempfile
import subprocess

FIELDTYPES = {'/Tx': 'text'}  # TODO: add other types if needed


def getFormFields(filepath):
    """
    Get field information of pdf file
    :param filepath: filepath to pdf file
    :return: list with tuples of (field name, field type) as counter to find multi fields
    """
    fields = []
    with open(filepath, 'rb') as f:
        reader = PdfFileReader(f)

        for k, v in reader.getFields().iteritems():
            if re.search('^\s*[0-9]', v['/T']):
                fields.append(("_".join(v['/T'].split('_')[1:]), FIELDTYPES[v['/FT']]))
            else:
                fields.append((v['/T'], FIELDTYPES[v['/FT']]))

        ret = OrderedDict()
        for k, v in iter(sorted(Counter(fields).iteritems())):
            ret[k[0].encode('utf-8')] = (k[1].encode('utf-8'), v)
        return ret


def getPDFInformation(filepath):
    """
    Read information of pdf file (title, author)
    :param filepath: filepath to pdf file
    :return: dict with title and author information
    """
    with open(filepath, 'rb') as f:
        reader = PdfFileReader(f)
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


class PDFFormFile:
    TAG_RE = re.compile(r'<[^>]+>')

    def __init__(self, filename, **kwargs):
        self.filename = filename
        self._information = getPDFInformation(self.filename)
        self._fields = getFormFields(self.filename)

    @property
    def information(self):
        return self._information

    @property
    def fields(self):
        return self._fields

    @property
    def multi(self):
        return max([f[1] for f in self.fields.values()]) > 1

    def createReport(self, **kwargs):
        """
        create the pdf report from template (pdf form)

        :param kwargs: 'alarmlist' with list of alarm objects, 'fielddefinition' as dict of fields in form template
        :return: filename of created report
        """
        alarms = []
        definition = []
        reportfields = []
        if 'alarmlist' in kwargs:
            alarms = kwargs['alarmlist']
        if 'fielddefinition' in kwargs:
            definition = kwargs['fielddefinition']

        for fieldname, fielddef in self.fields.iteritems():
            if fielddef[1] == 1 and fieldname in definition:  # single fields
                if len(alarms) > 0:
                    reportfields.append(('{}'.format(fieldname), alarms[0].getFieldValue(definition[fieldname]).encode('latin-1')))
                else:
                    reportfields.append(('{}'.format(fieldname), ''))

            elif fielddef[1] > 1 and fieldname in definition:  # multiple fields
                for alarm in alarms:
                    reportfields.append(('{}_{}'.format(alarms.index(alarm) + 1, fieldname), alarm.getFieldValue(definition[fieldname]).encode('latin-1')))

        tmppath = tempfile.gettempdir()
        outputname = '{}{}.{}'.format(tmppath, random.random(), self.filename.split('.')[-1])
        with open('{}{}.fdf'.format(tmppath, random.random()), 'wb') as tmpfile:
            tmpfile.write(self.forge_fdf('', reportfields))
            callstring = 'pdftk {} fill_form {} output {}'.format(self.filename, tmpfile.name, outputname)
            tmpfile.close()
            subprocess.call(callstring.split())  # create pdf form
            os.remove(tmpfile.name)  # remove data file
        return outputname

    def remove_tags(self, text):
        return self.TAG_RE.sub('', text)

    @staticmethod
    def handle_hidden(key, fields_hidden):
        if key in fields_hidden:
            return b"/SetF 2"
        return b"/ClrF 2"

    @staticmethod
    def handle_readonly(key, fields_readonly):
        if key in fields_readonly:
            return b"/SetFf 1"
        return b"/ClrFf 1"

    def handle_data_strings(self, fdf_data_strings, fields_hidden, fields_readonly):
        for (key, value) in fdf_data_strings:
            if isinstance(value, bool) and value:
                value = b'/Yes'
            elif isinstance(value, bool) and not value:
                value = b'/Off'
            else:
                value = b''.join([b' (', value, b')'])

            yield b''.join([b'<<\n/V', value, b'\n/T (', key, b')\n',
                            self.handle_hidden(key, fields_hidden), b'\n',
                            self.handle_readonly(key, fields_readonly), b'\n>>\n'])

    def handle_data_names(self, fdf_data_names, fields_hidden, fields_readonly):
        for (key, value) in fdf_data_names:
            yield b'<<\n/V /{}\n/T ({})\n{}\n{}\n>>\n'.format(value, key, self.handle_hidden(key, fields_hidden), self.handle_readonly(key, fields_readonly))

    def forge_fdf(self, pdf_form_url="", fdf_data_strings=list(), fdf_data_names=list(), fields_hidden=list(), fields_readonly=list()):
        fdf = [b'%FDF-1.2\n%\xe2\xe3\xcf\xd3\r\n', b'1 0 obj\n<<\n/FDF\n', b'<<\n/Fields [\n',
               b''.join(self.handle_data_strings(fdf_data_strings, fields_hidden, fields_readonly)),
               b''.join(self.handle_data_names(fdf_data_names, fields_hidden, fields_readonly))]
        if pdf_form_url:
            fdf.append(b'/F ({})\n'.format(pdf_form_url))
        fdf.append(b']\n>>\n>>\nendobj\ntrailer\n\n<<\n/Root 1 0 R\n>>\n%%EOF\n\x0a')
        return b''.join(fdf)
