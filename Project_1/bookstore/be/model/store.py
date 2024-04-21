import logging
import os
import sqlite3 as sqlite
import threading
import pymongo

class Store:
    database: str

    def __init__(self):
        #self.database = os.path.join(db_path, "be.db")
        #self.bookdatabase=os.path.join(db_path, "book.db")
        self.client= pymongo.MongoClient()
        self.conn=self.client['609']
    def clear_tables(self):
        self.conn["user"].delete_many({})
        self.conn["user_store"].delete_many({})
        self.conn["store"].delete_many({})
        self.conn["new_order"].delete_many({})
        self.conn["new_order_detail"].delete_many({})
    def get_db_client(self):
         return self.client

    def get_db_conn(self):
        return self.conn

database_instance: Store = None
# global variable for database sync
init_completed_event = threading.Event()


def init_database():
    global database_instance
    database_instance = Store()


def get_db_conn():
    global database_instance
    if(database_instance==None):
         init_database()
    return database_instance.get_db_conn()

def get_db_client():
    global database_instance
    if(database_instance==None):
        init_database()
    return database_instance.get_db_client()

def clear_db():
    global database_instance
    if(database_instance==None):
        init_database()
    database_instance.clear_tables()

# if __name__ == "__main__":

#     init_database()
#     clear_db()
#     conn=get_db_conn()
#     client=get_db_client()
#     session=client.start_session()
#     session.start_transaction()
#     conn['user'].insert_one({'name':'test','user_id':1234},session=session)
#     conn['user'].insert_one({'name':'test'},session=session)
#     session.commit_transaction()
#     session.start_transaction()
#     conn['user'].insert_one({'name':'test','user_id':1234},session=session)
#     conn['user'].insert_one({'name':'test'},session=session)
#     session.abort_transaction()
#     for i in conn['user'].find():
#         print(i)
#     session.end_session()