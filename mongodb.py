import os
from pymongo import MongoClient

class MongoDB:
    
    def __init__(self, databasename, columnname):
        mongoURL = os.getenv('MONGODB_URI')
        dbClient = MongoClient(mongoURL)
        db = dbClient[databasename]
        self.colDB = db[columnname]

    def findonedb(self, query):
        return self.colDB.find_one(query)

    def finddb(self, query):
        return self.colDB.find(query)

    def findalldb(self):
        return self.colDB.find()

    def insertonedb(self, query):
        self.colDB.insert_one(query)

    def deleteonedb(self, query):
        self.colDB.delete_one(query)