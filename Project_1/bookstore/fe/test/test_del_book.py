import pytest
import sys
sys.path.append("D:\\code\\数据库系统\\AllStuRead-master\\Project_1\\bookstore")
from be.model import db_conn
from fe import conf
from fe.access.new_seller import register_new_seller
from fe.access import book
import uuid
import os


class TestDelBook:

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        # do before test
        self.seller_id = "test_del_books_seller_id_{}".format(str(
            uuid.uuid1()))
        self.store_id = "test_del_books_store_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.seller = register_new_seller(self.seller_id, self.password)
        self.dbconn = db_conn.DBConn()
        code = self.seller.create_store(self.store_id)
        assert code == 200
        book_db = book.BookDB(conf.Use_Large_DB)
        self.books = book_db.get_book_info(0, 2)

        yield

    def test_ok(self):
        for b in self.books:
            code = self.seller.add_book(self.store_id, 0, b)
            assert code == 200

        for b in self.books:
            code = self.seller.del_book(self.store_id, b.id)
            assert code == 200
            

    def test_db_clean_ok(self):
        for b in self.books:
            code = self.seller.add_book(self.store_id, 0, b)
            assert code == 200

        for b in self.books:
            code = self.seller.del_book(self.store_id, b.id)
            assert code == 200

        conn=self.dbconn.get_conn()
        cursor=conn.cursor()
        for b in self.books:
            cursor.execute(
            'select title  from book_info where book_id=%s and store_id=%s',
            (
                b.id,
                self.store_id,
            ))
            title = cursor.fetchone()
            assert not title
        cursor.close()
        conn.close()

    def test_path_clean_ok(self):
        for b in self.books:
            code = self.seller.add_book(self.store_id, 0, b)
            assert code == 200
        for b in self.books:
            code = self.seller.del_book(self.store_id, b.id)
            assert code == 200

        current_file_path = os.path.abspath(__file__)
        current_directory = os.path.dirname(current_file_path)
        fe_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
        bkstore_directory = os.path.abspath(os.path.join(fe_directory, os.pardir))
        data_path=os.path.abspath(bkstore_directory+'/be/data')
        file_paths = [
            data_path+'/auth_intro/{id}.txt',
            data_path+'/book_intro/{id}.txt',
            data_path+'/content/{id}.txt',
            data_path+'/img/{id}.png'
        ]

        
        for b in self.books:
            book_id = b.id
            for path in file_paths:
                file_path = path.format(id=book_id)
                assert not os.path.exists(file_path)
    

    def test_error_non_exist_store_id(self):
        for b in self.books:
            code = self.seller.add_book(self.store_id, 0, b)
            assert code == 200

        for b in self.books:
            code = self.seller.del_book(self.store_id + "x", b.id)
            assert code != 200

    def test_error_non_exist_book(self):
        for b in self.books:
            code = self.seller.del_book(self.store_id, b.id)
            assert code != 200

    def test_error_non_exist_book_id(self):
        for b in self.books:
            code = self.seller.add_book(self.store_id, 0, b)
            assert code == 200

        for b in self.books:
            code = self.seller.del_book(self.store_id, b.id+ "x")
            assert code != 200

    def test_error_non_exist_user_id(self):
        for b in self.books:        
            code = self.seller.add_book(self.store_id, 0, b)
            assert code == 200

        for b in self.books:
            self.seller.seller_id = self.seller.seller_id + "_x"
            code = self.seller.del_book(self.store_id, b.id)
            assert code != 200

# if __name__=="__main__":
#     test=TestDelBook()
#     test.pre_run_initialization()
#    # test.test_cancel_paid_order_refund_ok()
#     test.test_db_clean_ok()
#     test.test_path_clean_ok()