import pytest
from be.model import db_conn
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
import uuid


class TestCancelOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_cancel_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_cancel_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_cancel_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.dbconn=db_conn.DBConn()
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        
        # ok, buy_book_id_list = self.gen_book.gen(
        #     non_exist_book_id=False, low_stock_level=False
        # )
        # code, ok, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        yield

    def test_unpaid_order_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.buyer.cancel(order_id)
        assert code == 200

    def test_cancel_paid_order_refund_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        cursor=self.dbconn.conn['user'].find_one({'user_id':self.seller_id})
        origin_seller_balance=cursor['balance']
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        origin_buyer_balance=10000000000
        code = self.buyer.add_funds(origin_buyer_balance)
        code = self.buyer.payment(order_id)
        assert code == 200
        code = self.buyer.cancel(order_id)
        assert code == 200
        cursor=self.dbconn.conn['user'].find_one({'user_id':self.buyer_id})
        check_refund_buyer=(origin_buyer_balance==cursor['balance'])
        assert check_refund_buyer
        cursor=self.dbconn.conn['user'].find_one({'user_id':self.seller_id})
        check_refund_seller=(origin_seller_balance==cursor['balance'])
        assert check_refund_seller
        

    def test_order_stock_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        pre_book_stock=[]
        cursor=self.dbconn.conn['store'].find({'store_id':self.store_id})
        for info in buy_book_id_list:
            for item in cursor:
                if item['book_id']==info[0]:
                    pre_book_stock.append((info[0], item['stock_level']))
                    break
            
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.buyer.cancel(order_id)
        cursor=self.dbconn.conn['store'].find({'store_id':self.store_id})
        for book_info in pre_book_stock:
            for item in cursor:
                if item['book_id']==book_info[0]:
                    check_stock=(book_info[1]==item['stock_level'])
                    assert check_stock
                    break
        assert code == 200

    def test_non_exist_order_id(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        order_id = order_id + "_x"
        code = self.buyer.cancel(order_id)
        assert code != 200


    def test_non_prossessing_order_id(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.buyer.cancel(order_id)
        code = self.buyer.cancel(order_id)
        assert code != 200
