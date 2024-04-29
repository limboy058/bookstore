import pytest
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer

import uuid


class TestSendOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_send_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_send_order_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_send_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.store_id_x = "test_send_order_store_x_id_{}".format(str(uuid.uuid1()))
        
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        self.seller=self.gen_book.return_seller()
        self.seller.create_store(self.store_id_x)
        
        yield

    def test_unmatch_send(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.buyer.add_funds(10000000000)
        code = self.buyer.payment(order_id)
        code = self.seller.send_books(self.store_id_x, order_id)
        assert code != 200

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

    def test_no_fund_send(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.buyer.payment(order_id)
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