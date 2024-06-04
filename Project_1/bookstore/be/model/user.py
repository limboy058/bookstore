import jwt
import time
import logging

import psycopg2
from psycopg2.extras import RealDictCursor
import sys

sys.path.append(r'D:\DS_bookstore\Project_1\bookstore')

from be.model import error
from be.model import db_conn

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
        super().__init__()

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
        try:
            with self.get_conn() as conn:
                with conn.cursor() as cur:
                    conn.autocommit = False

                    cur.execute('select user_id from "user" where user_id=%s',
                                (user_id,))
                    ret = cur.fetchone()
                    if ret is not None:
                        return error.error_exist_user_id(user_id)

                    cur.execute(
                        'select user_id from dead_user where user_id=%s' ,
                        (user_id,))
                    ret = cur.fetchone()
                    if ret is not None:
                        return error.error_exist_user_id(user_id)

                    terminal = "terminal_{}".format(str(time.time()))
                    token = jwt_encode(user_id, terminal)
                    cur.execute(
                        'insert into "user" (user_id, password, balance, token, terminal) VALUES (%s, %s, %s, %s, %s)'
                        ,(user_id, password, 0, token, terminal,))
                    conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def check_token(self, user_id: str, token: str,
                    cur) -> (int, str):
        cur.execute('select token from "user" where user_id=%s' , (user_id,))
        ret = cur.fetchone()
        if ret is None:
            return error.error_authorization_fail()
        db_token = ret[0]
        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str, cur) -> (int, str):

        cur.execute('select password from "user" where user_id=%s' , (user_id,))
        ret = cur.fetchone()

        if ret is None:
            return error.error_authorization_fail()

        if password != ret[0]:
            return error.error_authorization_fail()

        return 200, "ok"

    def login(self, user_id: str, password: str,
              terminal: str) -> (int, str, str):
        try:
            with self.get_conn() as conn:
                with conn.cursor() as cur:
                    conn.autocommit = False

                    code, message = self.check_password(user_id, password, cur)
                    if code != 200:
                        return code, message, ""

                    token = jwt_encode(user_id, terminal)
                    cur.execute(
                        'update "user" set token=%s ,terminal=%s where user_id=%s'
                        , (token, terminal, user_id,))

                    conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> bool:
        try:
            with self.get_conn() as conn:
                with conn.cursor() as cur:
                    conn.autocommit = False

                    code, message = self.check_token(user_id, token, cur)
                    if code != 200:
                        return code, message

                    terminal = "terminal_{}".format(str(time.time()))
                    dummy_token = jwt_encode(user_id, terminal)
                    cur.execute(
                        'update "user" set token=%s ,terminal=%s where user_id=%s'
                        , (dummy_token, terminal, user_id,))
                    conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            with self.get_conn() as conn:
                with conn.cursor() as cur:
                    conn.autocommit = False

                    code, message = self.check_password(user_id, password, cur)
                    if code != 200:
                        return code, message
                    
                    cur.execute('''
                                select new_order.buyer_id, store.user_id 
                                from new_order 
                                inner join store on new_order.store_id=store.store_id 
                                where (buyer_id =%s or user_id=%s ) and (status !='recieved' and status !='canceled') 
                                ''',(user_id,user_id,))
                    ret=cur.fetchone()
                    if ret is not None:
                        if ret[0]==user_id:
                            return error.error_unfished_buyer_orders()
                        elif ret[1]==user_id:
                            return error.error_unfished_seller_orders()
                        
                    cur.execute('''
                                UPDATE book_info 
                                SET stock_level = 0 
                                WHERE store_id IN (SELECT store_id FROM store WHERE user_id = %s)
                                ''',(user_id,))

                    cur.execute('delete from "user" where user_id=%s',(user_id,))
                    cur.execute('INSERT INTO dead_user (user_id) VALUES (%s)',(user_id,))

                    conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def change_password(self, user_id: str, old_password: str,
                        new_password: str) -> bool:
        try:
            with self.get_conn() as conn:
                with conn.cursor() as cur:
                    conn.autocommit = False

                    code, message = self.check_password(user_id,
                                                old_password,
                                                cur)
                    if code != 200:
                        return code, message

                    terminal = "terminal_{}".format(str(time.time()))
                    token = jwt_encode(user_id, terminal)
                    cur.execute('update "user" set password=%s ,token=%s,terminal=%s where user_id=%s',(new_password,token,terminal,user_id,))
                    conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"


    def search_order_detail(self, order_id):
        try:
            with self.get_conn() as conn:
                cur=conn.cursor()
                res=0
                cur.execute("SELECT total_price, status FROM new_order WHERE order_id = %s", (order_id,))
                order = cur.fetchone()
                if order is None:
                    cur.execute("SELECT total_price, status FROM old_order WHERE order_id = %s", (order_id,))
                    order = cur.fetchone()
                    if order is None:
                        ret = error.error_non_exist_order_id(order_id)
                        return ret[0], ret[1], ""
                    else:
                        cur.execute("select order_detail from old_order WHERE order_id = %s", (order_id,))
                        res = cur.fetchone()
                else:
                    cur.execute("select order_detail from new_order WHERE order_id = %s", (order_id,))
                    res = cur.fetchone()
                    
                detail=res[0].split('\n')
                detail_dict=dict()
                for tmp in detail:
                    tmp1=tmp.split(' ')
                    if(len(tmp1)<2):
                        break
                    book_id,count=tmp1
                    detail_dict[book_id]=count
                order_detail_list = (detail_dict, order[0], order[1])
                conn.commit()
                return 200, "ok", order_detail_list

        except psycopg2.Error as e:return 528, "{}".format(str(e)),""
        except BaseException as e: return 530, "{}".format(str(e)),""

