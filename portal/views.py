from flask import Blueprint, render_template, request, redirect, session, jsonify, flash, url_for, abort
from functools import wraps
from flask import session
import hashlib
import json
from datetime import datetime
from bson import ObjectId
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
#custom imports
from .models import Users
from .models import Orders
from admin.models import Books

book_object = Books()
user_object = Users()
order_object = Orders()
portal = Blueprint("portal", __name__, template_folder='../template', static_folder='../static',
                   static_url_path='../static')


@portal.errorhandler(404)
def page_not_found(error):
    return render_template('portal/404.html'), 404




@portal.route('/')
def index():
    books = book_object.get_books()
    print(books)
    return render_template('portal/home.html',books=books)
    

@portal.route('/viewall')
def viewall():
    books=book_object.get_books_by_genre(request.args.get('genre'))
    return render_template('portal/viewall.html',books=books)

@portal.route('/cart')
def cart():
    cart=user_object.get_user_cart()
    total=0
    books=[]
    detailed_cart={}
    for item in cart:
        book=book_object.get_book_by_id(item['_id'])
        print(book)
        book['qty']=item['qty']
        books.append(book)
        total=total+int(book['price'])*int(item['qty'])
    detailed_cart['books']=books
    detailed_cart['total']=total
    detailed_cart['gst']=(total*18)/100
    detailed_cart['net_total']=((total*18)/100)+total
    return render_template('portal/cart.html',detailed_cart=detailed_cart)


@portal.route('/profile')
def profile():
    user=user_object.get_user_profile()
    return render_template('portal/profile.html',user=user)


@portal.route('/product')
def product():
    book=book_object.get_book_by_id(ObjectId(request.args.get('book_id')))
    print(book)
    return render_template('portal/product.html',book=book)

@portal.route('/add_to_cart',methods=["POST"])
def add_to_cart():
    try:
        id=request.get_data()
        print('id:',type(id.decode("utf-8")))
        status=user_object.add_item_cart(id.decode("utf-8"))
        if status==True:
            res={"status":"OK","length":str(user_object.cart_length())}
            return jsonify(res)
        else:
            res={"status":"ERROR","error":status}
            return jsonify(res)
    except Exception as e:
        print(e)
        
@portal.route('/cart_length',methods=["GET"])
def cart_length():
    try:
        res={"status":"OK","length":str(user_object.cart_length())}
        return jsonify(res)
    except Exception as error:
        res={"status":"ERROR","error":error}
        return jsonify(res)

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
            remember_me=request.form.get('remember')
            if remember_me=="on":
                session["remember_me"]=True
            else:
                session["remember_me"]=False

            print('here',email,remember_me)
            login_status = user_object.login_user(email,password)
            print(login_status)
            if login_status==True:
                return redirect(url_for("portal.index"))
            elif login_status==False:
                flash("Invalid credentials")
                return render_template('portal/login.html')
            else:
                flash(login_status)
                return render_template('portal/login.html')
        else:
            return render_template('portal/login.html')
    except Exception as error:
        print('hereerreor',error)
        return render_template('portal/login.html')

@portal.route('/closing', methods=['POST','GET'])
def closing():
    print("Calling")
    if not session['remember_me']:
        session['logged_in']=False
        session["username"] = None
        session["name"] = None
        session['id'] = None
    return "done"

@portal.route('/change_qty',methods=['GET','POST'])
def change_qty():
    data=request.get_data()
    data=json.loads(data) 
    if data['type']=='add':
        new_qty=user_object.add_qty(data['id'])
    else:
        new_qty=user_object.minus_qty(data['id'])
    return jsonify(new_qty)

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
            if request.form.get('new_password'):
                if request.form.get('new_password')==request.form.get('confirm_password'):
                    if user_object.check_password(request.form.get('current_password')):
                        update_data['password']=request.form.get('new_password')
                    else:
                        flash('Incorrect current password! profile edit failed.')
                        #return render_template('portal/profile.html')
                        return redirect(url_for('portal.profile'))    
            
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
            status=user_object.user_edit(update_data)
            return redirect(url_for('portal.profile'))
    except Exception as error:
        return redirect(url_for('portal.profile'))

@portal.route('/checkout',methods=["GET"])
def checkout():
    cart=user_object.get_user_cart()
    total=0
    books=[]
    detailed_cart={}
    message="Your order has been placed here your purchase record\n"
    for item in cart:
        book=book_object.get_book_by_id(item['_id'])
        print(book)
        book['qty']=item['qty']
        books.append(book)
        message=message+"{} by {} qty: {} | price: {} | total:{}\n".format(book['title'],book['author'],book['qty'],book['price'],int(book['qty'])*int(book['price']))
        total=total+int(book['price'])*int(item['qty'])
    detailed_cart['books']=books
    detailed_cart['total']=total
    detailed_cart['gst']=(total*18)/100
    detailed_cart['net_total']=((total*18)/100)+total
    message=message+"____________________________________________________________\n Total: {}\n GST 18%: {}\n Net total:{}".format(detailed_cart['total'],detailed_cart['gst'],detailed_cart['net_total'])
    send_email(session["id"],message,"Order placed")
    order_object.place_order(cart,detailed_cart)
    return redirect(url_for('portal.cart'))

@portal.route('/forget_password',methods=["GET","POST"])
def forget_password():
    if request.method=="POST":
        email=request.form.get("email")
        lettersAndDigits = string.ascii_letters + string.digits
        new_password=''.join((random.choice(lettersAndDigits) for i in range(9)))
        status=user_object.forget_password(new_password,email)
        if status==True:
            message="Hello, your new password for Kitab.com account is "+new_password
            send_email("ramsuthar305@gmail.com",message,"New password")
            flash("New password has been sent to the registered email id")
            return redirect(url_for('portal.forget_password'))
        else:
            flash("Something went wrong")
            return redirect(url_for('portal.signin'))
    else:
        return render_template("portal/forget_password.html")

def send_email(to,msg,subject):
    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    sender_email = "kitaab.info123@gmail.com"
    receiver_email = to
    password = "123@cnd@"
    message='Subject:'+subject+"\n\n"+msg 
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted 
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)