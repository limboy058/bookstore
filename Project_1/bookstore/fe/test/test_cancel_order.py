import pytest
# import sys
# sys.path.append("D:\\code\数据库系统\\AllStuRead-master\\Project_1\\bookstore")
from be.model import db_conn
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.new_seller import register_new_seller
import uuid


class TestCancelOrder:

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_cancel_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_cancel_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_cancel_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.dbconn = db_conn.DBConn()
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        self.seller = self.gen_book.return_seller()
        yield




    def test_buyer_unpaid_order_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.buyer.cancel(order_id)
        assert code == 200

    def test_buyer_muti_cancel(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.buyer.cancel(order_id)
        assert code == 200
        code = self.buyer.cancel(order_id)
        assert code == 518

    def test_buyer_cancel_paid_order_refund_ok(self):
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
        code = self.buyer.payment(order_id)
        assert code == 200
        code = self.buyer.cancel(order_id)
        assert code == 200

        conn=self.dbconn.get_conn()
        cursor=conn.cursor()
        cursor.execute("select balance from \"user\" where user_id=%s",[self.buyer_id,])
        res=cursor.fetchone()
        assert(res is not None)
        new_buyer_balance = res[0]
        conn.close()

        check_refund_buyer = (origin_buyer_balance == new_buyer_balance)
        assert check_refund_buyer

        conn=self.dbconn.get_conn()
        cursor=conn.cursor()
        cursor.execute("select balance from \"user\" where user_id=%s",[self.seller_id,])
        res=cursor.fetchone()
        assert(res is not None)
        new_seller_balance = res[0]
        conn.close()

        check_refund_seller = (origin_seller_balance == new_seller_balance)
        assert check_refund_seller

    def test_buyer_order_stock_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        pre_book_stock = []
        conn=self.dbconn.get_conn()
        cursor=conn.cursor()
        cursor.execute("select book_id,stock_level from book_info where store_id=%s",[self.store_id,])
        res=cursor.fetchall()
        cursor.close()
        conn.close()

        for info in buy_book_id_list:
            for book_id,stock_level in res:
                if(book_id==info[0]):
                    pre_book_stock.append((book_id,stock_level))
                    break

        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.buyer.cancel(order_id)
        assert code == 200
        conn=self.dbconn.get_conn()
        cursor=conn.cursor()
        cursor.execute("select book_id,stock_level from book_info where store_id=%s",[self.store_id,])
        res=cursor.fetchall()
        cursor.close()
        conn.close()
        for book_info in pre_book_stock:
            for book_id,stock_level in res:
                if book_id == book_info[0]:
                    check_stock = (book_info[1] == stock_level)
                    assert check_stock
                    break
        assert code == 200

    def test_buyer_non_exist_order_id(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        order_id = order_id + "_x"
        code = self.buyer.cancel(order_id)
        assert code != 200

    def test_buyer_non_prossessing_order_id(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.buyer.cancel(order_id)
        code = self.buyer.cancel(order_id)
        assert code != 200

    def test_buyer_cancel_error_user_id(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        origin_user_id = self.buyer.user_id
        self.buyer.user_id = self.buyer.user_id + "_x"
        code = self.buyer.cancel(order_id)
        self.buyer.user_id = origin_user_id
        assert code != 200

    def test_buyer_cancel_delivering_order_id(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.buyer.add_funds(100000000)
        assert code == 200
        code = self.buyer.payment(order_id)
        assert code == 200
        code = self.seller.send_books(self.store_id, order_id)
        assert code == 200
        code = self.buyer.cancel(order_id)
        assert code != 200




    def test_seller_cancel_unpaid_order_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.seller.cancel(self.store_id, order_id)
        assert code == 200

    def test_seller_cancel_paid_order_refund_ok(self):
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
        code = self.buyer.payment(order_id)
        assert code == 200
        code = self.seller.cancel(self.store_id, order_id)
        assert code == 200

        conn=self.dbconn.get_conn()
        cursor=conn.cursor()
        cursor.execute("select balance from \"user\" where user_id=%s",[self.buyer_id,])
        res=cursor.fetchone()
        assert(res is not None)
        new_buyer_balance = res[0]
        conn.close()

        check_refund_buyer = (origin_buyer_balance == new_buyer_balance)
        assert check_refund_buyer

        conn=self.dbconn.get_conn()
        cursor=conn.cursor()
        cursor.execute("select balance from \"user\" where user_id=%s",[self.seller_id,])
        res=cursor.fetchone()
        assert(res is not None)
        new_seller_balance = res[0]
        conn.close()

        check_refund_seller = (origin_seller_balance == new_seller_balance)
        assert check_refund_seller

    def test_seller_order_stock_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        pre_book_stock = []
        conn=self.dbconn.get_conn()
        cursor=conn.cursor()
        cursor.execute("select book_id,stock_level from book_info where store_id=%s",[self.store_id,])
        res=cursor.fetchall()
        cursor.close()
        conn.close()

        for info in buy_book_id_list:
            for book_id,stock_level in res:
                if(book_id==info[0]):
                    pre_book_stock.append((book_id,stock_level))
                    break

        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.seller.cancel(self.store_id, order_id)
        assert code == 200
        conn=self.dbconn.get_conn()
        cursor=conn.cursor()
        cursor.execute("select book_id,stock_level from book_info where store_id=%s",[self.store_id,])
        res=cursor.fetchall()
        cursor.close()
        conn.close()
        for book_info in pre_book_stock:
            for book_id,stock_level in res:
                if book_id == book_info[0]:
                    check_stock = (book_info[1] == stock_level)
                    assert check_stock
                    break
        assert code == 200

    def test_seller_non_exist_order_id(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        order_id = order_id + "_x"
        code = self.seller.cancel(self.store_id, order_id)
        assert code != 200

    def test_seller_non_prossessing_order_id(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.seller.cancel(self.store_id, order_id)
        code = self.seller.cancel(self.store_id, order_id)
        assert code != 200

    def test_seller_cancel_non_exist_store_id(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        origin_user_id = self.buyer.user_id
        self.store_id = self.store_id + "_x"
        code = self.seller.cancel(self.store_id, order_id)
        self.buyer.user_id = origin_user_id
        assert code != 200

    def test_seller_cancel_unmatched_store_id(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False,)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        
        self.store_id2 = "test_cancel_store2_id_{}".format(str(uuid.uuid1()))
        self.seller_id2 = "test_cancel_seller2_id_{}".format(str(uuid.uuid1()))
        self.gen_book = GenBook(self.seller_id2, self.store_id2)
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False,)
        assert ok

        code, order_id2 = self.buyer.new_order(self.store_id2, buy_book_id_list)
        assert code == 200
        code = self.seller.cancel(self.store_id2, order_id)
        assert code != 200

    def test_seller_cancel_delivering_order_id(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.buyer.add_funds(100000000)
        assert code == 200
        code = self.buyer.payment(order_id)
        assert code == 200
        code = self.seller.send_books(self.store_id, order_id)
        assert code == 200
        code = self.seller.cancel(self.store_id, order_id)
        assert code != 200

# if __name__=="__main__":
#     test=TestCancelOrder()
#     test.pre_run_initialization()
#    # test.test_cancel_paid_order_refund_ok()
#     test.test_delivering_order_id()


