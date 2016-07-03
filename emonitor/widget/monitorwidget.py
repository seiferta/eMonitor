from flask import render_template


class MonitorWidget:
    """
    Widget prototype for monitor areas with content

    :var __info__: icon, version
    :var __fields__: field list for additional parameter values (names as string)
    :var size: tuple for default dimension (x, y)
    :var template: default template for method getHTML()
    """
    __info__ = {'icon': 'fa-gears', 'version': '1.1'}
    __fields__ = []  # aditional fields
    size = (1, 1)  # default size
    template = ""  # name of template

    def __init__(self, name, **params):
        """
        Init method with name and additional parameters

        :param name: name of widget
        :param optional params: can be updated by method *addParameters*
        """
        self.name = name
        self.params = params  # placeholder for special parameters of widget

    def getFieldNames(self):
        """
        Getter for fieldnames

        :return: list of additional fields
        """
        return self.__fields__

    def getName(self):
        """
        Getter for name of widget

        :return: name as string
        """
        return self.name
        
    def getDimension(self):
        """
        Getter for default dimension of widget

        :return: tuple with dimensions (x, y)
        """
        return self.size

    def addParameters(self, **kwargs):
        """
        Add parameters for widget stored in config of eMonitor or special for widget

        :param kwargs: args as dict list
        """
        self.params.update(kwargs)

    def getHTML(self, request, **kwargs):
        """
        Get rendered template for widget

        :param request: request object for params from current request (if needed)
        :param kwargs: list of parameters for given widget
        :return: rendered template or empty string if no template was given
        """
        if self.template != "":
            kwargs.update(self.params)
            try:
                return render_template(self.template, **kwargs)
            except:
                return render_template('widget.message.error.html', templatename=self.template, modulename=self.name)
        return "404: template not found"

    def getAdminContent(self, **params):
        """
        Get text/html value of widget for admin area

        :param params: parameter list
        :return: string value
        """
        return "<getAdminContent of prototype widget>"

    def getMonitorContent(self, **params):
        """
        Get text/html value of widget for monitor area if widget is used without surrounding template

        :param params: parameter list
        :return: string value
        """
        return "<getMonitorContent of prototype widget>"

    def getEditorContent(self, **params):
        """
        Get text/html value of widget for edit mode

        :param params: parameter list
        :return: string value
        """
        return "<getEditorContent of prototype widget>"

    @staticmethod
    def action(**kwargs):
        """
        Run type specific actions

        :param kwargs:
        :return:
        """
        return None
