from flask import render_template, request, g
from app import webapp
from wand.image import Image
from wand.color import Color

import mysql.connector
from app.config import db_config, mybucket, tmp_path
import boto3
import os


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


@webapp.route('/image_list/<int:user_id>')
def image_list(user_id):
    cnx = get_db()
    cursor = cnx.cursor()

    query = ('SELECT id,key1 FROM images WHERE userId=%s')
    cursor.execute(query, (user_id,))
    images = cursor.fetchall()

    keys = []
    for image in images:
        key = image[1]
        fname = os.path.split(key)
        key_thm = os.path.join(fname[0], 'thumbnail_'+fname[1])
        keys.append([image[0], key_thm])

    return render_template('image/image_list.html',
                               title='Image List',
                               mybucket=mybucket,
                               keys=keys,
                               user_id=user_id)

@webapp.route('/image_view/<int:user_id>_<int:img_id>')
def image_view(user_id, img_id):
    cnx = get_db()
    cursor = cnx.cursor()

    query = ('SELECT key1,key2,key3,key4 FROM images WHERE id=%s')
    cursor.execute(query,(img_id,))
    keys = cursor.fetchone()

    return render_template('image/image_view.html',
                               title='Image Viewer',
                               user_id=user_id,
                               mybucket=mybucket,
                               keys=keys)

@webapp.route('/image_upload/<int:user_id>')
def image_upload(user_id):
    return render_template('image/image_upload.html',
                               title='Upload a New Image',
                               user_id=user_id)

@webapp.route('/image_save/<int:user_id>', methods=['post'])
def image_save(user_id):
    if 'image' not in request.files:
        error_msg = 'Error: Missing Image!'
        return render_template('image/image_upload.html',
                                       title='Upload a New Image',
                                       user_id=user_id,
                                       error_msg=error_msg)

    image = request.files['image']

    if image.filename == '':
        error_msg = 'Error: Missing Image Name!'
        return render_template('image/image_upload.html',
                                       title='Upload a New Image',
                                       user_id=user_id,
                                       error_msg=error_msg)

    s3 = boto3.client('s3')
    keys = []

    imgname = os.path.join(tmp_path, image.filename)
    image.save(imgname)

    key1 = str(user_id) + '/' + image.filename
    s3.upload_file(imgname, mybucket, key1)
    #boto3.resource('s3').Object(bucket, key1).put(Body=image)

    keys.append(key1)


    img = Image(filename=imgname)
    
    thumbnail_img = img.clone()
    thumbnail_img.resize(160, 200)
    thumbnail_imgname = os.path.join(tmp_path, 'thumbnail_'+image.filename)    
    thumbnail_img.save(filename=thumbnail_imgname)
    
    key_thm = str(user_id) + '/' + 'thumbnail_'+image.filename
    s3.upload_file(thumbnail_imgname, mybucket, key_thm)


    flopped_img = img.clone()
    flopped_img.flop()
    flopped_imgname = os.path.join(tmp_path, 'flopped_'+image.filename)
    flopped_img.save(filename=flopped_imgname)

    key2 = str(user_id) + '/' + 'flopped_'+image.filename
    s3.upload_file(flopped_imgname, mybucket, key2)

    keys.append(key2)


    flipped_img = img.clone()
    flipped_img.flip()
    flipped_imgname = os.path.join(tmp_path, 'flipped_'+image.filename)
    flipped_img.save(filename=flipped_imgname)

    key3 = str(user_id) + '/' + 'flipped_'+image.filename
    s3.upload_file(flipped_imgname, mybucket, key3)

    keys.append(key3)
    
    
    rotated_img = img.clone()
    rotated_img.rotate(25, background=Color('green'))
    rotated_imgname = os.path.join(tmp_path, 'rotated_'+image.filename)
    rotated_img.save(filename=rotated_imgname)

    key4 = str(user_id) + '/' + 'rotated_'+image.filename
    s3.upload_file(rotated_imgname, mybucket, key4)

    keys.append(key4)


    cnx = get_db()
    cursor = cnx.cursor()

    query=('REPLACE INTO images (userId,key1,key2,key3,key4)'
               'VALUES (%s,%s,%s,%s,%s)')
    cursor.execute(query, (user_id,key1,key2,key3,key4,))
    cnx.commit()

    return render_template('image/image_view.html',
                               title='View Image',
                               user_id=user_id,
                               uploaded=True,
                               mybucket=mybucket,
                               keys=keys)
