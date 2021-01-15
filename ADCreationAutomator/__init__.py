"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)
from datetime import datetime
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os

#app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///admin.db'
#app.config['SECRET_KEY'] = 'secret'

#db = SQLAlchemy(app)

#admin = Admin(app)

#class Person(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    name = db.Column(db.String(30))

#admin.add_view(ModelView(Person, db.session))


import ADCreationAutomator.views
