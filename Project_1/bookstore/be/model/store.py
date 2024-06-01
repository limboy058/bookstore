import logging
import os
import sqlite3 as sqlite
import threading
import pymongo
import psycopg2
class Store:
    database: str

    def __init__(self):
        #self.database = os.path.join(db_path, "be.db")
        #self.bookdatabase=os.path.join(db_path, "book.db")
        self.user_name="mamba"
        self.user_password="out"
        #self.conn = psycopg2.connect(host="localhost",database="609A", user=self.user_name, password=self.user_password)
        
    def clear_tables(self):
        conn=self.get_db_conn()
        cur=conn.cursor()
        cur.execute("drop table if exists \"store\";")
        cur.execute("drop table if exists \"user\";")
        cur.execute("drop table if exists \"dead_user\";")
        cur.execute("drop table if exists \"new_order\";")
        cur.execute("drop table if exists \"old_order\";")
        cur.execute("drop table if exists \"order_detail\";")
        cur.execute("drop table if exists \"book_info\";")
        conn.commit()
        cur.close()
        conn.close()

    def clean_tables(self):
        conn=self.get_db_conn()
        cur=conn.cursor()
        cur.execute("delete from \"store\";")
        cur.execute("delete from \"user\";")
        cur.execute("delete from \"dead_user\";")
        cur.execute("delete from \"new_order\";")
        #cur.execute("delete from \"old_order\";")
        #cur.execute("delete from \"order_detail\";")
        cur.execute("delete from \"book_info\";")
        conn.commit()
        cur.close()
        conn.close()

    def build_tables(self):
        conn=self.get_db_conn()
        cur=conn.cursor()

        cur.execute("create table store("+
            "store_id varchar(255),user_id varchar(255),primary key(store_id)"        
        +")")
        cur.execute("create index store_user_id_idx on store using hash(user_id)")

        cur.execute("create table book_info("+
            "book_id varchar(255),store_id varchar(255),price int,stock_level int,sales int, "+
            "title TEXT,author varchar(255), tags TEXT[], "+
            "publisher varchar(255),original_title varchar(255),translator varchar(255),"+   
            "pub_year varchar(255),pages int,currency_unit varchar(255),"+         
            "binding varchar(255),isbn bigint,author_intro varchar(255),"+     
            "book_intro varchar(255),content varchar(255),picture varchar(255),"+ 
            "title_idx tsvector,"+
            " primary key(store_id,book_id)"+    
        ")")
        #对有排序需求和范围查询需求的字段做b+tree索引，只等值连接的字段做哈希索引
        cur.execute("create index book_info_book_id_idx on book_info using hash(book_id)")
        cur.execute("create index book_info_price_idx on book_info (price)")
        cur.execute("create index book_info_stock_level_idx on book_info (stock_level)")
        cur.execute("create index book_info_sales_idx on book_info (sales)")
        cur.execute("create index book_info_title_idx on book_info using GIN(title_idx)")
        cur.execute("create index book_info_tags_idx on book_info using GIN(tags)")
        cur.execute("create index book_info_author_idx on book_info using hash(author)")
        cur.execute("create index book_info_publisher_idx on book_info using hash(publisher)")
        cur.execute("create index book_info_original_title_idx on book_info using hash(original_title)")
        cur.execute("create index book_info_translator_idx on book_info using hash(translator)")
        cur.execute("create index book_info_pub_year_idx on book_info (pub_year)")
        cur.execute("create index book_info_binding_idx on book_info using hash(binding)")
        cur.execute("create index book_info_isbn_idx on book_info (isbn)")

        cur.execute("create table dead_user("+
            "user_id varchar(255),primary key(user_id)"        
        +")")

        cur.execute("create table \"user\"("+
            "user_id varchar(255),password varchar(255),balance bigint,token varchar(1023),terminal varchar(1023), primary key(user_id)"        
        +")")

        cur.execute("create table new_order("+
            "order_id varchar(255),store_id varchar(255),buyer_id varchar(255),status varchar(255),time timestamp,total_price bigint,order_detail Text, primary key(order_id)"        
        +")")


        # cur.execute("create table order_detail("+
        #     "order_id varchar(255),book_id varchar(255), count int,primary key(order_id,book_id)"        
        # +")")

        cur.close()
        conn.commit()
        conn.close()

    def get_db_conn(self):
        return psycopg2.connect(
            host="localhost",
            database="609A",
            user=self.user_name,
            password=self.user_password
        )


database_instance: Store = None
# global variable for database sync
init_completed_event = threading.Event()


def init_database():
    global database_instance
    database_instance = Store()
    #database_instance.clear_tables()#注释这一行来关掉每次建立连接清空数据
    #database_instance.build_tables()#注释这一行来关掉每次建立连接清空数据


def get_db_conn():

    global database_instance
    if (database_instance == None):
        init_database()
    return database_instance.get_db_conn()


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


# if __name__=="__main__":
#     clear_db()
#     build_db()
#     conn=get_db_conn()
#     cur=conn.cursor()
#     cur.execute("insert into dead_user values ('abc')")
#     cur.execute("select * from dead_user")
#     res=cur.fetchall()
#     for i in res:
#         print(i,len(i[0]))
