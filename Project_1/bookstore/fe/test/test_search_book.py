import time
import sys
import json
sys.path.append("D:/dbproject/Project_1/bookstore")
import pytest
import random
from fe.access.auth import Auth
from fe import conf
import pytest
from fe import conf
from fe.access.new_seller import register_new_seller
from fe.access import book
import uuid


class TestSearchBook:

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):

        self.seller_id = "test_add_books_seller_id_{}".format(str(
            uuid.uuid1()))
        self.store_id = "test_add_books_store_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.seller = register_new_seller(self.seller_id, self.password)
        self.auth = Auth(conf.URL)
        code = self.seller.create_store(self.store_id)
        assert code == 200
        self.test_books_num = 50
        book_db = book.BookDB(conf.Use_Large_DB)
        self.books = book_db.get_book_info(0, self.test_books_num)
        cnt = 0
        for i in range(0, len(self.books)):
            self.books[i].title = 'test name ' + str(i) + ' hey'
            self.books[i].picture = None
            code = self.seller.add_book(self.store_id, cnt, self.books[i])
            assert code == 200
            cnt += 1

    def test_search_book_id(self):
        for b in self.books:
            if (b.id == None):
                continue
            #test id
            book_id = b.id
            code, lst, _ = self.auth.searchbook(page_no=0,
                                                page_size=self.test_books_num,
                                                id=book_id)
            assert code == 200
            assert (len(lst) > 0)
            for i in lst:
                res = json.loads(i)
                tmp_judge = False
                assert (res['book_id'] == book_id)

    def test_search_book_title(self):
        cnt = 0
        for b in self.books:
            if (b.title == None or b.title == ""):
                continue
            #test title
            foozytitle = str(cnt)
            code, lst, msg = self.auth.searchbook(
                page_no=0,
                page_size=self.test_books_num,
                foozytitle=foozytitle)
            assert (code == 200 or (msg and foozytitle and b.title and 0))
            assert (len(lst) > 0 or (msg and foozytitle and b.title and 0))
            for i in lst:
                res = json.loads(i)
                assert (str(res['title']).find(foozytitle) != -1)

    def test_search_book_author(self):
        for b in self.books:
            #test author
            author = b.author
            if (author != None):
                code, lst, _ = self.auth.searchbook(
                    page_no=0, page_size=self.test_books_num, author=author)
                assert code == 200
                assert (len(lst) > 0)
                for i in lst:
                    res = json.loads(i)
                    assert (res['author'] == author)

    def test_search_book_tags(self):
        for b in self.books:
            #test tags
            reqtags = list(b.tags)
            while (len(reqtags) > 2):
                reqtags.pop()
            code, lst, _ = self.auth.searchbook(page_no=0,
                                                page_size=self.test_books_num,
                                                reqtags=reqtags)
            assert code == 200
            assert (len(lst) > 0)
            for i in lst:
                res = json.loads(i)
                tags_copy = reqtags.copy()
                for j in res['tags']:
                    if (j in tags_copy):
                        while (tags_copy.count(j)):
                            tags_copy.remove(j)
                assert (len(tags_copy) == 0)

    def test_search_book_isbn(self):
        for b in self.books:
            #test isbn
            isbn = b.isbn
            if (isbn != None):
                code, lst, _ = self.auth.searchbook(
                    page_no=0, page_size=self.test_books_num, isbn=isbn)
                assert code == 200
                assert (len(lst) > 0)
                for i in lst:
                    res = json.loads(i)
                    assert (res['isbn'] == isbn)

    def test_search_book_price(self):
        for b in self.books:
            #test price
            lowest_price = b.price
            code, lst, _ = self.auth.searchbook(page_no=0,
                                                page_size=self.test_books_num,
                                                lowest_price=lowest_price)
            assert code == 200
            assert (len(lst) > 0)
            for i in lst:
                res = json.loads(i)
                assert (res['price'] >= lowest_price)

            highest_price = b.price
            code, lst, _ = self.auth.searchbook(page_no=0,
                                                page_size=self.test_books_num,
                                                highest_price=highest_price)
            assert code == 200
            assert (len(lst) > 0)
            for i in lst:
                res = json.loads(i)
                assert (res['price'] <= highest_price)

    def test_search_book_pub_year(self):
        for b in self.books:
            #test pub year
            if (b.pub_year != None):
                lowest_year = b.pub_year[0:4]
                code, lst, _ = self.auth.searchbook(
                    page_no=0,
                    page_size=self.test_books_num,
                    lowest_pub_year=lowest_year)
                assert code == 200
                assert (len(lst) > 0)
                for i in lst:
                    res = json.loads(i)
                    assert (res['pub_year'][0:4] >= lowest_year)

                highest_year = b.pub_year[0:4]
                code, lst, _ = self.auth.searchbook(
                    page_no=0,
                    page_size=self.test_books_num,
                    highest_pub_year=highest_year)
                assert code == 200
                assert (len(lst) > 0)
                for i in lst:
                    res = json.loads(i)
                    assert (res['pub_year'][0:4] <= highest_year)

    def test_search_book_store_id(self):
        for b in self.books:
            #test store_id
            code, lst, _ = self.auth.searchbook(page_no=0,
                                                page_size=self.test_books_num,
                                                store_id=self.store_id)
            assert code == 200
            assert (len(lst) > 0)
            for i in lst:
                res = json.loads(i)
                assert (res['store_id'] == self.store_id)

    def test_search_book_publisher(self):
        for b in self.books:
            #test publisher
            publisher = b.publisher
            if (publisher != None):
                if (publisher is not None):
                    code, lst, _ = self.auth.searchbook(
                        page_no=0,
                        page_size=self.test_books_num,
                        publisher=publisher)
                    assert code == 200
                    assert (len(lst) > 0)
                    for i in lst:
                        res = json.loads(i)
                        assert (res['publisher'] == publisher)

    def test_search_book_translator(self):
        for b in self.books:
            #test translator
            translator = b.translator
            if (translator != None):
                code, lst, _ = self.auth.searchbook(
                    page_no=0,
                    page_size=self.test_books_num,
                    translator=translator)
                assert code == 200
                assert (len(lst) > 0)
                for i in lst:
                    res = json.loads(i)
                    assert (res['translator'] == translator)

    def test_search_book_binding(self):
        for b in self.books:
            #test binding
            binding = b.binding
            if (binding != None):
                code, lst, _ = self.auth.searchbook(
                    page_no=0, page_size=self.test_books_num, binding=binding)
                assert code == 200
                assert (len(lst) > 0)
                for i in lst:
                    res = json.loads(i)
                    assert (res['binding'] == binding)

    def test_search_book_stock(self):
        for b in self.books:
            #test having_stock
            code, lst, _ = self.auth.searchbook(page_no=0,
                                                page_size=self.test_books_num,
                                                having_stock=True,
                                                store_id=self.store_id)
            assert code == 200
            assert (len(lst) == self.test_books_num - 1)

    def test_search_book_non_exist_store(self):
        for b in self.books:
            #test non exist store
            tmp_store_id = str(uuid.uuid1()) + "1"
            code, lst, _ = self.auth.searchbook(page_no=0,
                                                page_size=self.test_books_num,
                                                store_id=tmp_store_id)
            assert code == 200
            assert (len(lst) == 0)

    def test_search_book_with_order(self):
        for b in self.books:
            #test order
            code, lst, _ = self.auth.searchbook(
                page_no=0,
                page_size=self.test_books_num,
                order_by_method=['stock_level', 1])
            assert code == 200
            assert (len(lst) == self.test_books_num)
            las_stock_level = 0
            for i in lst:
                res = json.loads(i)
                assert (res['stock_level'] >= las_stock_level)
                las_stock_level = res['stock_level']

            code, lst, _ = self.auth.searchbook(page_no=0,
                                                page_size=self.test_books_num,
                                                order_by_method=['price', -1])
            assert code == 200
            assert (len(lst) == self.test_books_num)
            las_price = -1
            for i in lst:
                res = json.loads(i)
                assert (res['price'] <= las_price or las_price == -1)
                las_price = res['price']

            code, lst, _ = self.auth.searchbook(page_no=0,
                                                page_size=self.test_books_num,
                                                order_by_method=['sales', -1])
            assert code == 200
            assert (len(lst) == self.test_books_num)
            las_sales = -1
            for i in lst:
                res = json.loads(i)
                assert (res['sales'] <= las_sales or las_sales == -1)
                las_price = res['sales']


# if __name__=="__main__":
#     test=TestSearchBook()
#     test.pre_run_initialization()
#     # test.test_search_book_isbn()
#     # test.test_search_book_non_exist_store()
#     # test.test_search_book_price()
#     # test.test_search_book_pub_year()
#     test.test_search_book_stock()
#     test.test_search_book_store_id()
#     #test.test_search_book_tags()