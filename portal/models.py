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

	def save_user(self,user):
		try:
			result = mongo.db.users.insert_one({
				"_id":user['username'],
				"username":user['username'],
				"password":user['password'],
				"phone":user['phone'],
				"address":user['address'],
				"name":user['name'],
				"resume":user['resume'],
				"profile_picture":user['profile_picture'],
				"user_type":"normal"
			})
			if result:
				print(result)
				session["username"] = user["username"]
				session["name"] = user["name"]
				session["logged_in"] = True
				session["user_type"] = "normal"
				session['id'] = str(user["username"])
				return True

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
				session["user_type"] = login_result['user_type']
				session['id'] = str(login_result["_id"])
				return True
			else:
				return "User does not exist"
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

	