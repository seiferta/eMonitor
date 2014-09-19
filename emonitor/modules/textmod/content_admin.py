import os
import random
import codecs
from xhtml2pdf import pisa
from StringIO import StringIO
from flask import request, render_template, current_app

from emonitor.extensions import db, classes


def getAdminContent(self, **params):
    module = request.view_args['module'].split('/')

    if len(module) == 2:
        if module[1] == 'ocr':  # ocr settings
            if request.method == 'POST':
                if request.form.get('action') == 'savereocrparams':  # save changes
                    classes.get('settings').set('ocr.inputformat', request.form.get('ocr_formats').split('\r\n'))
                    classes.get('settings').set('ocr.callstring', request.form.get('ocr_callstring'))

            params.update({'params': classes.get('ocr').getOCRParams()})
            return render_template('admin.textmod.ocr.html', **params)
        
        elif module[1] == 'ocrcustom':
            if request.method == 'POST':
                if request.form.get('action') == 'savereocrcustom':  # save changes
                    if not os.path.exists('%s/bin/tesseract/tessdata' % current_app.config.get('PROJECT_ROOT')):
                        os.makedirs('%s/bin/tesseract/tessdata/' % current_app.config.get('PROJECT_ROOT'))
                    with codecs.open('%s/bin/tesseract/tessdata/deu.user-words' % current_app.config.get('PROJECT_ROOT'), 'w', 'utf-8') as f:
                        f.write(request.form.get('ocrcustom', ''))
                        
            if os.path.exists('%s/bin/tesseract/tessdata/deu.user-words' % current_app.config.get('PROJECT_ROOT')):
                content = codecs.open('%s/bin/tesseract/tessdata/deu.user-words' % current_app.config.get('PROJECT_ROOT'), 'r', 'utf-8').read()
            else:
                current_app.logger.info('ocr custom wordlist not found')
                content = ""
            
            params.update({'content': content})
            return render_template('admin.textmod.ocrcustom.html', **params)

        elif module[1] == 'convert':  # convert image
            if request.method == 'POST':
                if request.form.get('action') == 'savereconvertparams':  # save changes
                    classes.get('settings').set('convert.format', request.form.get('convert_format'))
                    classes.get('settings').set('convert.callstring', request.form.get('convert_callstring'))

            params.update({'params': classes.get('ocr').getConvertParams(), 'imageformats': ['jpg', 'png']})
            return render_template('admin.textmod.convert.html', **params)

    else:  # replacements
        if request.method == 'POST':
            if request.form.get('action') == 'addreplace':  # add replacement
                params.update({'replacement': classes.get('replace')('', '')})
                return render_template('admin.textmod_actions.html', **params)

            elif request.form.get('action').startswith('editreplace_'):  # edit existing replacement
                params.update({'replacement': classes.get('replace').getReplacements(request.form.get('action').split('_')[-1])})
                return render_template('admin.textmod_actions.html', **params)

            elif request.form.get('action').startswith('deletereplace_'):  # delete existing replacement
                db.session.delete(classes.get('replace').getReplacements(int(request.form.get('action').split('_')[-1])))
                db.session.commit()
                
            elif request.form.get('action') == 'savereplace':  # save replacement
                if request.form.get('replace_id') == 'None':  # add new
                    db.session.add(classes.get('replace')(request.form.get('replace_text'), request.form.get('replace_repl')))
                    
                else:  # update existing replacement
                    replacement = classes.get('replace').getReplacements(request.form.get('replace_id'))
                    replacement.text = request.form.get('replace_text')
                    replacement.replace = request.form.get('replace_repl')
                db.session.commit()
               
        params.update({'replacements': classes.get('replace').getReplacements().all()})
        return render_template('admin.textmod.html', **params)


def getAdminData(self):
    if request.args.get('action') == 'testocr':
        ret = {'path': '', 'ocrtext': ''}
        teststring = request.args.get('callstring')
        teststring = teststring.replace('[basepath]', current_app.config.get('PROJECT_ROOT'))

        # test program
        ret['path'] = str(os.path.exists(teststring.split()[0]))

        # test ocr with random data
        ret['ocrtext'] = ""
        testtext = pisa.COPYRIGHT[:100].replace("\n", "")
        pdf = StringIO()
        pisa.CreatePDF(StringIO(render_template('admin.textmod.testfax.html', text=testtext)), pdf)
        tmpfilename = '%s.pdf' % random.random()
        with open("%s%s" % (current_app.config.get('PATH_TMP'), tmpfilename), 'wb') as f:
            f.write(pdf.getvalue())

        p, t = classes.get('ocr').convertFileType(current_app.config.get('PATH_TMP'), tmpfilename)
        if p != 1:  # only one page possible
            ret['error'] = "convert error"

        text, t = classes.get('ocr').convertText(current_app.config.get('PATH_TMP'), tmpfilename[:-3] + 'png', p)
        ret['ocrtext'] = str(text.replace("\n", " ").strip() == testtext)
        if os.path.exists('%s%s' % (current_app.config.get('PATH_TMP'), tmpfilename)):
            os.remove('%s%s' % (current_app.config.get('PATH_TMP'), tmpfilename))
        if os.path.exists('%s%s' % (current_app.config.get('PATH_TMP'), tmpfilename[:-3] + 'png')):
            os.remove('%s%s' % (current_app.config.get('PATH_TMP'), tmpfilename[:-3] + 'png'))

        return ret
    return ""
