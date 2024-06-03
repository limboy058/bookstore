import sys

sys.path.append("D:\\dbproject\\Project_1\\bookstore")
import random

import uuid
import json
import logging
import time
import datetime
import psycopg2
from be.model import db_conn
from be.model import error
from fe.conf import Retry_time

class Buyer(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(self, user_id: str, store_id: str,
                  id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        attempt=0
        while(True):
            try:
                with self.get_conn() as conn:
                    cur=conn.cursor()
                    if not self.user_id_exist(user_id,cur):
                        return error.error_non_exist_user_id(user_id) + (order_id, )
                    
                    cur.execute("select count(1) from store where store_id=%s",[store_id,])
                    res=cur.fetchone()
                    if res[0]==0:
                        return error.error_non_exist_store_id(store_id) + (order_id, )

                    uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))
                    sum_price = 0

                    book_id_lst=list()
                    for i in id_and_count:
                        book_id_lst.append(i[0])

                    cur.execute("select price,stock_level,book_id from book_info where store_id=%s and book_id in %s for update;",[store_id,tuple(book_id_lst)])

                    res=cur.fetchall()
                    for book_id,count in id_and_count:
                        judge=False
                        for price,stock_level,target_id in res:
                            if(book_id==target_id):
                                sum_price += price * count
                                if(stock_level<count):
                                    return error.error_stock_level_low(book_id) + (order_id, )
                                else:
                                    judge=True
                                    break
                        if not judge:
                            return error.error_non_exist_book_id(book_id) + (order_id, )
                    order_detail=""
                    for book_id, count in id_and_count:
                        cur.execute("update book_info set stock_level=stock_level-%s, sales=sales+%s where store_id=%s and book_id=%s",[count,count,store_id,book_id])
                        order_detail+=book_id+" "+str(count)+"\n"
                        #cur.execute("insert into order_detail values(%s,%s,%s)",[uid,book_id,count])
                    query="insert into new_order values(%s,%s,%s,%s,%s,%s,%s)"
                    order_id = uid
                    cur.execute(query,[order_id,store_id,user_id,'unpaid',datetime.datetime.now(),sum_price,order_detail])
                    conn.commit()
            except psycopg2.Error as e:
                if e.pgcode=="40001" and attempt<Retry_time:
                    attempt+=1
                    time.sleep(random.random()*attempt)
                    continue
                else:
                    return 528, "{}".format(str(e.pgerror+" "+e.pgcode)), ""
            except BaseException as e:  return 530, "{}".format(str(e)), ""
            return 200, "ok", order_id

    def payment(self, user_id: str, password: str,
                order_id: str) -> (int, str):
        attempt=0
        while(True):
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
                    
                    cur.execute("select balance from \"user\" where user_id=%s and password=%s for update",[user_id,password])
                    res=cur.fetchone()
                    if(res==None):
                        return error.error_authorization_fail()
                    if(res[0]<total_price):
                        return error.error_not_sufficient_funds(order_id)
                    cur.execute("update \"user\" set balance=balance-%s where user_id=%s and balance>=%s",[total_price,user_id,total_price])
                    if cur.rowcount == 0:  #受影响行数
                            return error.error_not_sufficient_funds(order_id)
                    cur.execute("update new_order set status=%s where order_id=%s and status=%s",["paid_but_not_delivered",order_id,'unpaid'])
                    conn.commit()
            except psycopg2.Error as e:
                if e.pgcode=="40001" and attempt<Retry_time:
                        attempt+=1
                        time.sleep(random.random()*attempt)
                        continue
                else:
                    return 528, "{}".format(str(e.pgerror+" "+e.pgcode)), ""
            except BaseException as e:  return 530, "{}".format(str(e))
            return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        attempt=0
        while(True):
            try:
                with self.get_conn() as conn:
                    cur=conn.cursor()
                    cur.execute("select password,balance from \"user\" where user_id=%s for update",[user_id,])
                    res=cur.fetchone()
                    if(res==None):
                        return error.error_non_exist_user_id(user_id)
                    elif res[0]!=password:
                        return error.error_authorization_fail()
                    elif res[1]<-add_value:
                        return error.error_non_enough_fund(user_id)
                    cur.execute("update \"user\" set balance=balance+%s where user_id=%s and balance>=%s",[add_value,user_id,-add_value])
                    if cur.rowcount == 0:  #受影响行数
                        return error.error_non_enough_fund(user_id)
                    conn.commit()
            except psycopg2.Error as e:
                if e.pgcode=="40001" and attempt<Retry_time:
                    attempt+=1
                    time.sleep(random.random()*attempt)
                    continue
                else:
                    return 528, "{}".format(str(e.pgerror+" "+e.pgcode)), ""
            except BaseException as e:  return 530, "{}".format(str(e))
            return 200, "ok"

    
    def cancel(self, user_id, order_id) -> (int, str):
        attempt=0
        while(True):
            try:
                with self.get_conn() as conn:
                    cur=conn.cursor()
                    unprossing_status = ["unpaid", "paid_but_not_delivered"]


                    cur.execute("select buyer_id, status, total_price, store_id from new_order WHERE order_id = %s", (order_id,))
                    order = cur.fetchone()
                    if not order:
                            cur.execute("select buyer_id, status, total_price, store_id from old_order WHERE order_id = %s", (order_id,))
                            order = cur.fetchone()
                            if not order:
                                    return error.error_non_exist_order_id(order_id)
                            else:
                                    return error.error_invalid_order_id(order_id)

                    buyer_id=order[0]
                    current_status = order[1]
                    total_price = order[2]
                    store_id = order[3]


                    if current_status not in unprossing_status:
                            return error.error_invalid_order_id(order_id)

                    if buyer_id != user_id:
                            return error.error_order_user_id(order_id, user_id)

                    cur.execute("""
                            UPDATE new_order
                            SET status = 'canceled'
                            WHERE order_id = %s and status in (%s,%s)
                    """, (order_id,unprossing_status[0],unprossing_status[1]))
                    if cur.rowcount == 0:
                                    return error.error_invalid_order_id(order_id)
                    cur.execute("select order_detail from new_order WHERE order_id = %s", (order_id,))
                    res = cur.fetchone()
                    detail=res[0].split('\n')
                    for tmp in detail:
                            tmp1=tmp.split(' ')
                            if(len(tmp1)<2):
                                    break
                            book_id,count=tmp1
                            cur.execute("""
                                    UPDATE book_info 
                                    SET stock_level = stock_level + %s, sales = sales - %s 
                                    WHERE book_id = %s AND store_id = %s
                            """, (count, count, book_id, store_id))

                    if current_status == "paid_but_not_delivered":
                            cur.execute(' UPDATE "user" SET balance = balance + %s WHERE user_id = %s', (total_price, user_id))

                    cur.execute('insert into old_order select * from new_order where order_id=%s',(order_id,))
                    cur.execute('delete from new_order where order_id=%s',(order_id,))

                    conn.commit()
                    return 200, "ok"

            except psycopg2.Error as e:
                if e.pgcode=="40001" and attempt<Retry_time:
                    attempt+=1
                    time.sleep(random.random()*attempt)
                    continue
                else:
                    return 528, "{}".format(str(e.pgerror+" "+e.pgcode)), ""
            except BaseException as e: return 530, "{}".format(str(e))

    
    def search_order(self, user_id):
        attempt=0
        while(True):
            try:
                with self.get_conn() as conn:
                    cur=conn.cursor()
                    cur.execute('SELECT 1 FROM "user" WHERE user_id = %s', (user_id,))
                    if not cur.fetchone():
                        return error.error_non_exist_user_id(user_id)+ ("",)

                    cur.execute("SELECT order_id FROM new_order WHERE buyer_id = %s", (user_id,))
                    orders = cur.fetchall()
                    result = [order[0] for order in orders]

                    #也在已完成的订单中查找
                    cur.execute("SELECT order_id FROM old_order WHERE buyer_id = %s", (user_id,))
                    orders = cur.fetchall()
                    for od in orders:
                        result.append(od[0])
                    return 200, "ok", result

            except psycopg2.Error as e:
                if e.pgcode=="40001" and attempt<Retry_time:
                    attempt+=1
                    time.sleep(random.random()*attempt)
                    continue
                else: return 528, "{}".format(str(e.pgerror+" "+e.pgcode)), ""
            except BaseException as e:  return 530, "{}".format(str(e)), ""

        

    def receive_books(self, user_id, order_id) -> (int, str):
        attempt=0
        while(True):
            try:
                with self.get_conn() as conn:
                    cur=conn.cursor()
                    cur.execute('SELECT user_id FROM "user" WHERE user_id = %s', (user_id,))
                    if not cur.fetchone():
                        return error.error_non_exist_user_id(user_id)

                    cur.execute("select buyer_id, status, total_price, store_id from new_order WHERE order_id = %s", (order_id,))
                    order = cur.fetchone()
                    if not order:
                        return error.error_invalid_order_id(order_id)

                    if order[1] != "delivered_but_not_received":
                        return error.error_invalid_order_id(order_id)

                    if order[0] != user_id:
                        return error.unmatched_order_user(order_id, user_id)

                    total_price = order[2]

                    store_id=order[3]
                    cur.execute("select user_id from store where store_id=%s",[store_id,])
                    res=cur.fetchone()
                    if(res is None):
                        return error.error_non_exist_store_id(store_id)
                    seller_id = res[0]
                    cur.execute("""
                        UPDATE new_order
                        SET status = 'received'
                        WHERE order_id = %s and status= 'delivered_but_not_received'
                    """, (order_id,))
                    if cur.rowcount == 0:  #受影响行数
                            return error.error_invalid_order_id(order_id)
                    cur.execute('UPDATE "user" SET balance = balance + %s WHERE user_id = %s', (total_price, seller_id))
                    
                    cur.execute('insert into old_order select * from new_order where order_id=%s',(order_id,))
                    cur.execute('delete from new_order where order_id=%s',(order_id,))
                    
                    conn.commit()
                    return 200, "ok"

            except psycopg2.Error as e:
                if e.pgcode=="40001" and attempt<Retry_time:
                    attempt+=1
                    time.sleep(random.random()*attempt)
                    continue
                else: return 528, "{}".format(str(e.pgerror+" "+e.pgcode)), ""
            except BaseException as e:  return 530, "{}".format(str(e))