import json
import os,base64
import random
import time
from fe.conf import Retry_time
# import sys
# sys.path.append("D:\\code\数据库系统\\AllStuRead-master\\Project_1\\bookstore")


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
        attempt=0
        while(True):
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
                        
                        #加载路径
                        current_file_path = os.path.abspath(__file__)
                        current_directory = os.path.dirname(current_file_path)
                        parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
                        data_path=os.path.abspath(parent_directory+'/data')
                        #保证路径存在
                        os.makedirs(data_path, exist_ok=True)
                        os.makedirs(data_path+'/img', exist_ok=True)
                        os.makedirs(data_path+'/book_intro', exist_ok=True)
                        os.makedirs(data_path+'/auth_intro', exist_ok=True)
                        os.makedirs(data_path+'/content', exist_ok=True)
                        #加载json中的资源並存儲
                        data = json.loads(book_json)
                        image_data=base64.b64decode(data['pictures'])
                        with open(data_path+'/img/'+data['id']+'.png', 'wb') as image_file:
                            image_file.write(image_data)
                        with open(data_path+'/auth_intro/'+data['id']+'.txt', 'w',encoding='utf-8') as ai_file:
                            ai_file.write(data['author_intro'])
                        with open(data_path+'/book_intro/'+data['id']+'.txt', 'w',encoding='utf-8') as bi_file:
                            bi_file.write(data['book_intro'])
                        with open(data_path+'/content/'+data['id']+'.txt', 'w',encoding='utf-8') as ct_file:
                            ct_file.write(data['content'])

                        cur.execute('''
                                    insert into book_info 
                                    (book_id,store_id,price,stock_level,sales,title,author,publisher,original_title,
                                    translator,pub_year,pages,currency_unit,binding,isbn,author_intro,book_intro,content,picture,tags)
                                    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
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
                            './be/data/auth_intro/'+data['id']+'.txt',
                            './be/data/book_intro/'+data['id']+'.txt',
                            './be/data/content/'+data['id']+'.txt',
                            './be/data/img/'+data['id']+'.png',
                            data['tags']
                        ))
                        conn.commit()
            except psycopg2.Error as e:
                if e.pgcode=="40001" and attempt<Retry_time:
                    attempt+=1
                    time.sleep(random.random()*attempt)
                    continue
                else:
                    return 528, "{}".format(str(e.pgerror+" "+e.pgcode)), ""
            except BaseException as e:
                return 530, "{}".format(str(e))
            return 200, "ok"
    
    def del_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
    ):
        attempt=0
        while(True):
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

                        
                        if not self.book_id_exist(store_id, book_id, cur):
                            return error.error_non_exist_book_id(book_id)
                        cur.execute(
                        'select stock_level from book_info where book_id=%s and store_id=%s',
                        (
                            book_id,
                            store_id,
                        ))
                        book_exist = cur.fetchone()
                        if not book_exist:
                            return error.error_non_exist_book_id(book_id)
                        cur.execute(
                        'update book_info set stock_level = 0 where book_id=%s and store_id=%s',
                        (
                            book_id,
                            store_id,
                        ))

                        conn.commit()

            except psycopg2.Error as e:
                if e.pgcode=="40001" and attempt<Retry_time:
                    attempt+=1
                    time.sleep(random.random()*attempt)
                    continue
                else:
                    return 528, "{}".format(str(e.pgerror+" "+e.pgcode)), ""
            except BaseException as e:
                return 530, "{}".format(str(e))
            return 200, "ok"


    def add_stock_level(self, user_id: str, store_id: str, book_id: str,
                        add_stock_level: int):
        attempt=0
        while(True):
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
                if e.pgcode=="40001" and attempt<Retry_time:
                    attempt+=1
                    time.sleep(random.random()*attempt)
                    continue
                else:
                    return 528, "{}".format(str(e.pgerror+" "+e.pgcode)), ""
            except BaseException as e:
                return 530, "{}".format(str(e))
            return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        attempt=0
        while(True):
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
                if e.pgcode=="40001" and attempt<Retry_time:
                    attempt+=1
                    time.sleep(random.random()*attempt)
                    continue
                else:
                    return 528, "{}".format(str(e.pgerror+" "+e.pgcode)), ""
            except BaseException as e:
                return 530, "{}".format(str(e))
            return 200, "ok"


    
    def send_books(self, store_id: str, order_id: str) -> (int, str):
        attempt=0
        while(True):
            try:
                with self.get_conn() as conn:
                    cur=conn.cursor()

                    cur.execute("SELECT 1 FROM store WHERE store_id = %s", (store_id,))
                    if not cur.fetchone():
                        return error.error_non_exist_store_id(store_id)

                    cur.execute("""
                        select status,store_id from new_order
                        WHERE order_id = %s
                    """, (order_id,))
                    order = cur.fetchone()
                    if not order:
                        return error.error_invalid_order_id(order_id)

                    if order[0] != "paid_but_not_delivered":
                        return error.error_invalid_order_id(order_id)

                    if order[1] != store_id:
                        return error.unmatched_order_store(order_id, store_id)
                    
                    cur.execute("""
                        UPDATE new_order
                        SET status = 'delivered_but_not_received'
                        WHERE order_id = %s and status='paid_but_not_delivered'
                    """, (order_id,))
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


    def search_order(self, seller_id, store_id):
        try:
            with self.get_conn() as conn:
                cur=conn.cursor()                
                if not self.user_id_exist(seller_id, cur):
                        return error.error_non_exist_user_id(seller_id)+ ("",)
                if not self.store_id_exist(store_id, cur):
                    return error.error_non_exist_store_id(store_id)+ ("",)

                cur.execute('SELECT 1 FROM store WHERE store_id = %s AND user_id = %s', (store_id, seller_id))
                if not cur.fetchone():
                    return error.unmatched_seller_store(seller_id, store_id)+ ("",)
                    

                cur.execute("SELECT order_id FROM new_order WHERE store_id = %s", (store_id,))
                orders = cur.fetchall()
                result = [order[0] for order in orders]
                
                #也在已完成的订单中查找
                cur.execute("SELECT order_id FROM old_order WHERE store_id = %s", (store_id,))
                orders = cur.fetchall()
                for od in orders:
                    result.append(od[0])

                return 200, "ok", result

        except psycopg2.Error as e:return 528, "{}".format(str(e)), ""
        except BaseException as e:return 530, "{}".format(str(e)), ""
    
    def cancel(self, store_id, order_id) -> (int, str):
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
                    store_id_ = order[3]

                    if current_status not in unprossing_status:
                        return error.error_invalid_order_id(order_id)

                    if store_id != store_id_:
                        return error.unmatched_order_store(order_id, store_id)
                    
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
                        cur.execute(' UPDATE "user" SET balance = balance + %s WHERE user_id = %s', (total_price, buyer_id))

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

# import fe.access.book
# if  __name__=='__main__':

#     b=fe.access.book.BookDB()
#     s=Seller()
#     books=b.get_book_info(12,10)
#     for book in books:
#         js=json.dumps(book.__dict__)
#         data=json.loads(js)
#         print(s.add_book('uid1','sid1',data['id'],js,10))
        

# import datetime
# from be.model.store import clean_db

# if __name__=="__main__":
#     clean_db()
#     seller=Seller()
#     conn=seller.get_conn()
#     cur=conn.cursor()
#     cur.execute("insert into \"user\" values('seller','abc',0,'a','a')")
#     cur.execute("insert into \"user\" values('buyer','abc',1000,'a','a')")
#     cur.execute("insert into store values('store','seller')")
#     cur.execute("insert into book_info (book_id,store_id,stock_level,sales,price) values ('mamba out!','store',10,0,50)")
#     query="insert into new_order values(%s,%s,%s,%s,%s,%s)"
#     order_id = 'order66666'
#     cur.execute(query,[order_id,'store','buyer','unpaid',datetime.datetime.now(),25000])
#     conn.commit()
#     res=seller.del_book('seller','store','mamba out!')
#     print(res)

#     conn=seller.get_conn()
#     cur=conn.cursor()
#     cur.execute("select * from new_order")
#     res=cur.fetchall()
#     print(res)
#     conn.commit()

#     conn=seller.get_conn()
#     cur=conn.cursor()
#     res=seller.send_books('store',order_id)
#     print(res)
#     conn.commit()

#     conn=seller.get_conn()
#     cur=conn.cursor()
#     cur.execute("UPDATE new_order SET status = %s",['paid_but_not_delivered',])
#     conn.commit()
#     cur=conn.cursor()

#     conn=seller.get_conn()
#     cur=conn.cursor()
#     cur.execute("select * from new_order")
#     res=cur.fetchall()
#     print(res)
#     conn.commit()

#     conn=seller.get_conn()
#     cur=conn.cursor()
#     res=seller.send_books('store',order_id)
#     print(res)
#     conn.commit()

    

#     conn=seller.get_conn()
#     cur=conn.cursor()
#     cur.execute("select * from new_order")
#     res=cur.fetchall()
#     print(res)
#     conn.commit()

#     conn=seller.get_conn()
#     cur=conn.cursor()
#     res=seller.search_order('seller','store')
#     print(res)

