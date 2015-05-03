import os
import codecs
import subprocess
import time
import logging
from PIL import Image

from emonitor.extensions import db
from emonitor.modules.settings.settings import Settings
from emonitor.modules.events.eventhandler import Eventhandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DEFAULTINPUTFORMAT = ['pdf', 'tiff', 'jpg']
DEFAULTINPUTTEXTFORMAT = ['txt']
DEFAULTCALLSTRING = '[basepath]/bin/tesseract/tesseract [incomepath][filename] [tmppath] -l deu -psm 6 quiet custom'

DEFAULTIMAGECONVERTFORMAT = 'png'
DEFAULTIMAGECONVERTCALL = 'convert -density 200 [incomepath][filename] -quality 200 [tmppath]'


class Ocr(Settings):
    """OCR class"""
    @staticmethod  # convert [pdf, tif, jpg] -> jpg or png
    def convertFileType(path, inname):
        from emonitor import app
        i = t = 0
        params = Ocr.getOCRParams()
        convertparams = Ocr.getConvertParams()
        
        ext = os.path.splitext(inname)[-1]
        inname = os.path.splitext(inname)[0]

        if ext[1:] not in params['inputformat']:
            return 0, 0.0
        
        path2 = app.config.get('PATH_TMP')
        if "/" in inname or "\\" in inname or ":" in inname:
            path = path2 = ""

        while 1:
            try:
                stime = time.time()
                callstring = convertparams['callstring']
                callstring = callstring.replace('[basepath]', app.config.get('PROJECT_ROOT'))
                callstring = callstring.replace('[incomepath]', path)
                callstring = callstring.replace('[filename]', '{}{}[{}]'.format(inname, ext, i))
                callstring = callstring.replace('[tmppath]', '{}{}-%d.{}'.format(path2, inname, convertparams['format']))
                logger.debug('run image conversion with {}'.format(callstring))
                subprocess.check_output(callstring, stderr=subprocess.STDOUT, shell=True)

                if i > -1:
                    im = Image.open('{}{}-{}.{}'.format(path2, inname, i, convertparams['format']))
                    w, h = im.size
                    # remove header line = 1/4 of quality
                    im.crop((0, 100, w, h - 100)).save('{}{}-{}.{}'.format(path2, inname, i, convertparams['format']), convertparams['format'].upper())

                i += 1
                t = time.time() - stime
                if ext[1:] in ['jpg', 'jpeg', 'tif', 'tiff', 'png']:  # tif and jpg with only one page
                    break
                    
            except:
                break
        return i, t
        
    @staticmethod
    def convertText(path, inname, pages):
        """
        Convert file to text (ocr)

        :param path: path of income file
        :param inname: filename of income file
        :param pages: number of pages
        :return: tuple of recognized text and time
        """
        from emonitor import app
        i = t = 0
        text = u""
        params = Ocr.getOCRParams()
        convertparams = Ocr.getConvertParams()

        ext = os.path.splitext(inname)[-1]
        if ext[1:] in params['inputtextformat']:  # text format from external application as text given
            stime = time.time()
            try:
                text = codecs.open('{}{}'.format(path, inname), 'r', encoding='utf-8').read()
            except:
                text = codecs.open('{}{}'.format(path, inname), 'r', encoding="latin-1").read()
            #try:
            #    text = text.decode('latin-1').encode('utf-8')
            #except:
            #
            #    pass
            return text, time.time() - stime

        inname = os.path.splitext(inname)[0]

        if path != app.config.get('PATH_TMP'):
            path = app.config.get('PATH_TMP')
        
        if "/" in inname or "\\" in inname or ":" in inname:
            path = ""

        while i < pages:
            stime = time.time()
            
            callstring = params['callstring']
            callstring = callstring.replace('[basepath]', app.config.get('PROJECT_ROOT'))
            callstring = callstring.replace('[incomepath]', path)
            callstring = callstring.replace('[filename]', '{}-{}.{}'.format(inname, i, convertparams['format']))
            callstring = callstring.replace('[tmppath]', '{}{}-{}'.format(path, inname, i))
            logger.debug('run ocr with {}'.format(callstring))
            subprocess.call(callstring, shell=True)

            try:
                text = u'{}{}'.format(text, codecs.open('{}{}-{}.txt'.format(path, inname, i), 'r', 'utf-8').read())
            except:
                pass
            try:
                os.remove('{}{}-{}.png'.format(path, inname, i))
            except:
                pass
            try:
                os.remove('{}{}-{}.txt'.format(path, inname, i))
            except:
                pass
            finally:
                t = time.time() - stime
            i += 1
        return text, t  # return ocr text
        
    @staticmethod
    def getConvertParams():
        """
        Get dict with configuration parameters for conversion

        :return: *callstring*, *format*
        """
        ret = {'callstring': '', 'format': ''}
        for v in Settings.query.filter(Settings.name.like('convert.%')):
            if v.name == 'convert.format':
                ret['format'] = v.value
            elif v.name == 'convert.callstring':
                ret['callstring'] = v.value
        if Settings.query.filter(Settings.name.like('convert.%')).count() == 0:  # use default values
            db.session.add(Settings.set('convert.format', DEFAULTIMAGECONVERTFORMAT))
            db.session.add(Settings.set('convert.callstring', DEFAULTIMAGECONVERTCALL))
            db.session.commit()
            return Ocr.getConvertParams()
        return ret

    @staticmethod
    def getOCRParams():
        """
        Get dict with OCR parameters

        :return: *callstring*, *inputformat*, *inputtextformat*
        """
        ret = {'callstring': '', 'inputformat': '', 'inputtextformat': ''}
        for v in Settings.query.filter(Settings.name.like('ocr.%')).all():
            ret[v.name.split('.')[-1]] = v.value
        if Settings.query.filter(Settings.name.like('ocr.%')).count() == 0:  # use default values
            db.session.add(Settings.set('ocr.inputformat', DEFAULTINPUTFORMAT))
            db.session.add(Settings.set('ocr.inputtextformat', DEFAULTINPUTTEXTFORMAT))
            db.session.add(Settings.set('ocr.callstring', DEFAULTCALLSTRING))
            db.session.commit()
            return Ocr.getOCRParams()
        return ret
        
    @staticmethod
    def handleEvent(eventname, **kwargs):
        """
        Event handler for OCR textmod module

        :param eventname: *file_added*
        :param kwargs: *time*, *incomepath*, *filename*
        :return: add *text* to kwargs
        """
        hdl = [hdl for hdl in Eventhandler.getEventhandlers(event=eventname) if hdl.handler == 'emonitor.modules.textmod.ocr.Ocr'][0]
        in_params = [v[1] for v in hdl.getParameterValues('in')]  # required parameters for method
        if sorted(in_params) != sorted(list(set(in_params) & set(kwargs.keys()))):
            if 'time' not in kwargs.keys():
                kwargs['time'] = []
            kwargs['time'].append(u'replace: missing parameters for replace, nothing done.')
        else:
            p, t1 = Ocr.convertFileType(kwargs['incomepath'], kwargs['filename'])
            text, t2 = Ocr.convertText(kwargs['incomepath'], kwargs['filename'], p)
            if 'time' not in kwargs.keys():
                kwargs['time'] = []
            kwargs['time'].append(u'ocr: text conversion and recognition done in {} sec.'.format(t1 + t2))
            kwargs['text'] = text
        return kwargs
