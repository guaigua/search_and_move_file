#!/usr/bin/env python
#how to connect python with mongo
import pymongo
import urllib.parse
from pymongo import MongoClient
from pprint import pprint
email = "mailuser@gmail.com"
username = urllib.parse.quote_plus('chew')
password = urllib.parse.quote_plus('zaq12Wsx')
#Connect with Mongo Server
client = MongoClient('mongodb://%s:%s@127.0.0.1' % (username, password))
#Connect to db
db = client.iportalDevDB19
#Connect to collection
collection = db.users

# Make a query to list all the documents

for doc in collection.find():
    if doc['email'] == email:
        print (doc['_id'])