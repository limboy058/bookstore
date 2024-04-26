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
        self.conn["user"].drop()
        self.conn["user_store"].drop()
        self.conn["store"].drop()
        self.conn["new_order"].drop()
        self.conn["new_order_detail"].drop()
        self.conn["user"]
        self.conn["user_store"]
        self.conn["store"]
        self.conn["new_order"]
        self.conn["new_order_detail"]
    def build_tables(self):
        self.conn["store"].create_index({"store_id":1})
        self.conn["store"].create_index({"book_info.translator":1})
        self.conn["store"].create_index({"book_info.publisher":1})
        self.conn["store"].create_index({"book_info.stock_level":1})
        self.conn["store"].create_index({"book_info.price":1})
        self.conn["store"].create_index({"book_info.pub_year":1})
        self.conn["store"].create_index({"book_info.id":1})
        self.conn["store"].create_index({"book_info.isbn":1})
        self.conn["store"].create_index({"book_info.author":1})
        self.conn["store"].create_index({"book_info.binding":1})
        self.conn['store'].create_index({'book_info.title':'text'})
        #self.conn['store'].create_index({})
        self.conn["user"].create_index({"user_id":1})

        self.conn["new_order"].create_index({"order_id":1})
        self.conn["new_order"].create_index({"store_id":1})
        self.conn["new_order"].create_index({"user_id":1})
        self.conn["new_order"].create_index({"order_time":1})

        self.conn["new_order_detail"].create_index({"order_id":1})

        self.conn["user_store"].create_index({"user_id":1})
        self.conn["user_store"].create_index({"store_id":1})
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

def build_db():
    global database_instance
    if(database_instance==None):
        init_database()
    database_instance.build_tables()
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