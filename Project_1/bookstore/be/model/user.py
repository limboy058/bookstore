import jwt
import time
import logging
from be.model import error
from be.model import db_conn
import pymongo.errors
import psycopg2
from psycopg2.extras import RealDictCursor

# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }


def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {
            "user_id": user_id,
            "terminal": terminal,
            "timestamp": time.time()
        },
        key=user_id,
        algorithm="HS256",
    )
    return encoded.encode("utf-8").decode("utf-8")


# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str):
        session = self.client.start_session()
        session.start_transaction()
        try:
            ret = self.conn['user'].find_one({'user_id': user_id},
                                             session=session)
            if ret is not None:
                return error.error_exist_user_id(user_id)
            ret = self.conn['dead_user'].find_one({'user_id': user_id},
                                                  session=session)
            if ret is not None:
                return error.error_exist_user_id(user_id)
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            ret = self.conn['user'].insert_one(
                {
                    'user_id': user_id,
                    'password': password,
                    'balance': 0,
                    'token': token,
                    'terminal': terminal
                },
                session=session)
            if not ret.acknowledged: return 528, "{}".format(str(ret))
        except BaseException as e:  return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"

    def check_token(self,
                    user_id: str,
                    token: str,
                    session=None) -> (int, str):
        ret = self.conn['user'].find_one({'user_id': user_id}, {
            '_id': 0,
            'token': 1
        },
                                         session=session)
        if ret is None:
            return error.error_authorization_fail()
        db_token = ret['token']
        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self,
                       user_id: str,
                       password: str,
                       session=None) -> (int, str):
        ret = self.conn['user'].find_one({'user_id': user_id}, {
            '_id': 0,
            'password': 1
        },
                                         session=session)

        if ret is None:
            return error.error_authorization_fail()

        if password != ret['password']:
            return error.error_authorization_fail()

        return 200, "ok"

    def login(self, user_id: str, password: str,
              terminal: str) -> (int, str, str):
        session = self.client.start_session()
        session.start_transaction()
        token = ""
        try:
            code, message = self.check_password(user_id,
                                                password,
                                                session=session)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            self.conn['user'].update_one(
                {'user_id': user_id},
                {'$set': {
                    'token': token,
                    'terminal': terminal
                }},
                session=session)
        except pymongo.errors.PyMongoError as e:  return 528, "{}".format(str(e)), ""
        except BaseException as e:  return 530, "{}".format(str(e)), ""
        session.commit_transaction()
        session.end_session()
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> bool:
        session = self.client.start_session()
        session.start_transaction()
        try:
            code, message = self.check_token(user_id, token, session=session)
            if code != 200:
                return code, message
            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)
            ret = self.conn['user'].update_one(
                {'user_id': user_id},
                {'$set': {
                    'token': dummy_token,
                    'terminal': terminal
                }},
                session=session)
        except pymongo.errors.PyMongoError as e:  return 528, "{}".format(str(e))
        except BaseException as e:  return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        session = self.client.start_session()
        session.start_transaction()
        try:
            code, message = self.check_password(user_id,
                                                password,
                                                session=session)
            if code != 200:
                return code, message

            cursor = self.conn['new_order'].find(
                {'$or': [{
                    'seller_id': user_id
                }, {
                    'user_id': user_id
                }]},
                session=session)
            for item in cursor:
                if item['status'] != 'received' and item[
                        'status'] != 'canceled':
                    if item['user_id'] == user_id:
                        return error.error_unfished_buyer_orders()
                    if item['seller_id'] == user_id:
                        return error.error_unfished_seller_orders()

            ret = self.conn['user'].find_one({'user_id': user_id},
                                             {'store_id': 1},
                                             session=session)
            if len(ret) == 2:
                store_list = list(ret['store_id'])
                if len(store_list) != 0:
                    ret = self.conn['store'].update_many(
                        {'store_id': {
                            '$in': store_list
                        }}, {'$set': {
                            'stock_level': 0
                        }},
                        session=session)  #修改书库存

            ret = self.conn['user'].delete_one({'user_id': user_id},
                                               session=session)
            self.conn['dead_user'].insert_one({'user_id': user_id},
                                              session=session)
        except pymongo.errors.PyMongoError as e:  return 528, "{}".format(str(e))
        except BaseException as e:  return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"

    def change_password(self, user_id: str, old_password: str,
                        new_password: str) -> bool:
        session = self.client.start_session()
        session.start_transaction()
        try:
            code, message = self.check_password(user_id,
                                                old_password,
                                                session=session)
            if code != 200:
                return code, message
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            self.conn['user'].update_one({'user_id': user_id}, {
                '$set': {
                    'password': new_password,
                    'token': token,
                    'terminal': terminal
                }
            },
                                         session=session)
        except pymongo.errors.PyMongoError as e:  return 528, "{}".format(str(e))
        except BaseException as e:  return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"

    def search_order_detail(self, order_id):
        try:
            cursor = self.conn['new_order'].find_one({'order_id': order_id})
            if cursor is None:
                ret = error.error_non_exist_order_id(order_id)
                return ret[0], ret[1], ""
            order_detail_list = (cursor['detail'], cursor['total_price'],
                                 cursor['status'])
        except pymongo.errors.PyMongoError as e:  return 528, "{}".format(str(e)), ""
        except BaseException as e:  return 530, "{}".format(str(e)), ""
        return 200, "ok", order_detail_list

    def search_order_detail(self, order_id):
        self.update_conn()
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:

                cur.execute("SELECT detail, total_price, status FROM new_order WHERE order_id = %s", (order_id,))
                order = cur.fetchone()
                
                if order is None:
                    ret = error.error_non_exist_order_id(order_id)
                    return ret[0], ret[1], ""
                
                order_detail_list = (order['detail'], order['total_price'], order['status'])
                return 200, "ok", order_detail_list

        except psycopg2.Error as e:return 528, "{}".format(str(e))
        except BaseException as e: return 530, "{}".format(str(e))
