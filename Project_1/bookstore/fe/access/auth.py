import requests
from urllib.parse import urljoin


class Auth:
    def __init__(self, url_prefix):
        self.url_prefix = urljoin(url_prefix, "auth/")

    def login(self, user_id: str, password: str, terminal: str) -> (int, str):
        json = {"user_id": user_id, "password": password, "terminal": terminal}
        url = urljoin(self.url_prefix, "login")
        r = requests.post(url, json=json)
        return r.status_code, r.json().get("token")

    def register(self, user_id: str, password: str) -> int:
        json = {"user_id": user_id, "password": password}
        url = urljoin(self.url_prefix, "register")
        r = requests.post(url, json=json)
        return r.status_code

    def password(self, user_id: str, old_password: str, new_password: str) -> int:
        json = {
            "user_id": user_id,
            "oldPassword": old_password,
            "newPassword": new_password,
        }
        url = urljoin(self.url_prefix, "password")
        r = requests.post(url, json=json)
        return r.status_code

    def logout(self, user_id: str, token: str) -> int:
        json = {"user_id": user_id}
        headers = {"token": token}
        url = urljoin(self.url_prefix, "logout")
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def unregister(self, user_id: str, password: str) -> int:
        json = {"user_id": user_id, "password": password}
        url = urljoin(self.url_prefix, "unregister")
        r = requests.post(url, json=json)
        return r.status_code

    def searchbook(self,page_no, page_size,
                      foozytitle:str=None,
                      reqtags:str=None,
                      id:str=None,
                      isbn:str=None,
                      author:str=None,
                      lowest_price:int=None,
                      highest_price:int=None,
                      lowest_pub_year:str=None,
                      highest_pub_year:str=None,
                      store_id:str=None,
                      publisher:str=None,
                      translator:str=None,
                      binding:str=None,
                      order_by_method:list=None,
                      having_stock:bool=None
                      ):
        json = {"page_no": page_no, "page_size": page_size,"foozytitle":foozytitle,"reqtags":reqtags
        ,"id":id,"isbn":isbn,"author":author,"lowest_price":lowest_price,"highest_price":highest_price,
        "lowest_pub_year":lowest_pub_year,"highest_pub_year":highest_pub_year,"store_id":store_id,
        "publisher":publisher,"translator":translator,"binding":binding,"order_by_method":order_by_method,
        "having_stock":having_stock}
        url = urljoin(self.url_prefix, "search_book")
        r = requests.post(url, json=json)
        return r.status_code,r.json().get("book_info")
