from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)


# this definition must follow app instantiation to hookup access to views
from yama import views, models
