from emonitor.utils import Module
from emonitor.extensions import babel, events
from emonitor.modules.scripts.script import Script


class ScriptsModule(Module):
    """
    Definition of scripts module with no area
    """
    info = dict(area=[], name='scripts', path='', icon='fa-terminal', version='0.1')

    def __repr__(self):
        return "scripts"

    def __init__(self, app):
        """
        Add event handler for *script-event*

        :param app: *Flask* app object
        """
        Module.__init__(self, app)

        # eventhandlers
        events.addHandlerClass('*', 'emonitor.modules.scripts.script.Script', Script.handleEvent, ['in.scriptname'])

        # translations
        babel.gettext(u'emonitor.modules.scripts.script.Script')
