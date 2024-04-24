import time
import sys
import json
sys.path.append("D:/dbproject/Project_1/bookstore")
import pytest
import random
from fe.access.auth import Auth
from fe import conf
import pytest
from fe.access import seller
from fe import conf
from fe.access.new_seller import register_new_seller
from fe.access import book
from fe.test import test_add_book
import uuid


class TestSearchBook:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):

        self.seller_id = "test_add_books_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_add_books_store_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.seller = register_new_seller(self.seller_id, self.password)
        self.auth=Auth(conf.URL)
        code = self.seller.create_store(self.store_id)
        assert code == 200

        book_db = book.BookDB(conf.Use_Large_DB)
        self.books = book_db.get_book_info(0, 2)
        

    def test_search_book(self):
        for b in self.books:
            code = self.seller.add_book(self.store_id, 0, b)
            assert code == 200
        for b in self.books:
            # book.id = row[0]
            # book.title = row[1]
            # book.author = row[2]
            # book.publisher = row[3]
            # book.original_title = row[4]
            # book.translator = row[5]
            # book.pub_year = row[6]
            # book.pages = row[7]
            # book.price = row[8]

            # book.currency_unit = row[9]
            # book.binding = row[10]
            # book.isbn = row[11]
            # book.author_intro = row[12]
            # book.book_intro = row[13]
            # book.content = row[14]
            # tags = row[15]

            # picture = row[16]
            chartitle=b.title[int(random.random()*len(b.title))]
            foozytitle=str(chartitle)
            
            code,lst = self.auth.searchbook(page_no=0,page_size=10,foozytitle=foozytitle)
            for i in lst:
                res=json.loads(i)
                tmp_judge=False
                for j in (res['title']):
                    if(j==chartitle):
                        tmp_judge=True
                        break
                assert(tmp_judge)

            author=b.author
            code,lst = self.auth.searchbook(page_no=0,page_size=10,author=author)
            for i in lst:
                res=json.loads(i)
                tmp_judge=False
                assert(res['author']==author)


        assert code == 200

if __name__ == "__main__":
    tmp=TestSearchBook()
    tmp.pre_run_initialization()
    tmp.test_search_book()
