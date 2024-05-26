import pymongo
import sys
sys.path.append("D:\dbproject\Project_1\\bookstore")
import uuid
import json
import logging
import time
import datetime
import pymongo.errors
import psycopg2
from be.model import db_conn
from be.model import error


class Buyer(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(self, user_id: str, store_id: str,
                  id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        
        try:
            with self.get_conn() as conn:
                cur=conn.cursor()
                if not self.user_id_exist(user_id,cur):
                    return error.error_non_exist_user_id(user_id) + (order_id, )
                
                cur.execute("select count(1) from store where store_id=%s",[store_id])
                res=cur.fetchone()
                if res is None:
                    return error.error_non_exist_store_id(store_id) + (order_id, )

                uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))
                sum_price = 0

                book_id_lst=list()
                for i in id_and_count:
                    book_id_lst.append(i[0])

                cur.execute("select price,stock_level,book_id from book_info where store_id=%s and book_id in %s ;",[store_id,tuple(book_id_lst)])

                res=cur.fetchall()
                for price,stock_level,target_id in res:
                    for book_id,count in id_and_count:
                        if(book_id==target_id):
                            sum_price += price * count
                            if(stock_level<count):
                                return error.error_stock_level_low(book_id) + (order_id, )
                            else:break

                for book_id, count in id_and_count:
                    cur.execute("update book_info set stock_level=stock_level-%s, sales=sales+%s where store_id=%s and book_id=%s",[count,count,store_id,book_id])
                query="insert into new_order values(%s,%s,%s,%s,%s,%s)"
                order_id = uid
                cur.execute(query,[order_id,store_id,user_id,'unpaid',datetime.datetime.now(),sum_price])
                conn.commit()
            
        except psycopg2.Error as e:  return 528, "{}".format(str(e)), ""
        except BaseException as e:  return 530, "{}".format(str(e)), ""
        return 200, "ok", order_id

    def payment(self, user_id: str, password: str,
                order_id: str) -> (int, str):
        try:
            with self.get_conn() as conn:
                cur=conn.cursor()
                cur.execute("select order_id,buyer_id,total_price from new_order where order_id=%s and status=%s",[order_id,"unpaid"])
                res=cur.fetchone()
                if(res==None):
                    return error.error_invalid_order_id(order_id)
                order_id = res[0]
                buyer_id = res[1]
                total_price = res[2]
                if buyer_id != user_id:
                    return error.error_authorization_fail()
                
                cur.execute("select balance from \"user\" where user_id=%s and password=%s",[user_id,password])
                res=cur.fetchone()
                if(res==None):
                    return error.error_authorization_fail()
                if(res[0]<total_price):
                    return error.error_not_sufficient_funds(order_id)
                cur.execute("update \"user\" set balance=balance-%s where user_id=%s",[total_price,user_id])
                    
                cur.execute("update new_order set status=%s where order_id=%s",["paid_but_not_delivered",order_id])
                conn.commit()
        except pymongo.errors.PyMongoError as e:  return 528, "{}".format(str(e))
        except BaseException as e:  return 530, "{}".format(str(e))
        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        session = self.client.start_session()
        session.start_transaction()
        try:
            cursor = self.conn['user'].find_one_and_update(
                {'user_id': user_id}, {'$inc': {
                    'balance': add_value
                }},
                session=session)
            if (cursor['password'] != password):
                return error.error_authorization_fail()
            if (cursor['balance'] < -add_value):
                return error.error_non_enough_fund(user_id)
        except pymongo.errors.PyMongoError as e:  return 528, "{}".format(str(e))
        except BaseException as e:  return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"

    def cancel(self, user_id, order_id) -> (int, str):
        session = self.client.start_session()
        session.start_transaction()
        unprosssing_status = ["unpaid", "paid_but_not_delivered"]
        try:
            cursor = self.conn['new_order'].find_one_and_update(
                {'order_id': order_id}, {'$set': {
                    'status': "canceled"
                }},
                session=session)
            if (cursor is None):
                return error.error_non_exist_order_id(order_id)

            if (cursor['status'] not in unprosssing_status):
                return error.error_invalid_order_id(order_id)

            if (cursor['user_id'] != user_id):
                return error.error_order_user_id(order_id, user_id)

            current_status = cursor['status']
            store_id = cursor['store_id']
            total_price = cursor['total_price']
            detail = list(cursor['detail'])

            for i in detail:
                self.conn['store'].update_one(
                    {
                        'book_id': i[0],
                        'store_id': store_id
                    }, {'$inc': {
                        "stock_level": i[1],
                        "sales": -i[1]
                    }},
                    session=session)
            if (current_status == "paid_but_not_delivered"):
                cursor = self.conn['user'].find_one_and_update(
                    {'user_id': user_id}, {'$inc': {
                        'balance': total_price
                    }},
                    session=session)

        except pymongo.errors.PyMongoError as e:  return 528, "{}".format(str(e))
        except BaseException as e:  return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"

    def search_order(self, user_id):
        try:
            cursor = self.conn['user'].find_one({'user_id': user_id})
            if (cursor is None):
                return error.error_non_exist_user_id(user_id) + ("", )
            cursor = self.conn['new_order'].find({'user_id': user_id})
            result = list()
            for i in cursor:
                result.append(i['order_id'])
        except pymongo.errors.PyMongoError as e:  return 528, "{}".format(str(e)), ""
        except Exception as e:  return 530, "{}".format(str(e)), ""
        return 200, "ok", result

    def receive_books(self, user_id, order_id) -> (int, str):
        session = self.client.start_session()
        session.start_transaction()
        try:
            if not self.user_id_exist(user_id, session=session):
                return error.error_non_exist_user_id(user_id)
            cursor = self.conn['new_order'].find_one_and_update(
                {'order_id': order_id}, {'$set': {
                    'status': "received"
                }},
                session=session)
            if (cursor == None):
                return error.error_invalid_order_id(order_id)
            if (cursor['status'] != "delivered_but_not_received"):
                return error.error_invalid_order_id(order_id)
            if (cursor['user_id'] != user_id):
                return error.unmatched_order_user(order_id, user_id)
            total_price = cursor['total_price']
            seller_id = cursor['seller_id']
            cursor = self.conn['user'].find_one_and_update(
                {'user_id': seller_id}, {'$inc': {
                    'balance': total_price
                }},
                session=session)

        except pymongo.errors.PyMongoError as e:  return 528, "{}".format(str(e))
        except BaseException as e:  return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"

if __name__=="__main__":
    buyer=Buyer()
    conn=buyer.get_conn()
    cur=conn.cursor()
    cur.execute("insert into \"user\" values('seller','abc',0,'a','a')")
    cur.execute("insert into \"user\" values('buyer','abc',1000,'a','a')")
    cur.execute("insert into store values('store','seller')")
    cur.execute("insert into book_info (book_id,store_id,stock_level,sales,price) values ('mamba out!','store',10,0,50)")
    conn.commit()
    res=buyer.new_order('buyer','store',[('mamba out!',5)])
    print(res)
    conn=buyer.get_conn()
    cur.execute("select * from new_order")
    res=cur.fetchone()
    print(res)
    order_id=res[0]
    conn.commit()
    res=buyer.payment("buyer","abc",order_id)
    print(res)
    conn=buyer.get_conn()
    cur.execute("select * from new_order")
    res=cur.fetchone()
    print(res)
    cur.execute("select * from \"user\"")
    res=cur.fetchall()
    for i in res:
        print(i)