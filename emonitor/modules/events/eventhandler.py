from emonitor.extensions import db, events


class Eventhandler(db.Model):
    """Eventhandler class"""
    __tablename__ = 'eventhandlers'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(32))
    handler = db.Column(db.String(64))
    position = db.Column(db.Integer, default=0)
    parameters = db.Column(db.Text, default="")

    def __init__(self, event, handler, position, parameters):
        self.event = event
        self.handler = handler
        self.position = position
        self.parameters = parameters
        
    def getParameterValue(self, parameter):
        """
        Get parameter value of given parameter

        :param parameter: name of parameter as string
        :return: value of parameter, '' if not found
        """
        for p in self.parameters.split("\r\n"):
            if p.startswith(parameter + "="):
                return p.split('=')[-1]
        return ""
        
    def getParameterList(self, t='out'):
        """
        Get list of parameter names

        :param optional t: type of parameters (default *out*)
        :return: list of parameter names
        """
        return [param.split('=')[0] for param in self.parameters.split('\r\n') if param.startswith(t + '.')]
        
    def getParameterValues(self, t='out'):
        """
        Get list of parameter values

        :param optional t: type of parameters (default *out*)
        :return: list of all values
        """
        return [param.split('=') for param in self.parameters.split('\r\n') if param.startswith(t + '.')]
        
    def getInParameters(self):
        """
        Get list of all input-parameters of eventhandler

        :return: handler list
        """
        event = events.getEvents(self.event)
        if self.position < 2:
            return event.parameters
        elif self.position == '':
            if len(event.getHandlers()) > 0:
                hdl = event.getHandlers()[-1]
                return hdl.getParameterList() + event.parameters  # add event parameters
            else:
                return []
        else:
            for hdl in event.getHandlers():
                if hdl.position == self.position - 1:
                    #return [param.split('=')[0] for param in hdl.parameters.split('\r\n') if param.startswith('out.')]
                    return hdl.getParameterList() + event.parameters  # add event parameters

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'event': self.event, 'handler': self.handler, 'position': self.position, 'parameters': self.parameters}

    @staticmethod
    def getEventhandlers(id="", event=""):
        """
        Get list of eventhandlers stored in database

        :param optional id: id of eventhander or 0 for all eventhandlers
        :param optional event: name of event
        :return: list or single object :py:class:`emonitor.modules.events.eventhandler.Eventhandler`
        """
        if id != '':
            return db.session.query(Eventhandler).filter_by(id=id).first()
        elif event != '':
            return db.session.query(Eventhandler).filter_by(event=event).order_by('position').all()
        else:
            return db.session.query(Eventhandler).order_by('event', 'position').all()
