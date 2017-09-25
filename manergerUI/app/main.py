from flask import render_template
from app import webapp


@webapp.route('/')
@webapp.route('/home')
def home():
	return render_template('home.html',
	                       title='Amazon Web Services by 11')
