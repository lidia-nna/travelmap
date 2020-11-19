from db import db
from werkzeug.security import generate_password_hash, check_password_hash
import random, datetime


class UserModel(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable = False)
    email = db.Column(db.String(120), unique=True, nullable = False)
    passwd_hash = db.Column(db.String(120), nullable = False)
    registered_on = db.Column(db.DateTime, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default = False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    # passive_deletes=all instead of cascade="all,delete" did not work
    trips = db.relationship("TripsModel", cascade="all, delete", backref="parent")


    def __init__(self, email, id = None, confirmed=False, registered_on=None, confirmed_on=None):
        self.id = id
        self.email = email
        self.username = email.split('@')[0]
        self.passwd_hash = None
        if registered_on is None:
            self.registered_on = datetime.datetime.now()
        else:
            self.registered_on = registered_on
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on

    # set password hash
    def set_password(self, password):
        self.passwd_hash = generate_password_hash(password)
    
    # set username
    def set_username(self):
        username_taken = UserModel.check_user(username=self.username)
        if username_taken:
            self.username += str(random.randint(0,1000))
            self.set_username()
        else:
            return 'Username set'

    @classmethod
    def is_password(cls, hashed_passwd, password):
        return check_password_hash(hashed_passwd, password)

    @classmethod
    def check_user(cls, username=None, email=None):
        if username:
            return cls.query.filter_by(username=username).first()
        if email:
            return cls.query.filter_by(email=email).first()

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}

    @classmethod
    def find_user_id(cls, username):
        user_record = cls.query.filter_by(username=username).first()
        return user_record.id

    @classmethod
    def find_user(cls, username):
        print (type(cls.query.filter_by(username=username).first()))
        return cls.query.filter_by(username=username).first()

    @classmethod
    def update_to_db(cls, *args, email = None, password = None, username = None):
        user = cls.find_user(*args)
        if email:
            user.email = email
            user.confirmed = False
            user.confirmed_on = None
        elif password:
            user.passwd_hash = generate_password_hash(password)
        elif username:
            user.username = username
        db.session.commit()

        

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
