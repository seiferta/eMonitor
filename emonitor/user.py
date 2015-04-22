from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy.exc
from .extensions import db


class User(db.Model):
    """User class"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    _password = db.Column('password', db.String(68), nullable=False)
    email = db.Column(db.String(120), unique=True)
    level = db.Column(db.Integer, default=0)  # 0=not set, 1=admin
    rights = db.Column(db.Text, default='')
    active = db.Column(db.SMALLINT, default=0)

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = generate_password_hash(password)

    password = db.synonym('_password', descriptor=property(_get_password, _set_password))
    """Hide password encryption by exposing password field only."""

    def __init__(self, username, password, email, level, rights, active=False):
        self.username = username
        self.password = password
        self.email = email
        self.level = level
        self.rights = rights
        self.active = active
        self.anonymous = False  # default value
        self.authenticated = True  # default value
        
    def __repr__(self):
        return '<User %r>' % self.username

    def check_password(self, password):
        if self.password is None:
            return False
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        """Flask-login integration"""
        try:
            return self.authenticated
        except AttributeError:
            return True

    def is_active(self):
        """Flask-login integration"""
        return self.active == 1

    def is_anonymous(self):
        """Flask-login integration"""
        try:
            return self.anonymous
        except AttributeError:
            return False

    def get_id(self):
        return self.id

    def __unicode__(self):
        """Required for administrative interface"""
        return self.username
    
    # static part
    @staticmethod
    def getUsers(userid=0):
        """
        Get users filtered by parameter

        :param optional userid: id of user, *0* for all
        :return: list or :py:class:`emonitor.user.User`
        """
        if userid == 0:
            return db.session.query(User).order_by(User.level).all()
        else:
            user = db.session.query(User).filter_by(id=userid)
            try:
                if user.first():
                    return user.first()
            except sqlalchemy.exc.OperationalError:
                db.session.rollback()
                return User.getUsers(userid)
            
        # no user found -> init: create admin user
        if db.session.query(User).count() == 0:
            user = User('Administrator', '', '', 1, '', True)
            user._set_password('admin')
            db.session.add(user)
            db.session.commit()
            return user
        return None
        
    @staticmethod
    def getUserByName(username):
        """
        Get user by name

        :param username: username as string
        :return: :py:class:`emonitor.user.User`
        """
        user = db.session.query(User).filter_by(username=username)
        if user.first():
            return user.first()
        else:
            return None
        
    @staticmethod
    def count():
        """
        Get number of users

        :return: number as integer
        """
        return db.session.query(User).count()
