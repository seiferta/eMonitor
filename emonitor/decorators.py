from functools import wraps

from flask_login import current_user
from .extensions import login_manager


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if (not current_user.is_authenticated) or current_user.level != 1:
            return login_manager.unauthorized()
        return f(*args, **kwargs)
    return decorated_function
