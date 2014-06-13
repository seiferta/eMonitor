from functools import wraps

from flask.ext.login import current_user
from .extensions import login_manager


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated():
            return login_manager.unauthorized()
        return f(*args, **kwargs)
    return decorated_function
