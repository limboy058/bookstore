import os
import sqlite3 as sqlite
import random
import base64
import simplejson as json


class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    currency_unit: str
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: [str]
    pictures: [bytes]

    def __init__(self):
        self.tags = []
        self.pictures = []


class BookDB:
    def __init__(self, large: bool = False):
        parent_path = os.path.dirname(os.path.dirname(__file__))
        self.db_s = os.path.join(parent_path, "data/book.db")
        self.db_l = os.path.join(parent_path, "data/book_lx.db")
        print(self.db_s)
        if large:
            self.book_db = self.db_l
        else:
            self.book_db = self.db_s

    def get_book_count(self):
        conn = sqlite.connect(self.book_db)
        cursor = conn.execute("SELECT count(id) FROM book")
        row = cursor.fetchone()
        return row[0]

    def get_book_info(self,start, size) -> [Book]:
        books = []
        conn = sqlite.connect(self.book_db)
        cursor = conn.execute(
            "SELECT id, title, author, "
            "publisher, original_title, "
            "translator, pub_year, pages, "
            "price, currency_unit, binding, "
            "isbn, author_intro, book_intro, "
            "content, tags, picture FROM book ORDER BY id "
            "LIMIT ? OFFSET ?",
            (size, start),
        )
        for row in cursor:
            book = Book()
            book.id = row[0]
            book.title = row[1]
            book.author = row[2]
            book.publisher = row[3]
            book.original_title = row[4]
            book.translator = row[5]
            book.pub_year = row[6]
            book.pages = row[7]
            book.price = row[8]

            book.currency_unit = row[9]
            book.binding = row[10]
            book.isbn = row[11]
            book.author_intro = row[12]
            book.book_intro = row[13]
            book.content = row[14]
            tags = row[15]

            picture = row[16]

            for tag in tags.split("\n"):
                if tag.strip() != "":
                    book.tags.append(tag)
            for i in range(0, random.randint(0, 9)):
                if picture is not None:
                    encode_str = base64.b64encode(picture).decode("utf-8")
                    book.pictures.append(encode_str)
            books.append(book)
            # print(tags.decode('utf-8'))

            # print(book.tags, len(book.picture))
            # print(book)
            # print(tags)

        return books
    
    def get_book_info_with_option(self, page_no, page_size,
                      foozytitle=None,
                      reqtags=None,
                      id=None,
                      isbn=None,
                      author=None,
                      lowest_price=None,
                      highest_price=None) -> [Book]:
        books = []
        conn = sqlite.connect(self.book_db)

        add_sql="where "
        if(foozytitle!=None):
            add_sql+="title like '%"+foozytitle+"%' and "
        if(reqtags!=None):
            add_sql+="("
            for tag in reqtags:
                add_sql+=" tags like '%\n"+tag+"\n%' or "#非第一个tag
                add_sql+=" tags like '"+tag+"\n%' or "#第一个tag
            add_sql=add_sql[0:len(add_sql)-3]
            add_sql+=") and "
        if(id!=None):
            add_sql+=" id="+str(id)+" and "
        if(isbn!=None):
            add_sql+=" isbn="+str(id)+" and "
        if(author!=None):
            add_sql+="author like '%"+author+"%' and "
        if(lowest_price!=None):
            add_sql+="price >="+str(lowest_price)+" and "
        if(highest_price!=None):
            add_sql+="price <="+str(highest_price)+" and "

        if(add_sql!="where "):
            add_sql=add_sql[0:len(add_sql)-4]
        else: add_sql=""
        cursor = conn.execute(
            "SELECT id, title, author, "
            "publisher, original_title, "
            "translator, pub_year, pages, "
            "price, currency_unit, binding, "
            "isbn, author_intro, book_intro, "
            "content, tags, picture FROM book "+add_sql+" ORDER BY id "
            "LIMIT ? OFFSET ?",
            (page_size, page_no*page_size),
        )
        for row in cursor:
            book = Book()
            book.id = row[0]
            book.title = row[1]
            book.author = row[2]
            book.publisher = row[3]
            book.original_title = row[4]
            book.translator = row[5]
            book.pub_year = row[6]
            book.pages = row[7]
            book.price = row[8]
            book.currency_unit = row[9]
            book.binding = row[10]
            book.isbn = row[11]
            book.author_intro = row[12]
            book.book_intro = row[13]
            book.content = row[14]
            tags = row[15]
            picture = row[16]

            for tag in tags.split("\n"):
                if tag.strip() != "":
                    book.tags.append(tag)
            for i in range(0, random.randint(0, 9)):
                if picture is not None:
                    encode_str = base64.b64encode(picture).decode("utf-8")
                    book.pictures.append(encode_str)
            books.append(book)
        return books

import pymongo
# if __name__ == "__main__":
#    bookdb=BookDB(True)
#    for i in bookdb.get_book_info_with_option(0,5,foozytitle="王子",lowest_price=1000,reqtags=["小王子"]):
#        book_info=i.__dict__
#        client= pymongo.MongoClient()
#        conn=client['609']
#        book_info=json.dumps(book_info)
#        conn['store'].update_many({},{'$set':{'book_info':book_info}})
#        break
