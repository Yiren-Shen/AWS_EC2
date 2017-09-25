from flask import render_template, request, redirect, url_for
from app import webapp
from wand.image import Image
from wand.color import Color

import mysql.connector
from app.config import mybucket, tmp_path
import boto3
import os


@webapp.route('/test')
def test():
    return render_template('test.html',
                           title='Test Page')

@webapp.route('/test/FileUpload', methods=['post'])
def FileUpload():
    if 'uploadedfile' not in request.files:
        error_msg = 'Error: Missing Image!'
        return render_template('test.html',
                               title='Test Page',
                               error_msg=error_msg)

    image = request.files['uploadedfile']
    userID = request.form.get('userID',"")
    password = request.form.get('password',"")


    if userID =="" or password == "" or image.filename == "":
        error_msg = 'Error: All fields are required!'
        return render_template('test.html',
                               title='Test Page',
                               error_msg=error_msg)

    s3 = boto3.client('s3')

    imgname = os.path.join(tmp_path, image.filename)
    image.save(imgname)

    key1 = 'load_test/'+ userID + '/' + image.filename
    s3.upload_file(imgname, mybucket, key1)


    img = Image(filename=imgname)


    thumbnail_img = img.clone()
    thumbnail_img.resize(160, 200)
    thumbnail_imgname = os.path.join(tmp_path, 'thumbnail_'+image.filename)    
    thumbnail_img.save(filename=thumbnail_imgname)

    key_thm = 'load_test/'+ userID + '/' + 'thumbnail_'+image.filename
    s3.upload_file(thumbnail_imgname, mybucket, key_thm)


    flopped_img = img.clone()
    flopped_img.flop()
    flopped_imgname = os.path.join(tmp_path, 'flopped_'+image.filename)
    flopped_img.save(filename=flopped_imgname)

    key2 = 'load_test/'+ userID + '/' + 'flopped_'+image.filename
    s3.upload_file(flopped_imgname, mybucket, key2)



    flipped_img = img.clone()
    flipped_img.flip()
    flipped_imgname = os.path.join(tmp_path, 'flipped_'+image.filename)
    flipped_img.save(filename=flipped_imgname)

    key3 = 'load_test/'+ userID + '/' + 'flipped_'+image.filename
    s3.upload_file(flipped_imgname, mybucket, key3)


    rotated_img = img.clone()
    rotated_img.rotate(25, background=Color('green'))
    rotated_imgname = os.path.join(tmp_path, 'rotated_'+image.filename)
    rotated_img.save(filename=rotated_imgname)

    key4 = 'load_test/'+ userID + '/' + 'rotated_'+image.filename
    s3.upload_file(rotated_imgname, mybucket, key4)

    return redirect('/test')