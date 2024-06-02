import os
import sqlite3 as sqlite

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
    pictures: bytes

    def __init__(self):
        self.tags = []
        self.pictures = []


class BookDB:
    def __init__(self, large: bool = False):
        parent_path = os.path.dirname(os.path.dirname(__file__))
        self.db_s = os.path.join(parent_path, "data/book.db")
        self.db_l = os.path.join(parent_path, "data/book_lx.db")
        if large:
            self.book_db = self.db_l
        else:
            self.book_db = self.db_s

    def get_book_count(self):
        conn = sqlite.connect(self.book_db)
        cursor = conn.execute("SELECT count(id) FROM book")
        row = cursor.fetchone()
        return row[0]

    def clean_book_db(self):
        conn = sqlite.connect(self.book_db)
        conn.execute("delete from book where id is NULL or price is NULL or title is NULL or pub_year<'0000' or pub_year>'9999'")
        conn.commit()
        conn.close()
        
    def get_book_info(self, start, size) -> [Book]:
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
            if(book.isbn is not None):
                book.isbn=int(book.isbn)
            book.author_intro = row[12]
            book.book_intro = row[13]
            book.content = row[14]
            tags = row[15]

            # image = Image.open(BytesIO(picture))
            # image.show()

            for tag in tags.split("\n"):
                if tag.strip() != "":
                    book.tags.append(tag)

            if row[16] is not None:
                encode_str = base64.b64encode(row[16]).decode("utf-8")
                book.pictures=encode_str

            books.append(book)
            # print(tags.decode('utf-8'))

            # print(book.tags, len(book.picture))
            # print(book)
            # print(tags)

        return books


# if __name__=='__main__':
#     b=BookDB()
#     b.get_book_info(10,3)