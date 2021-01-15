"""
Routes and views for the flask application.
"""

# Archive after creating accounts. PS needs to delete file.

from datetime import datetime
from flask import render_template, flash
from ADCreationAutomator import app
from flask import request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
import sqlite3
import os.path
from flask_admin.actions import action
import subprocess
from io import StringIO
import pandas as pd
from os import path
import time
from flask_admin.menu import MenuLink

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dbpath = os.path.join(BASE_DIR, 'admin.db')
csvpath = os.path.join(BASE_DIR, 'Users.csv')

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///admin.db'
app.config['SECRET_KEY'] = 'secret'

db = SQLAlchemy(app)
admin = Admin(app)

class StudentTeacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    middle_initial = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    email = db.Column(db.String(30))
    school = db.Column(db.String(30))
    startdate = db.Column(db.String(30))
    enddate = db.Column(db.String(30))
    requested_by = db.Column(db.String(30))

class StudentTeacherArchive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    middle_initial = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    email = db.Column(db.String(30))
    school = db.Column(db.String(30))
    startdate = db.Column(db.String(30))
    enddate = db.Column(db.String(30))
    requested_by = db.Column(db.String(30))


class TransactionView(ModelView):

    @action('create accounts', 'Create Accounts', 'Are you sure you want to create the selected acounts in AD?')
    def action_export(self, ids):
        idlist = []
        conn = sqlite3.connect(dbpath)
        count = 0
        for _id in ids:
            idlist.append(_id)
            print(idlist)
            count += 1
        #SQL query
        df = pd.read_sql_query("select * from Student_Teacher where id IN (%s)" % ",".join(map(str,idlist)), conn)
        if path.exists(csvpath) is True:
            df.to_csv(csvpath, mode='a', header=False, encoding='utf-8', index=False)
        else:
            df.to_csv(csvpath, mode='a', encoding='utf-8', index=False)
        #Query setup for moving values
        sql = "BEGIN TRANSACTION; INSERT INTO Student_Teacher_Archive(first_name,middle_initial,last_name,email,school,startdate,enddate,requested_by) SELECT first_name,middle_initial,last_name,email,school,startdate,enddate,requested_by FROM Student_Teacher WHERE id IN (%s)" % ",".join(map(str,idlist)) + "; DELETE FROM Student_Teacher WHERE id in (%s)" % ",".join(map(str,idlist)) + "; COMMIT;"
        c = conn.cursor()
        c.executescript(sql)
        flash("{0} accounts have been created, entries were moved to Archive".format(count))

class ArchiveView(ModelView):

    @action('create accounts', 'Create Accounts', 'Are you sure you want to create the selected acounts in AD?')
    def action_export(self, ids):
        idlist = []
        conn = sqlite3.connect(dbpath)
        count = 0
        for _id in ids:
            idlist.append(_id)
            print(idlist)
            count += 1
        #SQL query
        df = pd.read_sql_query("select * from Student_Teacher_Archive where id IN (%s)" % ",".join(map(str,idlist)), conn)
        if path.exists(csvpath) is True:
            df.to_csv(csvpath, mode='a', header=False, encoding='utf-8', index=False)
        else:
            df.to_csv(csvpath, mode='a', encoding='utf-8', index=False)
        flash("{0} accounts have been created".format(count))



TransactionView.can_export = True
ArchiveView.can_export = True
admin.add_view(TransactionView(StudentTeacher, db.session))
admin.add_view(ArchiveView(StudentTeacherArchive, db.session))
admin.add_link(MenuLink(name='Main', category='', url='/home'))


@app.route('/py', methods=['GET', 'POST'])
def server():
        # Then get the data from the form
    if request.method == 'POST':
        yourfirst = request.form.get('yourfirst')
        yourlast = request.form.get('yourlast')
        yourspace = ' '
        yourname = yourfirst + yourspace + yourlast
        teachersfirst = request.form.get('theirfirst')
        teachersmiddle = request.form.get('theirmiddle')
        teachersmiddle += "."
        teacherslast = request.form.get('theirlast')
        email = request.form.get('email')
        school = request.form.get('school')
        startdate = request.form.get('start')
        enddate = request.form.get('end')
        rowsQuery = "SELECT MAX(ID) FROM Student_Teacher"
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute(rowsQuery)
        oldrows = c.fetchall()
        rows = [*oldrows]
        try:
            numberstring = str(rows[0])
            number = int(''.join(filter(str.isdigit, numberstring)))
            noentries = 0
        except:
            noentries = 1

        if noentries == 1:
            id = 1
        else:
            rows = [*oldrows]
            numberstring = str(rows[0])
            number = int(''.join(filter(str.isdigit, numberstring)))
            id = number + 1
        #set up SQL query
        sql = ''' INSERT INTO Student_Teacher(id,first_name,middle_initial,last_name,email,school,startdate,enddate,requested_by) VALUES(?,?,?,?,?,?,?,?,?) '''
        project = (id, teachersfirst, teachersmiddle, teacherslast, email, school, startdate, enddate, yourname)

        #Insert records
        
        c.execute(sql, project)
        conn.commit()
        oldrows.clear()
        rows.clear()
        noentries = 0
        # Get the username/password associated with this tag
        

        # Generate just a boring response
        return 'Thank you, your account request has been submitted.'
        time.sleep(5)
        return redirect("http://www.example.com", code=302)
        # Or you could have a custom template for displaying the info
        # return render_template('asset_information.html',
        #                        username=user, 
        #                        password=password)

    # Otherwise this was a normal GET request
    else:   
        return render_template('index.html')


@app.route('/')

@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/staff')
def contact():
    """Renders the contact page."""
    return render_template(
        'staff.html',
        title='Staff Account',
        year=datetime.now().year,
        message='Staff Account Request'
    )

@app.route('/studentteacher')
def about():
    """Renders the about page."""
    return render_template(
        'studentteacher.html',
        title='Student Teacher Account Request',
        year=datetime.now().year,
        message='Student Teacher Account Request'
    )
