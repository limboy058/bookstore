import pytest
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer

import uuid


class TestreceiveOrder:

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_receive_order_seller_id_{}".format(
            str(uuid.uuid1()))
        self.store_id = "test_receive_order_store_id_{}".format(
            str(uuid.uuid1()))
        self.buyer_id = "test_receive_order_buyer_id_{}".format(
            str(uuid.uuid1()))
        self.password = self.seller_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        self.seller = self.gen_book.return_seller()

        yield

    def test_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.buyer.add_funds(10000000000)
        code = self.buyer.payment(order_id)
        code = self.seller.send_books(self.store_id, order_id)
        code = self.buyer.receive_books(order_id)
        assert code == 200

    def test_unmatch_user_id_receive(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.buyer.add_funds(10000000000)
        code = self.buyer.payment(order_id)
        code = self.seller.send_books(self.store_id, order_id)
        self.buyer.user_id = self.seller_id
        code = self.buyer.receive_books(order_id)
        assert code != 200

    def test_not_paid_receive(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.seller.send_books(self.store_id, order_id)
        code = self.buyer.receive_books(order_id)
        assert code != 200

    def test_no_fund_receive(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.buyer.payment(order_id)
        code = self.seller.send_books(self.store_id, order_id)
        code = self.buyer.receive_books(order_id)
        assert code != 200

    def test_error_order_id_receive(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.buyer.add_funds(10000000000)
        code = self.buyer.payment(order_id)
        code = self.seller.send_books(self.store_id, order_id)
        order_id = order_id + "_x"
        code = self.buyer.receive_books(order_id)
        assert code != 200

    def test_error_user_id_receive(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.buyer.add_funds(10000000000)
        code = self.buyer.payment(order_id)
        code = self.seller.send_books(self.store_id, order_id)
        self.buyer.user_id = self.buyer.user_id + "_x"
        code = self.buyer.receive_books(order_id)
        assert code != 200

    def test_no_send_receive(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.buyer.add_funds(10000000000)
        code = self.buyer.payment(order_id)
        code = self.buyer.receive_books(order_id)
        assert code != 200
