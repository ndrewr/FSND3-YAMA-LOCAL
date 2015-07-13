"""
    defines model classes.
    - User refers to a registered User
    - CourseCategory refers to a specific course subject
    - CourseItem refers to an individual course offering in a registered Category
"""

from . import db


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    picture = db.Column(db.String(250))
    # user = db.relationship('User', backref='creator', lazy='dynamic')

    def __init__(self, username="Zed", email="example@mail.com", picture=""):
        self.name = username
        self.email = email
        self.picture = picture


class Category(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer, unique=True, nullable=False)
    description = db.Column(db.String(250))
    # courses = db.relationship("Item", backref=db.backref('category', lazy='dynamic'))

    def __init__(self, name="New Course",
                description="A brand new course subject."):
        self.name = name
        self.description = description

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'               : self.name,
           'id'                 : self.id,
           'description'        : self.description
       }

class Item(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    url = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(250))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    # category = db.relationship('Category', backref='courses', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, url, description, category_id, user_id):
        self.name = name
        self.url = url
        self.description = description
        self.category_id = category_id
        self.user_id = user_id

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'           : self.name,
           'id'             : self.id,
           'description'    : self.description,
           'url'            : self.url
       }

if __name__ == '__main__':
    db.create_all()
