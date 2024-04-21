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
        self.init_tables()
        
    def init_tables(self):
        # try:
            conn = self.get_db_conn()
            conn["user"].delete_many({})
            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS user ("
            #     "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
            #     "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
            # )
            conn["user_store"].delete_many({})
            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS user_store("
            #     "user_id TEXT, store_id, PRIMARY KEY(user_id, store_id));"
            # )
            conn["store"].delete_many({})
            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS store( "
            #     "store_id TEXT, book_id TEXT, book_info TEXT, stock_level INTEGER,"
            #     " PRIMARY KEY(store_id, book_id))"
            # )
            conn["new_order"].delete_many({})
            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS new_order( "
            #     "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT)"
            # )
            conn["new_order_detail"].delete_many({})
            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS new_order_detail( "
            #     "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
            #     "PRIMARY KEY(order_id, book_id))"
            # )
            #conn.commit()
        # except sqlite.Error as e:
        #     logging.error(e)
        #     conn.rollback()

    def get_db_conn(self):
        return self.conn
    # def get_db_book_conn(self) -> sqlite.Connection:
    #     return sqlite.connect(self.database)


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

if __name__ == "__main__":
     init_database()
     conn=get_db_conn()
     conn['user'].insert_one({'name':'test','user_id':1234})
     conn['user'].insert_one({'name':'test'})
     for i in conn['user'].find():
          print(i)