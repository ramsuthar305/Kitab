from flask import Blueprint, render_template, request, redirect, session, jsonify, flash, url_for, abort, Response
from functools import wraps
from flask import session
import hashlib
import json
from datetime import datetime
#custom imports
from .models import Books
book_object = Books()
admin = Blueprint("admin", __name__, template_folder='../template', static_folder='../static',
                   static_url_path='../static')


@admin.errorhandler(404)
def page_not_found(error):
    return render_template('admin/404.html'), 404




@admin.route('/')
def index():
    return render_template('admin/home.html')
    


@admin.route('/new_book', methods=['POST','GET'])
def new_book():
    try:
        if request.method == 'POST':
            #x = request.get_json(force=True)
            genres=['Romance','Mystery','Biography','Horror','Science fiction']
            print
            title= request.form.get('title')
            author= request.form.get('author')
            genre= request.form.get('genre')
            description= request.form.get('description')
            front_cover= request.form.get('front_cover')
            back_cover= request.form.get('back_cover')
            qty= request.form.get('quantity')
            price= request.form.get('price')
           
            book={
                "title":title,
                "author":author,
                "genre":genres[int(genre)-1],
                "description":description,
                "front_cover":front_cover,
                "back_cover":back_cover,
                "qty":qty,
                "price":price,
                "created_on":datetime.now(),
                "last_login":datetime.now(),
            }
            print(book)
            stock_status = book_object.save_book(book)
            if stock_status == True:
                return redirect(url_for("admin.index"))
            else:
                flash(stock_status)
                return render_template('admin/home.html')
        else:
            return render_template('admin/home.html')
    except Exception as error:
        print(error)
        return render_template('admin/home.html')

@admin.route('/get_books',methods=['GET'])
def get_books():
    books=book_object.get_books()
    
    return Response(json.dumps(books),  mimetype='application/json')

@admin.route('/edit_profile', methods=['POST','GET'])
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
            #         book_object.upload_file(profile_pic, file,"pic")

            
            update_data={}
            if request.form.get('new_password'):
                if request.form.get('new_password')==request.form.get('confirm_password'):
                    if book_object.check_password(request.form.get('current_password')):
                        update_data['password']=request.form.get('new_password')
                    else:
                        flash('Incorrect current password! profile edit failed.')
                        #return render_template('admin/profile.html')
                        return redirect(url_for('admin.profile'))    
            
            if request.form.get('email'):
                update_data['email']=request.form.get('email')

            if request.form.get('name'):
                update_data['name']=request.form.get('name')

            if request.form.get('address_line1'):
                update_data['address_line1']=request.form.get('address_line1')

            if request.form.get('address_line2'):
                update_data['address_line2']=request.form.get('address_line2')

            if request.form.get('city'):
                update_data['city']=request.form.get('city')

            if request.form.get('pincode'):
                update_data['pincode']=request.form.get('pincode')

            if request.form.get('state'):
                update_data['state']=request.form.get('state')

            if request.form.get('phone'):
                update_data['phone']=request.form.get('phone')

            print(update_data)
            status=book_object.user_edit(update_data)
            return redirect(url_for('admin.profile'))
    except Exception as error:
        return redirect(url_for('admin.profile'))
