import time
import re
from emonitor.extensions import db
from emonitor.modules.events.eventhandler import Eventhandler


class Replace(db.Model):
    """Replace class"""
    __tablename__ = 'replace'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    replace = db.Column(db.Text)
    
    def __init__(self, text, replace):
        self.text = text
        self.replace = replace

    @staticmethod
    def getReplacements(id=0):
        """
        Get list of replacements or filtered by id

        :param optional id: id of replacement or *0* for all
        :return: list of :py:class:`emonitor.modules.textmod.replace.Replace`
        """
        if id == 0:
            return db.session.query(Replace).order_by('id').all()
        else:
            return db.session.query(Replace).filter_by(id=id).one()

    @staticmethod
    def handleEvent(eventname, **kwargs):
        """
        Event handler for replacements

        :param eventname: *file_added*
        :param kwargs: *time*, *text*
        :return: kwargs
        """
        hdl = [hdl for hdl in Eventhandler.getEventhandlers(event=eventname) if hdl.handler == 'emonitor.modules.textmod.ocr.Ocr'][0]
        in_params = [v[1] for v in hdl.getParameterValues('in')]  # required parameters for method

        if sorted(in_params) != sorted(list(set(in_params) & set(kwargs.keys()))):
            if 'time' not in kwargs:
                kwargs['time'] = []
            kwargs['time'].append(u'replace: missing parameters for replace, nothing done.')
            return kwargs
        else:
            stime = time.time()
            text = u''

            for l in kwargs['text'].split("\n"):
                if "__" in l or l.strip() == "" or "===" in l or l.strip() == "":  # leave empty and lines
                    continue
                text = u'{}{}\n'.format(text, l)

            for r in Replace.getReplacements():
                try:
                    text = re.sub(r.text, r.replace, text)
                except:
                    pass

            kwargs['text'] = text
            t = time.time() - stime
            
        if 'time' not in kwargs.keys():
            kwargs['time'] = []
        kwargs['time'].append(u'replace: replace done in {} sec.'.format(t))
        
        return kwargs
