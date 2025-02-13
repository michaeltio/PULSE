from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("DB_URL"))  
db = client["MDI"] 
users_collection = db["users"]

def authenticate_user(username, password):
    print("Mencari user:", username)
    user = users_collection.find_one({"username": username})  
    if user:
        print("User ditemukan:", user)
    else:
        print("User tidak ditemukan")

    if user and user["password"] == password:
        print("Login sukses")
        return True
    print("Login gagal")
    return False

def add_user(username, password):
    print("Menambahkan user:", username)
    if users_collection.find_one({"username": username}):
        return False  
    users_collection.insert_one({"username": username, "password": password})
    return True
