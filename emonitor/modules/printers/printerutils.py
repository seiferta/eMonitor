from flask import current_app
from jinja2 import Environment, PackageLoader, meta


class LayoutParameter:
    """
    Class for layout parameters in jinja2 templates

    types can be:

    - bool
    - str
    """
    def __init__(self, name):
        """
        Init parameter

        :param name: name as string param_[type]_[name]
        """
        t = name.split('_')
        self.ptype = t[1]
        self.pname = t[2]
        self.value = ""

    def __str__(self):
        return '<params_%s_%s>' % (self.ptype, self.pname)

    def setValue(self, value):
        """
        Setter for values

        :param value: value for current parameter
        """
        self.value = value

    def getFullName(self):
        """
        Full name of parameter uses parameter type in name

        :return: param_[type]_[name]
        """
        return "param_%s_%s" % (self.ptype, self.pname)

    def getFormatedValue(self):
        """
        Format value for type of parameter

        :return: correct type of parameter
        """
        if self.ptype == 'bool':
            return bool(int(self.value))
        else:
            return self.value


class PrintLayout:
    """
    Print layout class builds object from filename for printing
    """
    def __init__(self, filename):
        """
        Init object from filename. filenamebase *emonitor/modules/*
        path: [module]/templates/[filename]

        :param filename: print.[layout].html
        """
        self.module = filename.split('.')[0]
        self.filename = '.'.join(filename.split('.')[1:])
        self.parameters = []
        env = Environment(loader=PackageLoader('emonitor.modules.%s' % self.module, 'templates'))
        env.filters.update(current_app.jinja_env.filters)
        parsed_content = env.parse(env.loader.get_source(env, self.filename)[0])
        parameters = meta.find_undeclared_variables(parsed_content)
        for p in filter(lambda x: x.startswith('param_'), parameters):
            self.parameters.append(LayoutParameter(p))

    def getParameters(self, values=[]):
        """
        Get parameters for template. If values list is set, values will be set to parameters

        :param values: list of values for parameter
        :return: list of parameters for current layout/template file
        """
        for value in values:
            _p = value.split('=')
            for p in self.parameters:
                if p.pname == _p[0]:
                    p.setValue(_p[1])
                    break
        return self.parameters
