import pytest
# import sys
# sys.path.append("D:\\code\数据库系统\\AllStuRead-master\\Project_1\\bookstore")
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
        self.seller_id = "test_search_order_seller_id_{}".format(
            str(uuid.uuid1()))
        self.store_id = "test_search_order_store_id_{}".format(
            str(uuid.uuid1()))
        self.buyer_id = "test_search_order_buyer_id_{}".format(
            str(uuid.uuid1()))
        self.password = self.seller_id
        self.auth = Auth(conf.URL)
        self.dbconn = db_conn.DBConn()
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        self.seller = self.gen_book.return_seller()
        yield

    def test_search_orders_detail_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        tol_price = 0
        conn=self.dbconn.get_conn()
        cursor=conn.cursor()
        for info in buy_book_id_list:
            cursor.execute("select price from book_info where book_id=%s and store_id=%s",[info[0],self.store_id,])
            res=cursor.fetchone()
            assert res != None
            cur_price = res[0]
            tol_price += cur_price * info[1]
        cursor.close()
        code, tmp = self.auth.search_order_detail(order_id)
        assert (code == 200)
        (book_list, price, status) = tmp
        assert list(book_list).sort() == buy_book_id_list.sort()
        assert tol_price == price
        assert status == 'unpaid'

    def test_search_invalid_orders_detail(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code, _ = self.auth.search_order_detail(order_id + "_y")
        assert code != 200

    def test_buyer_search_order_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code, order_list = self.buyer.search_order()
        assert code == 200

    def test_buyer_search_error_user_order(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        self.buyer.user_id = self.buyer.user_id + "_x"
        code, order_list = self.buyer.search_order()
        assert code != 200

    def test_buyer_search_empty_order(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_list = self.buyer.search_order()
        assert code == 200

    def test_buyer_one_order_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        order_list = list()
        order_list.append(order_id)
        code, received_list = self.buyer.search_order()
        assert order_list.sort() == received_list.sort()

    def test_buyer_many_orders_ok(self):
        order_list = list()
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False,
                                                 high_stock_level=True)
        assert ok
        for i in range(0, 5):
            code, order_id = self.buyer.new_order(self.store_id,
                                                  buy_book_id_list)
            assert code == 200
            order_list.append(order_id)
        code, received_list = self.buyer.search_order()
        assert order_list.sort() == received_list.sort()

    def test_seller_search_order_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code, order_list = self.seller.search_order(self.store_id)
        assert code == 200

    def test_seller_search_empty_order_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_list = self.seller.search_order(self.store_id)
        assert code == 200

    def test_seller_search_error_seller_order(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        self.seller.seller_id = self.seller.seller_id + "_x"
        code, order_list = self.seller.search_order(self.store_id)
        assert code != 200

    def test_seller_search_error_store_order(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code, order_list = self.seller.search_order(self.store_id + "_x")
        assert code != 200

    def test_seller_search_unmatch_order(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        self.seller.seller_id = self.buyer_id
        code, order_list = self.seller.search_order(self.store_id)
        assert code != 200

    def test_seller_one_order_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        order_list = list()
        order_list.append(order_id)
        code, received_list = self.seller.search_order(self.store_id)
        assert order_list.sort() == received_list.sort()

    def test_seller_many_orders_ok(self):
        order_list = list()
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False,
                                                 high_stock_level=True)
        assert ok
        for i in range(0, 5):
            code, order_id = self.buyer.new_order(self.store_id,
                                                  buy_book_id_list)
            assert code == 200
            order_list.append(order_id)
        code, received_list = self.seller.search_order(self.store_id)
        assert order_list.sort() == received_list.sort()

# if __name__=="__main__":
#     test=TestSearchOrder()
#     test.pre_run_initialization()
#    # test.test_cancel_paid_order_refund_ok()
#     test.test_buyer_search_order_ok()