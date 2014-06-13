from flask import render_template


class MonitorWidget:
    
    def __init__(self, name, size=(), template=""):
        self.name = name
        self.size = size  # tuple
        self.template = template
        
    def getName(self):
        return self.name
        
    def getDimension(self):
        return self.size

    def getHTML(self, request, **args):
        #params = {}
        #for p in request.args:
        #    params[p] = request.args.get(p)
        #
        #for k in args:
        #    params[k] = str(args[k])
        if self.template:
            return render_template(self.template, **args)
        return ""
