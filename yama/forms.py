"""
	Class definitions for form components using WTForms
"""
from wtforms import TextAreaField, StringField, validators
from flask_wtf import Form

from models import User, Category, Item

class TitleDescriptionForm(Form):
	name = StringField('name', validators=[validators.Required(), validators.Length(min=2, max=32)])
	description = TextAreaField('description', validators=[validators.Length(max=120)], default='A new course.')
	url = StringField('url', validators=[validators.Required(), validators.URL()])
