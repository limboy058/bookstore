import time
#import sys
# sys.path.append('D:\\DS_bookstore\\Project_1\\bookstore')

import pytest

import be.model.scanner
from fe.access.new_buyer import register_new_buyer
from fe.test.gen_book_data import GenBook

class TestScanner:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self, live_time=10, scan_interval=2):
        self.buyer_id = "test_register_buyer_{}".format(time.time())
        self.password = self.buyer_id
        self.store_id = "test_payment_store_id_{}".format(time.time())

        self.seller_id = "test_register_seller_{}".format(time.time())
        self.password = self.seller_id

        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)

        self.live_time = live_time
        self.scan_interval = scan_interval
        self.scanner = be.model.scanner.Scanner(live_time=live_time,
                                                scan_interval=scan_interval)
        yield

    def test_auto_cancel(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False,
                                                 low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200

        g = self.scanner.keep_running()
        chk = False
        for i in range(self.live_time // self.scan_interval + 3):
            try:
                s = next(g)
                print(s)
                if s[1] != 0:
                    chk = True
            except:
                assert -1
        assert chk
        code = self.buyer.cancel(order_id)
        assert code == 518


# if __name__ == "__main__":
#     tmp = TestScanner()
#     tmp.pre_run_initialization()
#     tmp.test_cancel()
