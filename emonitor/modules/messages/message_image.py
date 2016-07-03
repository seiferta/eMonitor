import os
import shutil
from uuid import uuid4
import mimetypes
from flask import render_template, current_app
from emonitor.extensions import babel
from emonitor.widget.monitorwidget import MonitorWidget
from emonitor.modules.messages.messages import Messages
from emonitor.modules.settings.settings import Settings
from emonitor.modules.settings.department import Department


__all__ = ['ImageWidget']

babel.gettext(u'image')
babel.gettext(u'message.image')


class ImageWidget(MonitorWidget):
    """Widget for image slideshow with Ken Burns effect"""
    __info__ = {'icon': 'fa-file-image-o'}
    __fields__ = ['images', 'key', 'crestposition']
    template = 'widget.message.image.html'
    size = (5, 4)

    def __repr__(self):
        return "image"

    def getAdminContent(self, **params):
        """
        Get content for admin area to config all parameters of message type object

        :param params: list of all currently used parameters
        :return: rendered template of image message type
        """
        params.update(settings=Settings)
        return render_template('admin.messages.image.html', **params)

    def getMonitorContent(self, **params):
        """
        Get Content for monitor of text type message

        :param params: list of all currently used parameters
        :return: html content for monitor
        """
        self.addParameters(**params)
        return self.getHTML('', **params)

    def getEditorContent(self, **params):
        """
        Get content for frontend configuration of image type message

        :param params: list of all currently used parameters
        :return: renderd template of image message type
        """
        self.addParameters(**params)
        params.update(self.params, settings=Settings)
        return render_template('frontend.messages_edit_image.html', **params)

    def addParameters(self, **kwargs):
        """
        Add special parameters for image widget *messages.image.\**
        :param kwargs: list of parameters for update
        """
        key = uuid4().hex
        if 'message' in kwargs:
            imagepath = "{}messages/{}".format(current_app.config.get('PATH_DATA'), kwargs.get('message').get('key'))
            if os.path.exists(imagepath):
                images = filter(lambda x: x.endswith('.jpg'), os.listdir(imagepath))
            else:
                images = []
            mid = kwargs.get('message').id
            if kwargs.get('message').get('key') != "":
                key = kwargs.get('message').get('key')
        else:
            images = []
            mid = None

        mimetypes.init()
        dep = Department.getDefaultDepartment()
        kwargs.update(images=images, mid=mid, key=key, crest=dep.getLogoStream(), mime=mimetypes.guess_type(dep.attributes['logo'])[0])
        self.params = kwargs

    @staticmethod
    def action(**kwargs):
        """
        implementation of image-message specific actions
        :param kwargs: list of parameters: action, mid and all arguments of ajax requests
        :return: results of action
        """
        if kwargs.get('action') == 'imageupload':
            imagepath = "{}messages/{}".format(current_app.config.get('PATH_DATA'), kwargs.get('key', '0'))
            if not os.path.exists(imagepath):
                os.makedirs(imagepath)
            images = filter(lambda x: x.lower().endswith('.jpg') or x.lower().endswith('.png'), os.listdir(imagepath))
            ext = kwargs.get('name').lower().split('.')[-1]
            filename = "{}.{}".format(len(images) + 1, ext)
            while os.path.exists("{}/{}".format(imagepath, filename)):
                filename = "{}.{}".format(int(filename.split('.')[0]) + 1, ext)

            f = open('{}/{}'.format(imagepath, filename), 'wb')
            f.write(kwargs.get('data').split('base64,')[-1].decode('base64'))
            text = '<p id="{imgshort}"><input type="checkbox" name="images" value="{img}" checked="checked"> <a href="/messages/inc/message/{key}/{img}" target=_blank">{img}</a> <i class="fa fa-trash-o fa-lg" onclick="deleteFile(\'{img}\')"></i></p>'.format(imgshort=filename.replace('.', ''), img=filename, key=kwargs.get('key'))
            return {'message': babel.gettext('messages.fileupload.done'), 'text': text}

        elif kwargs.get('action') == 'imagedelete':
            """
            delete image of message with given filename
            """
            imagepath = "{}messages/{}/".format(current_app.config.get('PATH_DATA'), kwargs.get('key', '0'))
            if os.path.exists(imagepath + kwargs.get('filename')):
                os.remove(imagepath + kwargs.get('filename'))
            return {'message': babel.gettext('messages.filedelete.done'), 'filename': kwargs.get('filename')}

        elif kwargs.get('action') == 'delete':
            """
            operation before message object deleted:
            remove all uploaded images
            """
            message = Messages.getMessages(kwargs.get('mid'))
            if os.path.exists("{}messages/{}".format(current_app.config.get('PATH_DATA'), message.get('key', '0'))):
                shutil.rmtree("{}messages/{}".format(current_app.config.get('PATH_DATA'), message.get('key', '0')))

        return "ok"
