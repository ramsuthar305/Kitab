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
    return render_template('portal/home.html')
    

@portal.route('/viewall')
def viewall():
    return render_template('portal/viewall.html')

@portal.route('/cart')
def cart():
    return render_template('portal/cart.html')


@portal.route('/profile')
def profile():
    user=user_object.get_user_profile()
    return render_template('portal/profile.html',user=user)


@portal.route('/product')
def product():
    return render_template('portal/product.html')


@portal.route('/register', methods=['POST','GET'])
def register():
    try:
        if request.method == 'POST':
            #x = request.get_json(force=True)
            print
            email= request.form.get('email')
            name= request.form.get('name')
            password= request.form.get('password')
            address_line1= request.form.get('address_line1')
            address_line2= request.form.get('address_line2')
            city= request.form.get('city')
            pincode= request.form.get('pincode')
            state= request.form.get('state')
            phone= request.form.get('phone')
            user={
                "username":email,
                "email":email,
                "name":name,
                "password":password,
                "phone":phone,
                "cart":[],
                "profile_picture":None,
                "address_line1":address_line1,
                "address_line2":address_line2,
                "orders":[],
                "city":city,
                "pincode":pincode,
                "state":state,
                "created_on":datetime.now(),
                "last_login":datetime.now(),
            }
            print(user)
            registration_status = user_object.save_user(user)
            if registration_status == True:
                return redirect(url_for("portal.signin"))
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
        print('callled')
        if session.get('logged_in', False)==True:
            print(session['logged_in here'])
            return redirect(url_for("portal.index"))
        if request.method == 'POST':
            #x = request.get_json(force=True)
            email= request.form.get('email')
            password= request.form.get('password')
            print('here',email,password)
            login_status = user_object.login_user(email,password)
            print(login_status)
            if login_status==True:
                return redirect(url_for("portal.index"))
            else:
                flash(login_status)
                return render_template('portal/login.html')
        else:
            return render_template('portal/login.html')
    except Exception as error:
        print('hereerreor',error)
        return render_template('portal/login.html')


@portal.route('/logout', methods=['POST','GET'])
def logout():
    try:
        session['logged_in']=False
        session["username"] = None
        session["name"] = None
        session['id'] = None
        return redirect(url_for('portal.signin'))
    except Exception as error:
        print(error)
        return redirect(url_for('portal.signin'))

@portal.route('/edit_profile', methods=['POST','GET'])
def edit_profile():
    try:
        if request.method=='POST':
            #print("in request files", request.files)
            # if not request.files.get('profile_picture', None):
            #     pass
            # else:
            #     file=request.files['profile_picture']
            #     if file:
            #         profile_pic = {}
            #         profile_pic["filename"] = file.filename
            #         profile_pic["directory"] = session['id'] + "/profile_picture" + "/"
            #         print(file.filename)
            #         user_object.upload_file(profile_pic, file,"pic")

            
            update_data={}
            
            if request.form.get('current_password'):
                update_data['current_password']=request.form.get('current_password')
            
            if request.form.get('new_password'):
                update_data['new_password']=request.form.get('new_password')
            
            if request.form.get('confirm_password'):
                update_data['confirm_password']=request.form.get('confirm_password')
            
            if request.form.get('address'):
                update_data['address']=request.form.get('address') 
            
            # if update_data:
            #     user_object.user_edit(update_data)
            print(update_data)
            return redirect(url_for('portal.profile'))
    except Exception as error:
        return redirect(url_for('portal.profile'))
