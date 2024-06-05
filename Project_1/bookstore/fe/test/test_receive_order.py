import pytest
import sys
# sys.path.append("D:\\code\数据库系统\\AllStuRead-master\\Project_1\\bookstore")
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from be.model import db_conn

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
        self.dbconn = db_conn.DBConn()

        yield

    def test_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.buyer.add_funds(100000000)
        code = self.buyer.payment(order_id)
        code = self.seller.send_books(self.store_id, order_id)
        code = self.buyer.receive_books(order_id)
        assert code == 200

    def test_seller_fund_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        conn=self.dbconn.get_conn()
        cursor=conn.cursor()
        cursor.execute("select balance from \"user\" where user_id=%s",[self.seller_id,])
        res=cursor.fetchone()
        assert(res!=None)
        origin_seller_balance = res[0]
        conn.close()

        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        origin_buyer_balance = 1000000000
        code = self.buyer.add_funds(origin_buyer_balance)
        assert code==200

        conn=self.dbconn.get_conn()
        cursor=conn.cursor()
        cursor.execute("select total_price from new_order where order_id=%s",[order_id,])
        res=cursor.fetchone()
        assert(res is not None)
        total_price = res[0]
        conn.close()

        code = self.buyer.payment(order_id)
        assert code == 200
        code = self.seller.send_books(self.store_id, order_id)
        assert code == 200
        code = self.buyer.receive_books(order_id)
        assert code == 200


        conn=self.dbconn.get_conn()
        cursor=conn.cursor()
        cursor.execute("select balance from \"user\" where user_id=%s",[self.seller_id,])
        res=cursor.fetchone()
        assert(res is not None)
        new_seller_balance = res[0]
        conn.close()

        check_refund_seller = (origin_seller_balance+total_price == new_seller_balance)
        assert check_refund_seller

    def test_unmatch_user_id_receive(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.buyer.add_funds(100000000)
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
        code = self.buyer.add_funds(100000000)
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
        code = self.buyer.add_funds(100000000)
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
        code = self.buyer.add_funds(100000000)
        code = self.buyer.payment(order_id)
        code = self.buyer.receive_books(order_id)
        assert code != 200

# if __name__=="__main__":
#     test=TestreceiveOrder()
#     test.pre_run_initialization()
#    # test.test_cancel_paid_order_refund_ok()
#     test.test_ok()
