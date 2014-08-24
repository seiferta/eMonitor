import os
import subprocess
import time
from PIL import Image

from emonitor.extensions import db, classes
from emonitor.modules.settings.settings import Settings

DEFAULTINPUTFORMAT = ['pdf', 'tiff', 'jpg']
DEFAULTCALLSTRING = '[basepath]/bin/tesseract/tesseract [incomepath][filename] [tmppath] -l deu -psm 6 quiet custom'

DEFAULTIMAGECONVERTFORMAT = 'png'
DEFAULTIMAGECONVERTCALL = 'convert -density 200 [incomepath][filename] -quality 200 [tmppath]'


class Ocr(Settings):

    @staticmethod  # convert [pdf, tif, .jpg] -> jpg or png
    def convertFileType(path, inname):
        from main import webapp as wa
        i = t = 0
        params = Ocr.getOCRParams()
        convertparams = Ocr.getConvertParams()
        
        ext = os.path.splitext(inname)[-1]
        inname = os.path.splitext(inname)[0]

        if ext[1:] not in params['inputformat']:
            return 0, 0.0
        
        path2 = wa.config.get('PATH_TMP')
        if "/" in inname or "\\" in inname or ":" in inname:
            path = path2 = ""

        while 1:
            try:
                stime = time.time()
                callstring = convertparams['callstring']
                callstring = callstring.replace('[basepath]', wa.config.get('PROJECT_ROOT'))
                callstring = callstring.replace('[incomepath]', path)
                callstring = callstring.replace('[filename]', '%s%s[%s]' % (inname, ext, i))
                callstring = callstring.replace('[tmppath]', '%s%s%s' % (path2, inname + '-%d.', convertparams['format']))
                #wa.logger.info('run image conversion with %s' % callstring)
                subprocess.check_output(callstring, stderr=subprocess.STDOUT, shell=True)

                if i > -1:
                    im = Image.open('%s%s-%s.%s' % (path2, inname, i, convertparams['format']))
                    w, h = im.size
                    # remove header line = 1/4 of quality
                    im.crop((0, 100, w, h - 100)).save('%s%s-%s.%s' % (path2, inname, i, convertparams['format']), convertparams['format'].upper())

                i += 1
                t = time.time() - stime
                if ext in ['.jpg', '.tif', 'png']:  # tif and jpg with only one page
                    break
                    
            except:
                break
        return i, t
        
    @staticmethod  # run ocr with given file
    def convertText(path, inname, pages):
        from main import webapp as wa
        i = t = 0
        text = ""
        params = Ocr.getOCRParams()
        convertparams = Ocr.getConvertParams()
        inname = os.path.splitext(inname)[0]
        
        if path != wa.config.get('PATH_TMP'):
            path = wa.config.get('PATH_TMP')
        
        #path2 = wa.config.get('PATH_TMP')
        if "/" in inname or "\\" in inname or ":" in inname:
            path = ""

        while i < pages:
            stime = time.time()
            
            callstring = params['callstring']
            callstring = callstring.replace('[basepath]', wa.config.get('PROJECT_ROOT'))
            callstring = callstring.replace('[incomepath]', path)
            callstring = callstring.replace('[filename]', '%s-%s.%s' % (inname, i, convertparams['format']))
            callstring = callstring.replace('[tmppath]', '%s%s-%s' % (path, inname, i))
            #wa.logger.info('run ocr with %s' % callstring)
            subprocess.call(callstring, shell=True)

            try:
                text += open('%s%s-%s.txt' % (path, inname, i), 'r').read()
            except:
                pass
            try:
                os.remove('%s%s-%s.%s' % (path, inname, i, 'png'))
            except:
                pass
            try:
                os.remove('%s%s-%s.txt' % (path, inname, i))
            except:
                pass
            finally:
                t = time.time() - stime
            i += 1
        return text, t  # return ocr text
        
    @staticmethod
    def getConvertParams():
        ret = {'callstring': '', 'format': ''}
        for v in db.session.query(Settings).filter(Settings.name.like('convert.%')):
            if v.name == 'convert.format':
                ret['format'] = v.value
            elif v.name == 'convert.callstring':
                ret['callstring'] = v.value
        if db.session.query(Settings).filter(Settings.name.like('convert.%')).count() == 0:  # use default values
            db.session.add(Settings.set('convert.format', DEFAULTIMAGECONVERTFORMAT))
            db.session.add(Settings.set('convert.callstring', DEFAULTIMAGECONVERTCALL))
            db.session.commit()
            return Ocr.getConvertParams()
        return ret

    @staticmethod
    def getOCRParams():
        ret = {'callstring': '', 'inputformat': ''}
        for v in db.session.query(Settings).filter(Settings.name.like('ocr.%')):
            if v.name == 'ocr.inputformat':
                ret['inputformat'] = v.value
            elif v.name == 'ocr.callstring':
                ret['callstring'] = v.value
        if db.session.query(Settings).filter(Settings.name.like('ocr.%')).count() == 0:  # use default values
            db.session.add(Settings.set('ocr.inputformat', DEFAULTINPUTFORMAT))
            db.session.add(Settings.set('ocr.callstring', DEFAULTCALLSTRING))
            db.session.commit()
            return Ocr.getOCRParams()
        return ret
        
    @staticmethod
    def handleEvent(eventname, *kwargs):
        hdl = [hdl for hdl in classes.get('eventhandler').getEventhandlers(event=eventname) if hdl.handler == 'emonitor.modules.textmod.ocr.Ocr'][0]
        in_params = [v[1] for v in hdl.getParameterValues('in')]  # required parameters for method
        if sorted(in_params) != sorted(list(set(in_params) & set(kwargs[0].keys()))):
            if not 'time' in kwargs[0]:
                kwargs[0]['time'] = []
            kwargs[0]['time'].append('replace: missing parameters for replace, nothing done.')
        else:
            p, t1 = Ocr.convertFileType(kwargs[0]['incomepath'], kwargs[0]['filename'])
            text, t2 = Ocr.convertText(kwargs[0]['incomepath'], kwargs[0]['filename'], p)
            if not 'time' in kwargs[0]:
                kwargs[0]['time'] = []
            kwargs[0]['time'].append('ocr: text conversion and recognition done in %s sec.' % (t1 + t2))
            kwargs[0]['text'] = text
        return kwargs
