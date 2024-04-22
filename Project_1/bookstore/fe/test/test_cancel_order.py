import pytest

from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
import uuid


class TestCancelOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_new_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_new_order_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_new_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        # ok, buy_book_id_list = self.gen_book.gen(
        #     non_exist_book_id=False, low_stock_level=False
        # )
        # code, ok, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        yield

    def test_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        code, ok, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert ok
        code, _ = self.buyer.cancel(self.order_id)
        assert code == 200

    def test_non_exist_order_id(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        code, ok, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert ok
        self.order_id = self.order_id + "_x"
        code, _ = self.buyer.cancel(self.order_id)
        assert code != 200

    def test_non_exist_user_id(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        code, ok, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert ok
        self.order_id = self.user_id + "_x"
        code, _ = self.buyer.cancel(self.order_id)
        assert code != 200


    def test_non_prossessing_order_id(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        code, ok, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert ok
        code, _ = self.buyer.cancel(self.order_id)
        code, _ = self.buyer.cancel(self.order_id)
        assert code != 200
