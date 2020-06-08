from flask import Blueprint, render_template, request, redirect, session, jsonify, flash, url_for, abort
from functools import wraps
from flask import session
import hashlib
import json
from datetime import datetime
#custom imports
from .models import Users
user_object = Users()
portal = Blueprint("portal", __name__, template_folder='../template', static_folder='../static',
                   static_url_path='../static')


@portal.errorhandler(404)
def page_not_found(error):
    return render_template('portal/404.html'), 404




@portal.route('/')
def index():
    print('called')
    return render_template('portal/home.html')


@portal.route('/profile')
def profile():
    user=user_object.get_user_profile()
    return render_template('portal/profile.html',user=user)


@portal.route('/signup', methods=['POST','GET'])
def signup():
    try:
        if session['logged_in']==True:
            return redirect(url_for("portal.dashboard"))
        if request.method == 'POST':
            #x = request.get_json(force=True)
            email= request.form.get('email')
            name= request.form.get('name')
            password= request.form.get('password')
            user={
                "username":email,
                "name":name,
                "password":password,
                "phone":None,
                "resume":None,
                "profile_picture":None,
                "address":None
            }
            registration_status = user_object.save_user(user)
            if registration_status == True:
                return redirect(url_for("portal.dashboard"))
            else:
                flash(registration_status)
                return render_template('portal/signup.html', TOPIC_DICT = TOPIC_DICT)
        else:
            return render_template('portal/signup.html')
    except Exception as error:
        print(error)
        return render_template('portal/signup.html')


@portal.route('/signin', methods = ['GET', 'POST'])
def signin():
    try:
        print(session['logged_in'])
        if session['logged_in']==True:
            return redirect(url_for("portal.dashboard"))
        if request.method == 'POST':
            #x = request.get_json(force=True)
            email= request.form.get('email')
            password= request.form.get('password')
            
            login_status = user_object.login_user(email,password)
            if login_status==True:
                return redirect(url_for("portal.dashboard"))
            else:
                flash(login_status)
                return render_template('portal/signin.html', TOPIC_DICT = TOPIC_DICT)
        else:
            return render_template('portal/signin.html')
    except Exception as error:
        print(error)
        return render_template('portal/signin.html')


@portal.route('/logout', methods=['POST','GET'])
def logout():
    try:
        session['logged_in']=False
        session["username"] = None
        session["name"] = None
        session["user_type"] = None
        session['id'] = None
        return redirect(url_for('portal.signin'))
    except Exception as error:
        print(error)
        return redirect(url_for('portal.signin'))

