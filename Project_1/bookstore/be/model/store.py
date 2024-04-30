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
        self.client = pymongo.MongoClient()
        self.conn = self.client['609']

    def clear_tables(self):
        self.conn["user"].drop()
        self.conn["store"].drop()
        self.conn["new_order"].drop()
        self.conn["dead_user"].drop()
        self.conn["user"]
        self.conn["store"]
        self.conn["new_order"]
        self.conn["dead_user"]

    def clean_tables(self):
        self.conn["user"].delete_many({})
        self.conn["store"].delete_many({})
        self.conn["new_order"].delete_many({})
        self.conn["dead_user"].delete_many({})

    def build_tables(self):
        self.conn["store"].create_index({"book_info.translator": 1})
        self.conn["store"].create_index({"book_info.publisher": 1})
        self.conn["store"].create_index({"stock_level": 1})
        self.conn["store"].create_index({"book_info.price": 1})
        self.conn["store"].create_index({"book_info.pub_year": 1})
        self.conn["store"].create_index({"book_info.id": 1})
        self.conn["store"].create_index({"book_info.isbn": 1})
        self.conn["store"].create_index({"book_info.author": 1})
        self.conn["store"].create_index({"book_info.binding": 1})
        self.conn['store'].create_index({'book_info.title': 'text'})
        self.conn['store'].create_index(([("store_id", 1),
                                          ("book_info.id", 1)]),
                                        unique=True)
        #self.conn['store'].create_index({})

        self.conn["user"].create_index([("user_id", 1)], unique=True)
        self.conn["user"].create_index({"stroe_id": 1})

        self.conn["dead_user"].create_index([("user_id", 1)], unique=True)

        self.conn["new_order"].create_index([("order_id", 1)], unique=True)
        self.conn["new_order"].create_index({"store_id": 1})
        self.conn["new_order"].create_index({"user_id": 1})
        self.conn["new_order"].create_index({"order_time": 1})
        self.conn["new_order"].create_index({"seller_id": 1})

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
    if (database_instance == None):
        init_database()
    return database_instance.get_db_conn()


def get_db_client():
    global database_instance
    if (database_instance == None):
        init_database()
    return database_instance.get_db_client()


def clear_db():
    global database_instance
    if (database_instance == None):
        init_database()
    database_instance.clear_tables()


def build_db():
    global database_instance
    if (database_instance == None):
        init_database()
    database_instance.build_tables()


def clean_db():
    global database_instance
    if (database_instance == None):
        init_database()
    database_instance.clean_tables()
