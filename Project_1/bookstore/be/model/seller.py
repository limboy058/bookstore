import json
# import sys

# sys.path.append(r'D:\DS_bookstore\Project_1\bookstore')


from be.model import error
from be.model import db_conn

import psycopg2


class Seller(db_conn.DBConn):

    def __init__(self):
        super().__init__()

    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
        book_json: str,
        stock_level: int,
    ):
        try:
            with self.get_conn() as conn:
                with conn.cursor() as cur:
                    conn.autocommit = False
                    if not self.user_id_exist(user_id, cur):
                        return error.error_non_exist_user_id(user_id)
                    if not self.store_id_exist(store_id, cur):
                        return error.error_non_exist_store_id(store_id)
                    cur.execute(
                        'select * from store where store_id=%s and user_id!=%s',
                        (
                            store_id,
                            user_id,
                        ))
                    ret = cur.fetchone()
                    if ret != None:
                        return error.error_authorization_fail()
                    if self.book_id_exist(store_id, book_id, cur):
                        return error.error_exist_book_id(book_id)
                    data = json.loads(book_json)
                    cur.execute('''
                                insert into book_info 
                                (book_id,store_id,price,stock_level,sales,title,author,publisher,original_title,
                                translator,pub_year,pages,currency_unit,binding,isbn,author_intro,book_intro,content,picture)
                                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                ''' , (
                        book_id,
                        store_id,
                        data['price'],
                        stock_level,
                        0,
                        data['title'],
                        data['author'],
                        data['publisher'],
                        data['original_title'],
                        data['translator'],
                        data['pub_year'],
                        data['pages'],
                        data['currency_unit'],
                        data['binding'],
                        data['isbn'],
                        'unsetpath',
                        'unsetpath',
                        'unsetpath',
                        'unsetpath',
                    ))
                    conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(self, user_id: str, store_id: str, book_id: str,
                        add_stock_level: int):
        try:
            with self.get_conn() as conn:
                with conn.cursor() as cur:
                    conn.autocommit = False
                    if not self.user_id_exist(user_id, cur):
                        return error.error_non_exist_user_id(user_id)
                    if not self.store_id_exist(store_id, cur):
                        return error.error_non_exist_store_id(store_id)
                    if not self.book_id_exist(store_id, book_id, cur):
                        return error.error_non_exist_book_id(book_id)
                    cur.execute(
                        'update book_info set stock_level=stock_level+%s where book_id=%s and store_id=%s and stock_level>=%s',
                        (add_stock_level, book_id, store_id, -add_stock_level))
                    if cur.rowcount == 0:  #受影响行数
                        return error.error_out_of_stock(book_id)
                    conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            with self.get_conn() as conn:
                with conn.cursor() as cur:
                    conn.autocommit = False
                    if not self.user_id_exist(user_id, cur):
                        return error.error_non_exist_user_id(user_id)
                    if self.store_id_exist(store_id, cur):
                        return error.error_exist_store_id(store_id)
                    cur.execute(
                        'insert into store (store_id,user_id)values(%s,%s)', (
                            store_id,
                            user_id,
                        ))
                    conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"


    # def send_books(self, store_id: str, order_id: str) -> (int, str):
    #     session = self.client.start_session()
    #     session.start_transaction()
    #     try:
    #         if not self.store_id_exist(store_id, session=session):
    #             return error.error_non_exist_store_id(store_id)

    #         cursor = self.conn['new_order'].find_one_and_update(
    #             {'order_id': order_id},
    #             {'$set': {
    #                 'status': "delivered_but_not_received"
    #             }},
    #             session=session)
    #         if (cursor is None):
    #             return error.error_invalid_order_id(order_id)
    #         if (cursor['status'] != "paid_but_not_delivered"):
    #             return error.error_invalid_order_id(order_id)
    #         if (cursor['store_id'] != store_id):
    #             return error.unmatched_order_store(order_id, store_id)
    #     except BaseException as e:
    #         return 530, "{}".format(str(e))
    #     session.commit_transaction()
    #     session.end_session()
    #     return 200, "ok"

    # def search_order(self, seller_id, store_id):
    #     try:
    #         ret = self.conn['user'].find({'user_id': seller_id})
    #         if (ret is None):
    #             return error.error_non_exist_user_id(seller_id) + ("", )
    #         ret = self.conn['user'].find({'store_id': store_id})
    #         if (ret is None):
    #             return error.error_non_exist_store_id(store_id) + ("", )
    #         ret = self.conn['user'].find_one({
    #             'store_id': store_id,
    #             'user_id': seller_id
    #         })
    #         if (ret is None):
    #             return error.unmatched_seller_store(seller_id,
    #                                                 store_id) + ("", )
    #         cursor = self.conn['new_order'].find({'store_id': store_id})

    #         result = list()
    #         for i in cursor:
    #             result.append(i['order_id'])

    #     except pymongo.errors.PyMongoError as e:
    #         return 528, "{}".format(str(e)), ""
    #     except BaseException as e:
    #         return 530, "{}".format(str(e)), ""
    #     return 200, "ok", result



# from fe.access import book
# from be.model import user
# if __name__=='__main__':
#     u=user.User()

#     s=Seller()

#     b=book.BookDB()
#     books = b.get_book_info(0, 4)

#     print(s.add_book('uid1','sid1','100012',json.dumps(books[3].__dict__),10))
#     print(s.add_book('uid1','sid1','1000112',json.dumps(books[2].__dict__),10))
