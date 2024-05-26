import pymongo
import json
from be.model import error
from be.model import db_conn
import psycopg2
from psycopg2.extras import RealDictCursor


class Seller(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
        book_json: str,
        stock_level: int,
    ):
        session = self.client.start_session()
        session.start_transaction()
        try:
            if not self.user_id_exist(user_id, session=session):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id, session=session):
                return error.error_non_exist_store_id(store_id)
            if self.conn['user'].find_one(
                {'store_id': store_id}, session=session)['user_id'] != user_id:
                return error.error_authorization_fail()
            if self.book_id_exist(store_id, book_id, session=session):
                return error.error_exist_book_id(book_id)

            ret = self.conn['store'].insert_one(
                {
                    'store_id': store_id,
                    'book_id': book_id,
                    'book_info': json.loads(book_json),
                    'stock_level': stock_level,
                    'sales': 0
                },
                session=session)
            if not ret.acknowledged:
                return 528, "{}".format(str(ret))
        except BaseException as e:  return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"

    def add_stock_level(self, user_id: str, store_id: str, book_id: str,
                        add_stock_level: int):
        session = self.client.start_session()
        session.start_transaction()
        try:
            if not self.user_id_exist(user_id, session=session):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id, session=session):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id, session=session):
                return error.error_non_exist_book_id(book_id)
            ret = self.conn['store'].find_one_and_update(
                {
                    'store_id': store_id,
                    'book_id': book_id,
                    'stock_level': {
                        '$gte': -add_stock_level
                    }
                }, {'$inc': {
                    'stock_level': add_stock_level
                }},
                session=session)
            if ret is None:
                return error.error_out_of_stock(book_id)
        except BaseException as e:  return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        session = self.client.start_session()
        session.start_transaction()
        try:
            if not self.user_id_exist(user_id, session=session):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id, session=session):
                return error.error_exist_store_id(store_id)
            ret = self.conn['user'].update_one(
                {'user_id': user_id}, {'$push': {
                    'store_id': store_id
                }},
                session=session)
            if not ret.acknowledged: return 528, "{}".format(str(ret))
        except BaseException as e:  return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
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
    #     except BaseException as e:  return 530, "{}".format(str(e))
    #     session.commit_transaction()
    #     session.end_session()
    #     return 200, "ok"
    
    def send_books(self, store_id: str, order_id: str) -> (int, str):
        self.update_conn()
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                self.conn.autocommit = False

                cur.execute("SELECT 1 FROM stores WHERE store_id = %s", (store_id,))
                if not cur.fetchone():
                    self.conn.rollback()
                    return error.error_non_exist_store_id(store_id)

                cur.execute("""
                    UPDATE new_order
                    SET status = 'delivered_but_not_received'
                    WHERE order_id = %s
                    RETURNING user_id, status, store_id
                """, (order_id,))
                order = cur.fetchone()
                if not order:
                    self.conn.rollback()
                    return error.error_invalid_order_id(order_id)

                if order['status'] != "paid_but_not_delivered":
                    self.conn.rollback()
                    return error.error_invalid_order_id(order_id)

                if order['store_id'] != store_id:
                    self.conn.rollback()
                    return error.unmatched_order_store(order_id, store_id)
                
                self.conn.commit()
                return 200, "ok"

        except psycopg2.Error as e:self.conn.rollback(); return 528, "{}".format(str(e))
        except BaseException as e:self.conn.rollback(); return 530, "{}".format(str(e))

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

    #     except pymongo.errors.PyMongoError as e:  return 528, "{}".format(str(e)), ""
    #     except BaseException as e:  return 530, "{}".format(str(e)), ""
    #     return 200, "ok", result

    def search_order(self, seller_id, store_id):
        self.update_conn()
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT 1 FROM users WHERE user_id = %s", (seller_id,))
                if not cur.fetchone():
                    return error.error_non_exist_user_id(seller_id), ""

                cur.execute("SELECT 1 FROM stores WHERE store_id = %s", (store_id,))
                if not cur.fetchone():
                    return error.error_non_exist_store_id(store_id), ""

                cur.execute("""
                    SELECT 1 FROM store_users 
                    WHERE store_id = %s AND user_id = %s
                """, (store_id, seller_id))
                if not cur.fetchone():
                    return error.unmatched_seller_store(seller_id, store_id), ""

                cur.execute("SELECT order_id FROM new_order WHERE store_id = %s", (store_id,))
                orders = cur.fetchall()
                result = [order['order_id'] for order in orders]

                return 200, "ok", result

        except psycopg2.Error as e:return 528, "{}".format(str(e))
        except BaseException as e:return 530, "{}".format(str(e))