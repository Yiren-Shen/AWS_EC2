from flask import render_template, redirect, url_for, request, g
from app import webapp

import mysql.connector
from app.config import db_config
import boto3


def connect_to_database():
    return mysql.connector.connect(**db_config)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@webapp.route('/login')
def login():
    return render_template('login/login.html',
                           title='Login')


@webapp.route('/login', methods=['post'])
def login_verify():
    user_account = request.form.get('user_account',"")
    user_password = request.form.get('user_password',"")
        
    if user_account =="" or user_password == "":
        error_msg = 'Error: All fields are required!'
        return render_template('login/login.html',
                               title='Login',
                               error_msg=error_msg)
    
    cnx = get_db()
    cursor = cnx.cursor()
    query = ('SELECT * FROM users WHERE login=%s')
    
    cursor.execute(query, (user_account,))
    verify_user = cursor.fetchone()
    
    if verify_user == None:
        error_msg = "Error: User ID doesn't exist!"
        return render_template('login/login.html',
                               title='Login',
                               error_msg=error_msg)
    
    verify_password = verify_user[2]
    if user_password != verify_password:
        error_msg = "Error: Incorrect password!"
        return render_template('login/login.html',
                               title='Login',
                               error_msg=error_msg)
    
    user_id = verify_user[0]
    
    return redirect(url_for('index', user_id=user_id))
    
    
@webapp.route('/index/<int:user_id>')
def index(user_id):
    cnx = get_db()
    cursor = cnx.cursor()
    
    query = ('SELECT login FROM users WHERE id=%s')
    
    cursor.execute(query,(user_id,))
    user_account = cursor.fetchone()
    
    return render_template('login/index.html',
                           title="Hello, %s!"%(user_account),
                           user_id=user_id)


@webapp.route('/register')
def register():
    return render_template('login/register.html',
                           title='Register')


@webapp.route('/register', methods=['post'])
def register_save():
    user_account = request.form.get('user_account',"")
    user_password = request.form.get('user_password',"")
    confirm_password = request.form.get('confirm_password',"")
    
    error = False
    
    if user_account == "" or user_password == "" or confirm_password == "":
        error = True
        error_msg = "Error: All fields are required!"
        
    if user_password != confirm_password:
        error = True
        error_msg = "Error: Passwords don't match!"
        
    if error:
        return render_template('login/register.html',
                               title='Register',
                               error_msg=error_msg,
                               user_account=user_account)
    
    cnx = get_db()
    cursor = cnx.cursor()
    
    query = ('INSERT INTO users (login, password)'
             'VALUES (%(user_account)s, %(user_password)s)')
    user = {
        'user_account': user_account,
        'user_password': user_password,
    }
    
    try:
        cursor.execute(query, user)
        cnx.commit()
    except mysql.connector.errors.IntegrityError:
        error = True
        error_msg = "Error: User ID already exists!"
        return render_template('login/register.html',
                               title='Register',
                               error_msg=error_msg)
    else:
        return render_template('login/register_success.html',
                               title='Register Completed!')
