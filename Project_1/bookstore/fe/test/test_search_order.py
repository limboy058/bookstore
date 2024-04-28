import pytest
from fe.access.auth import Auth
from fe import conf
from be.model import db_conn
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
import uuid
import random


class TestSearchOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_search_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_search_order_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_search_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.auth=Auth(conf.URL)
        self.dbconn=db_conn.DBConn()
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        self.seller=self.gen_book.return_seller()
        yield

    def test_search_orders_detail_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        tol_price=0
        for info in buy_book_id_list:
            cursor=self.dbconn.conn['store'].find_one({'book_id':info[0],'store_id':self.store_id})
            assert cursor!=None
            cur=cursor['book_info']
            cur_price=cur['price']
            tol_price+=cur_price*info[1]
            
        cursor=self.dbconn.conn['new_order'].find_one({'order_id':order_id})
        code, (book_list, price, status)= self.auth.search_order_detail(order_id)
        assert buy_book_id_list.sort() == book_list.sort()
        assert tol_price == price
        assert status=='unpaid'

    def test_user_search_order_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code, order_list= self.buyer.search_order()
        assert code == 200

    def test_user_one_order_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        order_list=list()
        order_list.append(order_id)
        code, received_list= self.buyer.search_order()
        assert order_list == received_list

    def test_user_many_orders_ok(self):
        order_list=list()
        ok, buy_book_id_list = self.gen_book.gen(
        non_exist_book_id=False, low_stock_level=False, high_stock_level=True
        )
        assert ok
        # step = int(len(buy_book_id_list)/5)
        # lst = [buy_book_id_list[i:i+step] for i in range(0, len(buy_book_id_list), step)]
        for i in range(0,5):
            code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
            assert code == 200
            order_list.append(order_id)
        code, received_list= self.buyer.search_order()
        assert order_list == received_list

    def test_seller_search_order_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code, order_list= self.seller.search_order(self.store_id)
        assert code == 200

    def test_seller_one_order_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        order_list=list()
        order_list.append(order_id)
        code, received_list= self.seller.search_order(self.store_id)
        assert order_list == received_list

    def test_seller_many_orders_ok(self):
        order_list=list()
        ok, buy_book_id_list = self.gen_book.gen(
        non_exist_book_id=False, low_stock_level=False, high_stock_level=True
        )
        assert ok
        # step = int(len(buy_book_id_list)/5)
        # lst = [buy_book_id_list[i:i+step] for i in range(0, len(buy_book_id_list), step)]
        for i in range(0,5):
            code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
            assert code == 200
            order_list.append(order_id)
        code, received_list= self.seller.search_order(self.store_id)
        assert order_list == received_list