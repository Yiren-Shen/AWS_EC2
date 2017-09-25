from flask import render_template, redirect, url_for, g
from app import webapp

import mysql.connector
from app.config import db_config, mybucket
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


@webapp.route('/data_clearing')
def delete():
    return render_template('mgr/delete.html',
                           title='Data Clearing')

@webapp.route('/data_clearing_complete')
def delete_complete():
    cnx = get_db()
    cursor = cnx.cursor()

    query = ('DELETE FROM images')
    cursor.execute(query)
    cnx.commit()

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(mybucket)

    for key in bucket.objects.all():
        key.delete()

    return render_template('mgr/delete_complete.html',
                           title='Data Clearing')