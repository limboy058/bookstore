import requests
from urllib.parse import urljoin
from fe.access import book
from fe.access.auth import Auth

class Seller:
    def __init__(self, url_prefix, seller_id: str, password: str):
        self.url_prefix = urljoin(url_prefix, "seller/")
        self.seller_id = seller_id
        self.password = password
        self.terminal = "my terminal"
        self.auth = Auth(url_prefix)
        code, self.token = self.auth.login(self.seller_id, self.password, self.terminal)
        assert code == 200

    def create_store(self, store_id):
        json = {
            "user_id": self.seller_id,
            "store_id": store_id,
        }
        # print(simplejson.dumps(json))
        url = urljoin(self.url_prefix, "create_store")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def add_book(self, store_id: str, stock_level: int, book_info: book.Book) -> int:
        json = {
            "user_id": self.seller_id,
            "store_id": store_id,
            "book_info":book_info.__dict__,
            # "book_id":book_info.id,
            # "tags":book_info.tags,
            # "title":book_info.title,
            # "author":book_info.author,
            # "publisher":book_info.publisher,
            # "original_title":book_info.original_title,
            # "translator":book_info.translator,
            # "pub_year":book_info.pub_year,
            # "pages":book_info.pages,
            # "price":book_info.price,
            # "currency_unit":book_info.currency_unit,
            # "binding":book_info.binding,
            # "isbn":book_info.isbn,
            # "author_intro":book_info.author_intro,
            # "book_intro":book_info.book_intro,
            # "content":book_info.content,
            # "tags":book_info.tags,
            # "picture":book_info.pictures,
             "stock_level": stock_level,
        }
        # print(simplejson.dumps(json))
        url = urljoin(self.url_prefix, "add_book")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def add_stock_level(
        self, seller_id: str, store_id: str, book_id: str, add_stock_num: int
    ) -> int:
        json = {
            "user_id": seller_id,
            "store_id": store_id,
            "book_id": book_id,
            "add_stock_level": add_stock_num,
        }
        # print(simplejson.dumps(json))
        url = urljoin(self.url_prefix, "add_stock_level")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code
    