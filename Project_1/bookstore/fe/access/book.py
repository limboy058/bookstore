import os
import pymongo
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
        self.client=pymongo.MongoClient()
        self.conn=self.client['609']
        if large:
            self.book_db = self.conn['book_lx']
        else:
            self.book_db = self.conn['book']


    def clean_db(self):
        self.book_db.delete_many({
                "$or": [
                    {"id": None},
                    {"title": None},
                    {"author": None},
                    {"publisher": None},
                    {"pub_year": None},
                    {"price": None},
                    {"binding": None},
                    {"isbn": None},
                    {"tags": None},
                    {"picture": None}]})
        
    def get_book_count(self):
        return self.book_db.count_documents({})

    def get_book_info(self,start, size) -> [Book]:
        books = []
        cursor = self.book_db.aggregate([
            {"$sort": {"id": 1}},
            {"$skip": start},
            {"$limit": size},
            {"$project": {
                "id": 1, "title": 1, "author": 1,
                "publisher": 1, "original_title": 1,
                "translator": 1, "pub_year": 1, "pages": 1,
                "price": 1, "currency_unit": 1, "binding": 1,
                "isbn": 1, "author_intro": 1, "book_intro": 1,
                "content": 1, "tags": 1, "picture": 1
            }}
        ])
        for row in cursor:
            book = Book()
            book.id = row['id']
            book.title = row['title']
            book.author = row["author"]
            book.publisher = row["publisher"]
            book.original_title = row["original_title"]
            book.translator = row["translator"]
            book.pub_year = row["pub_year"]
            book.pages = row["pages"]
            book.price = row["price"]

            book.currency_unit = row["currency_unit"]
            book.binding = row["binding"]
            book.isbn = row["isbn"]
            book.author_intro = row["author_intro"]
            book.book_intro = row["book_intro"]
            book.content = row["content"]
            tags = row["tags"]
            picture=None#speed up test
            #picture = row["picture"]

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


# if __name__=='__main__':
#     bdb=BookDB()
#     for item in bdb.get_book_info(0,1000):
#         print(item.id)