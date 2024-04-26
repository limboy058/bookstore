import pytest

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
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        self.seller=self.gen_book.return_seller()
        yield

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
        non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        step = int(len(buy_book_id_list)/5)
        lst = [buy_book_id_list[i:i+step] for i in range(0, len(buy_book_id_list), step)]
        for i in range(0,5):
            code, order_id = self.buyer.new_order(self.store_id, lst[i])
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
        non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        step = int(len(buy_book_id_list)/5)
        lst = [buy_book_id_list[i:i+step] for i in range(0, len(buy_book_id_list), step)]
        for i in range(0,5):
            code, order_id = self.buyer.new_order(self.store_id, lst[i])
            assert code == 200
            order_list.append(order_id)
        code, received_list= self.seller.search_order(self.store_id)
        assert order_list == received_list