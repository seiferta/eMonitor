from werkzeug import generate_password_hash, check_password_hash
from .extensions import db


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    _password = db.Column('password', db.String(68), nullable=False)
    email = db.Column(db.String(120), unique=True)
    level = db.Column(db.Integer, default=0) # 0=not set, 1=admin
    rights = db.Column(db.Text, default='')

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = generate_password_hash(password)
    
    # Hide password encryption by exposing password field only.
    password = db.synonym('_password', descriptor=property(_get_password, _set_password))

    def __init__(self, username, password, email, level, rights):
        self.username = username
        self.password = password
        self.email = email
        self.level = level
        self.rights = rights
        
    def __repr__(self):
        return '<User %r>' % self.username

    def check_password(self, password):
        if self.password is None:
            return False
        return check_password_hash(self.password, password)

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username
    
    # static part
    @staticmethod
    def get(userid):
        user = db.session.query(User).filter_by(id=userid)
        if user.first():
            return user.first()
            
        # no user found -> init
        if db.session.query(User).count() == 0:
            user = User('Administrator', '', '', 1, '')
            user._set_password('admin')
            db.session.add(user)
            db.session.commit()
            return user
        return None
        
    @staticmethod
    def getUserByName(username):
        user = db.session.query(User).filter_by(username=username)
        if user.first():
            return user.first()
        else:
            return None
        
    @staticmethod
    def count():
        return db.session.query(User).count()
