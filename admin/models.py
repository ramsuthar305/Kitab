import hashlib
from app import *
from flask import session
import os 
from pyresparser import ResumeParser
from bson import ObjectId


class Books:
	def __init__(self):
		self.mongo = mongo.db

	def check_user_exists(self, username):
		result = self.mongo.users.find_one({"$or": [{"username": username}, {"phone": username}]})
		if result:
			return True
		else:
			return False

	def save_book(self,book):
		try:
			result = mongo.db.books.insert_one({
			"title":book["title"],
			"author":book["author"],
			"genre":book["genre"],
			"description":book["description"],
			"front_cover":book["front_cover"],
			"back_cover":book["back_cover"],
			"qty":book["qty"],
			"price":book["price"],
			"created_on":book["created_on"],
			"last_login":book["last_login"]
			})
			if result:
				print(result)
				return True
			else:
				return "Opps something went wrong"

		except Exception as error:
			print(error)
			if error.code == 11000:
				return "Book already exists"

	def get_books(self):
		genres=list(self.mongo.genres.find())
		print(genres[0]['genres'])
		books=[]
		for i in genres[0]['genres']:
			temp={}
			temp['genre']=i
			temp['books']=list(self.mongo.books.find({"genre":i}))
			books.append(temp)
		return books
	
	def get_book_by_id(self,id):
		book=self.mongo.books.find_one({"_id":id})
		return book

	def get_books_by_genre(self,genre):
		books=list(self.mongo.books.find({"genre":genre}))
		return books

	def user_edit(self, data):
		try:
			result = self.mongo.users.update_one({"_id": session["id"]}, {"$set": data})
			print(result)
			return True
		except Exception as error:
			print(error)
			return False