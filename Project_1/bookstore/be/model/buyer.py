import pymongo
import uuid
# import sys
# sys.path.append('D:\\DS_bookstore\\Project_1\\bookstore')
import json
import logging
import time
import pymongo.errors
from be.model import db_conn
from be.model import error

class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        try:
            session=self.client.start_session()
            session.start_transaction()
            if not self.user_id_exist(user_id,session=session):
                return error.error_non_exist_user_id(user_id) + (order_id,)

            res=self.conn['user'].find_one({'store_id':store_id},{'user_id':1},session=session)
            if res is None:
                return error.error_non_exist_store_id(store_id) + (order_id,)
            seller_id=res['user_id']

            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))
            sum_price=0
            for book_id, count in id_and_count:
                cursor=self.conn['store'].find_one({'store_id':store_id,'book_id':book_id},session=session)
                results=cursor
                if results==None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)
                stock_level = int(results['stock_level'])
                book_info = results['book_info']
                price = book_info["price"]
                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)
                sum_price += price * count
                cursor=self.conn['store'].find_one_and_update({'store_id':store_id,'book_id':book_id},
                                                        {"$inc":{"stock_level":-count,"sales":count}},session=session)
            self.conn['new_order'].insert_one({'order_id':uid,'store_id':store_id,'seller_id':seller_id,'user_id':user_id,'status':'unpaid','order_time':int(time.time()),'total_price':sum_price,'detail':id_and_count},session=session)
            session.commit_transaction()
            order_id = uid
        except pymongo.errors.PyMongoError as e:return 528, "{}".format(str(e)),""
        except BaseException as e:return 530, "{}".format(str(e)),""
        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        conn = self.conn
        session=self.client.start_session()
        session.start_transaction()
        try:
            cursor=conn['new_order'].find_one_and_update({'order_id':order_id,'status':"unpaid"},{'$set':{'status':'paid_but_not_delivered'}},session=session)
            if cursor is None:
                return error.error_invalid_order_id(order_id)
            order_id = cursor['order_id']
            buyer_id = cursor['user_id']
            seller_id = cursor['seller_id']
            if not self.user_id_exist(seller_id,session=session):
                return error.error_non_exist_user_id(seller_id)
            total_price = cursor['total_price']
            if buyer_id != user_id:
                return error.error_authorization_fail()
            cursor=conn['user'].find_one_and_update({'user_id':user_id},{'$inc':{'balance':-total_price}},session=session)
            if cursor is None:
                return error.error_non_exist_user_id(buyer_id)
            if password != cursor['password']:
                return error.error_authorization_fail()
            if(cursor['balance']<total_price):
                return error.error_not_sufficient_funds(order_id)
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        session=self.client.start_session()
        session.start_transaction()
        try:
            cursor=self.conn['user'].find_one_and_update({'user_id':user_id},{'$inc':{'balance':add_value}},session=session)
            if(cursor['password']!=password):
                return error.error_authorization_fail()
            if(cursor['balance']<-add_value):
                return error.error_non_enough_fund(user_id)
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"

    def cancel(self, user_id, order_id) -> (int, str):
        session=self.client.start_session()
        session.start_transaction()
        unprosssing_status =["unpaid", "paid_but_not_delivered"]
        try:
            cursor=self.conn['new_order'].find_one_and_update({'order_id':order_id},{'$set': {'status': "canceled"}},session=session)
            if(cursor is None):
                return error.error_non_exist_order_id(order_id)

            if(cursor['status'] not in unprosssing_status):
                return error.error_invalid_order_id(order_id)

            if(cursor['user_id'] !=user_id):
                return error.error_order_user_id(order_id, user_id)

            current_status=cursor['status']
            store_id=cursor['store_id']
            total_price=cursor['total_price']
            detail=list(cursor['detail'])
            
            for i in detail:
                self.conn['store'].update_one({'book_id':i[0],'store_id':store_id},{'$inc':{"stock_level":i[1],"sales":-i[1]}},session=session)
            if(current_status=="paid_but_not_delivered"):
                cursor=self.conn['user'].find_one_and_update(
                    {'user_id':user_id},{'$inc':{'balance':total_price}},session=session)

        except pymongo.errors.PyMongoError as e:return 528, "{}".format(str(e))
        except BaseException as e:return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"

    def search_order(self, user_id):
        try:
            cursor=self.conn['new_order'].find({'user_id':user_id})
            result=list()
            for i in cursor:
                result.append(i['order_id'])
        except pymongo.errors.PyMongoError as e:return self.pymongo_exception_handle(e)
        except BaseException as e:return self.base_exception_handle(e)
        return 200, "ok", result


    def receive_books(self, order_id) -> (int, str):
        session=self.client.start_session()
        session.start_transaction()
        try:
            cursor = self.conn['new_order'].find_one_and_update(
                {'order_id': order_id},
                {'$set': {'status': "received"}},
                session=session
            )
            if(cursor==None):
                return error.error_invalid_order_id(order_id)
            if(cursor['status'] != "delivered_but_not_received"):
                return error.error_invalid_order_id(order_id)
            total_price=cursor['total_price']
            seller_id=cursor['seller_id']
            cursor=self.conn['user'].find_one_and_update({'user_id':seller_id},{'$inc':{'balance':total_price}},session=session)

        except pymongo.errors.PyMongoError as e:return 528, "{}".format(str(e))
        except BaseException as e:return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"
