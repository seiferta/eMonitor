import flask

widget = flask.Blueprint('widget', __name__)
widget.modules = []


def _addModule(module):
    if module not in widget.modules:
        widget.modules.append(module)

widget.addModule = _addModule

