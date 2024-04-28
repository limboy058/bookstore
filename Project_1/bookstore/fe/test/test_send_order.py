import pytest
import sys
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer

import uuid


class TestSendOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_send_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_send_order_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_send_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.seller_id_x = "test_send_order_seller_id_x_{}".format(str(uuid.uuid1()))
        self.store_id_x = "test_send_order_store_id_x_{}".format(str(uuid.uuid1()))
        self.buyer_id_x = "test_send_order_buyer_id_x_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id_x, self.store_id_x)
        self.password_x = self.seller_id_x
        self.buyer_x = register_new_buyer(self.buyer_id_x, self.password_x)
        self.gen_book_x = GenBook(self.seller_id_x, self.store_id_x)
        self.seller=self.gen_book.return_seller()
        self.seller_x=self.gen_book.return_seller()
        
        yield

    def test_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.buyer.add_funds(10000000000)
        code = self.buyer.payment(order_id)
        code = self.seller.send_books(self.store_id, order_id)
        assert code == 200

    def test_not_paid_send(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.buyer.add_funds(10000000000)
        code = self.seller.send_books(self.store_id, order_id)
        assert code != 200

    def test_error_order_id_send(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.buyer.add_funds(10000000000)
        code = self.buyer.payment(order_id)
        order_id = order_id + "_x"
        code = self.seller.send_books(self.store_id, order_id)
        assert code != 200

    def test_error_store_id_send(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.buyer.add_funds(10000000000)
        code = self.buyer.payment(order_id)
        self.store_id = self.store_id + "_x"
        code = self.seller.send_books(self.store_id, order_id)
        assert code != 200

    def test_unmatch_store_id_send(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False, high_stock_level=True
        )
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code, order_id_x = self.buyer.new_order(self.store_id_x, buy_book_id_list)
        assert code == 200
        code = self.buyer.add_funds(10000000000)
        code = self.buyer.payment(order_id)
        code = self.buyer_x.add_funds(10000000000)
        code = self.buyer_x.payment(order_id_x)
        code = self.seller.send_books(self.store_id_x, order_id)
        assert code != 200