import time

import pytest
# import sys
# sys.path.append('D:\\DS_bookstore\\Project_1\\bookstore')
from fe.access import auth
from fe import conf

from fe.access.new_buyer import register_new_buyer
from fe.test.gen_book_data import GenBook


class TestRegister:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.user_id = "test_register_user_{}".format(time.time())
        self.store_id = "test_payment_store_id_{}".format(time.time())
        self.password = "test_register_password_{}".format(time.time())
        self.auth = auth.Auth(conf.URL)
        yield

    def test_register_ok(self):
        code = self.auth.register(self.user_id, self.password)
        assert code == 200

    def test_unregister_ok(self):
        code = self.auth.register(self.user_id, self.password)
        assert code == 200

        code = self.auth.unregister(self.user_id, self.password)
        assert code == 200

    def test_unregister_error_authorization(self):
        code = self.auth.register(self.user_id, self.password)
        assert code == 200

        code = self.auth.unregister(self.user_id + "_x", self.password)
        assert code != 200

        code = self.auth.unregister(self.user_id, self.password + "_x")
        assert code != 200

    def test_register_error_exist_user_id(self):
        code = self.auth.register(self.user_id, self.password)
        assert code == 200

        code = self.auth.register(self.user_id, self.password)
        assert code != 200

        code = self.auth.unregister(self.user_id, self.password)
        assert code == 200

        code = self.auth.register(self.user_id, self.password)
        assert code != 200

    def test_unregister_with_buyer_or_seller_order(self):

        buyer = register_new_buyer(self.user_id+'b', self.user_id+'b')
        gen_book = GenBook(self.user_id+'s', self.store_id)

        ok, buy_book_id_list = gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
    
        code, order_id = buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200

        code = self.auth.unregister(self.user_id+'b', self.user_id+'b')
        assert code == 526

        code = self.auth.unregister(self.user_id+'s', self.user_id+'s')
        assert code == 527

        code = buyer.cancel(order_id)
        assert code == 200

        code = self.auth.unregister(self.user_id+'b', self.user_id+'b')
        assert code == 200

        code = self.auth.unregister(self.user_id+'s',self.user_id+'s')
        assert code == 200


# if __name__ == "__main__":
#     tmp=TestRegister()
#     tmp.pre_run_initialization()
#     tmp.test_unregister_with_buyer_or_seller_order()