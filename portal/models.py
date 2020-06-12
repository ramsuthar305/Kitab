import hashlib
from app import *
from flask import session
import os 
from pyresparser import ResumeParser
from bson import ObjectId


class Users:
	def __init__(self):
		self.mongo = mongo.db

	def check_user_exists(self, username):
		result = self.mongo.users.find_one({"$or": [{"username": username}, {"phone": username}]})
		if result:
			return True
		else:
			return False
	
	def check_password(self,password):
		result=self.mongo.users.find_one({"password":password})
		if result:
			return True
		else:
			return False

	def save_user(self,user):
		try:
			result = mongo.db.users.insert_one({
				"_id":user['username'],
				"username":user["email"],
                "name":user["name"],
                "password":user["password"],
                "phone":user["phone"],
                "cart":user["cart"],
                "profile_picture":user["profile_picture"],
                "address_line1":user["address_line1"],
                "address_line2":user["address_line2"],
                "orders":user["orders"],
                "city":user["city"],
                "pincode":user["pincode"],
                "state":user["state"],
                "created_on":user["created_on"],
                "last_login":user["last_login"],
			})
			if result:
				print(result)
				return True
			else:
				return "Opps something went wrong"

		except Exception as error:
			print(error)
			if error.code == 11000:
				return "User already exists"


	def login_user(self, username, password):
		try:
			login_result = self.mongo.users.find_one(
				{"$and": [{"$or": [{"username": username}, {"phone": username}]},
						  {"password": password}]})
			if login_result is not None:
				session["username"] = login_result["username"]
				session["name"] = login_result["name"]
				session["logged_in"] = True
				session['id'] = str(login_result["_id"])
				return True
			else:
				return False
		except Exception as error:
			return error

	def get_user_profile(self):
		try:
			user_profile=self.mongo.users.find_one({"username": session["username"]})
			return (user_profile)
		except Exception as error:
			print(error)

	def upload_file(self, file_data, file, file_type):
		try:
			print('called')
			if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'] + file_data["directory"])):
				os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'] + file_data["directory"]))
			file_path = os.path.join(app.config['UPLOAD_FOLDER'] + file_data["directory"])
			file.save(file_path + file_data["filename"])
			file_result = os.path.exists(file_path + file_data["filename"])
			print(file_result)
			
			if file_result:
				file_data["file_path"] = file_path.split("static/")[1]
				
				if file_type=="pic":
					if os.path.exists(file_data["file_path"]):
						os.remove(file_data["file_path"])
					result = self.mongo.users.update_one({"_id": session["id"]}, {"$set": {"profile_picture":file_data["file_path"] + file_data["filename"]}})
			
				if file_type=="resume":
					if os.path.exists(file_data["file_path"]):
						os.remove(file_data["file_path"])
					print(file_data['file_path'])
					data = ResumeParser(os.path.join(app.config['UPLOAD_FOLDER'] + file_data["directory"]+file_data["filename"])).get_extracted_data()
					result = self.mongo.users.update_one({"_id": session["id"]}, {"$set": {"resume":file_data["file_path"] + file_data["filename"],"skills":data["skills"]}})
			return True
		except Exception as error:
			print(error)
			return True

	def add_item_cart(self,book_id):
		try:
			book_exists = self.mongo.users.find_one({"$and": [{"_id": session["id"]}, {"cart._id": ObjectId(book_id)}]})
			if book_exists is not None:
				return "Book already exists in the cart"
			book={"_id":ObjectId(book_id),"qty":1}
			self.mongo.users.update_one({"_id": session["id"]},{ "$push": { "cart": book } })
			return True
		except Exception as error:
			print(error)
			if error.code == 11000:
				return "Book already exists in the cart"
			else:
				return error

	def cart_length(self):
		try:
			user=self.mongo.users.find_one({"_id": session["id"]})
			return len(user['cart'])
		except Exception as error:
			print(error)

	def get_user_cart(self):
		try:
			user=self.mongo.users.find_one({"_id": session["id"]})
			return user['cart']
		except Exception as error:
			print(error)

	def get_current_qty(self,id):
		user_cart=self.mongo.users.find_one({"_id":session["id"]},{"cart":1})
		self.current_qty=0
		for item in user_cart['cart']:
			if item["_id"]==ObjectId(id):
				self.current_qty=item['qty']
		return self.current_qty

	def add_qty(self,id):
		#try:
		self.curren_qty=self.get_current_qty(id)
		
		print('This is current qty: ',type(self.current_qty))
		user=self.mongo.users.update({"_id":session["id"], "cart":{"$elemMatch":{"_id":ObjectId(id)}}},{"$set":{"cart.$.qty":self.current_qty+1}})
		return {'status':True,'qty':self.current_qty+1}

	def minus_qty(self,id):
		#try:
		self.curren_qty=self.get_current_qty(id)
		print('This is current qty: ',type(self.current_qty))
		book=self.mongo.books.find_one({"_id":ObjectId(id)})
		print(book)
		if int(book['qty'])-self.curren_qty > 0:
			if self.curren_qty-1==0:
				self.mongo.users.update({"_id":session["id"]},{"$pull":{"cart":{"_id":ObjectId(id)}}})
				return {'status':True,'qty':self.current_qty-1}
			elif not self.curren_qty-1 < 0:
				user=self.mongo.users.update({"_id":session["id"], "cart":{"$elemMatch":{"_id":ObjectId(id)}}},{"$set":{"cart.$.qty":self.current_qty-1}})
				return {'status':True,'qty':self.current_qty-1}
			else:
				return {'status':False,'qty':self.curren_qty}
		else:
			return {'status':False,error:"Books out of stock"}


	def user_edit(self, data):
		try:
			result = self.mongo.users.update_one({"_id": session["id"]}, {"$set": data})
			print(result)
			return True
		except Exception as error:
			print(error)
			return False