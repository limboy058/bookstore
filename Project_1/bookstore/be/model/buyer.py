import pymongo
import uuid
import json
import logging
import time
import pymongo.errors
from be.model import db_conn
from be.model import error
from be.model.order import Order
# import db_conn
# import error
# from order import Order

class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))
            session=self.client.start_session()
            session.start_transaction()
            for book_id, count in id_and_count:
                cursor=self.conn['store'].find_one({'store_id':store_id,'book_id':book_id},session=session)
                results=cursor
                if results==None:
                    session.abort_transaction()
                    session.end_session()
                    return error.error_non_exist_book_id(book_id) + (order_id,)
                stock_level = int(results['stock_level'])
                book_info = results['book_info']
                price = book_info["price"]
                if stock_level < count:
                    session.abort_transaction()
                    session.end_session()
                    return error.error_stock_level_low(book_id) + (order_id,)
                cursor=self.conn['store'].find_one_and_update({'store_id':store_id,'book_id':book_id,'stock_level':{'$gte':count}},
                                                        {"$inc":{"stock_level":-count}},session=session)
                results=cursor
                if results==None:
                    session.abort_transaction()
                    session.end_session()
                    return error.error_stock_level_low(book_id) + (order_id,)
                
                cursor=self.conn['new_order_detail'].insert_one({'order_id':uid,'book_id':book_id,'count':count,'price':price},session=session)
            self.conn['new_order'].insert_one({'order_id':uid,'store_id':store_id,'user_id':user_id,'status':'unpaid','order_time':int(time.time())},session=session)
            session.commit_transaction()
            order_id = uid
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""
        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        conn = self.conn
        session=self.client.start_session()
        session.start_transaction()
        try:
            cursor=conn['new_order'].find_one({'order_id':order_id},session=session)
            if cursor is None:
                session.abort_transaction()
                session.end_session()
                return error.error_invalid_order_id(order_id)
            order_id = cursor['order_id']
            buyer_id = cursor['user_id']
            store_id = cursor['store_id']
            if buyer_id != user_id:
                session.abort_transaction()
                session.end_session()
                return error.error_authorization_fail()
            cursor=conn['user'].find_one({'user_id':user_id},session=session)
            if cursor is None:
                session.abort_transaction()
                session.end_session()
                return error.error_non_exist_user_id(buyer_id)
            balance = cursor['balance']
            if password != cursor['password']:
                session.abort_transaction()
                session.end_session()
                return error.error_authorization_fail()
            cursor=conn['user_store'].find_one({'store_id':store_id},session=session)
            if cursor is None:
                session.abort_transaction()
                session.end_session()
                return error.error_non_exist_store_id(store_id)
            seller_id = cursor['user_id']
            if not self.user_id_exist(seller_id):
                session.abort_transaction()
                session.end_session()
                return error.error_non_exist_user_id(seller_id)
            cursor=conn['new_order_detail'].find({'order_id':order_id},session=session)
            total_price = 0
            for row in cursor:
                count = row['count']
                price = row['price']
                total_price = total_price + price * count
            if balance < total_price:
                session.abort_transaction()
                session.end_session()
                return error.error_not_sufficient_funds(order_id)
            cursor=conn['user'].find_one_and_update({'user_id':user_id,'balance':{'$gte':total_price}},{'$inc':{'balance':-total_price}},session=session)
            if cursor is None:
                session.abort_transaction()
                session.end_session()
                return error.error_not_sufficient_funds(order_id)
            cursor=conn['user'].find_one_and_update({'user_id':seller_id},{'$inc':{'balance':total_price}},session=session)
            if cursor is None:
                session.abort_transaction()
                session.end_session()
                return error.error_non_exist_user_id(seller_id)
            #cursor=conn['new_order'].delete_one({'order_id':order_id},session=session)
            conn['new_order'].update_one({'order_id':order_id},{'$set':{'status':'paid_but_not_delivered'}},session=session)
            if cursor is None:
                session.abort_transaction()
                session.end_session()
                return error.error_invalid_order_id(order_id)
            # cursor=conn['new_order_detail'].delete_one({'order_id':order_id},session=session)
            # if cursor is None:
            #     session.abort_transaction()
            #     session.end_session()
            #     return error.error_invalid_order_id(order_id)
        except BaseException as e:
            return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        session=self.client.start_session()
        session.start_transaction()
        try:
            cursor=self.conn['user'].find_one({'user_id':user_id},session=session)
            if cursor is None:
                session.abort_transaction()
                session.end_session()
                return error.error_authorization_fail()
            if(cursor['password']!=password):
                session.abort_transaction()
                session.end_session()
                return error.error_authorization_fail()
            cursor=self.conn['user'].find_one_and_update({'user_id':user_id},{'$inc':{'balance':add_value}},session=session)
            if cursor is None:
                session.abort_transaction()
                session.end_session()
                return error.error_non_exist_user_id(user_id)
        except pymongo.errors.PyMongoError as e:
            session.abort_transaction()
            session.end_session()
            return 528, "{}".format(str(e))
        except Exception as e:
            session.abort_transaction()
            session.end_session()
            return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"

# import seller
# import user

# if __name__ == "__main__":
#     buyer=Buyer()
#     s=seller.Seller()
#     u=user.User()
#     # res=u.register('bigone','hey')
#     # res=s.create_store('bigone','store1')
#     # print(res)
#     # res=s.add_book('bigone','store1','book1','',2)
#     # print(res)
#     # res=s.add_book('bigone','store1','book2','',6)
#     # print(res)
#     # res=u.register('123','hey')
#     # print(res)
#     #res1=buyer.new_order('123','store1',[('book1',1),('book2',2)])
#     #res1=buyer.payment('123','hey','123_store1_a735a43c-ffcf-11ee-924a-d4548b9011a8')
#     res1=buyer.add_funds('bigone','hey',99999)
#     print(res1)
#     res=buyer.conn['new_order'].find()
#     for i in res:
#         print(i)
    def cancel(self, user_id, order_id) -> (int, str):
        session=self.client.start_session()
        session.start_transaction()
        valid_status = 'unpaid'
        try:
            cursor=self.conn['new_order'].find_one({'order_id':order_id},session=session)
            if(cursor is None):
                session.abort_transaction()
                session.end_session()
                return error.error_non_exist_order_id(order_id)
            
            if(cursor['status']!=valid_status):
                session.abort_transaction()
                session.end_session()
                return error.error_invalid_order_id(order_id)

            if(cursor['user_id']!=user_id):
                session.abort_transaction()
                session.end_session()
                return error.error_order_user_id(order_id, user_id)

            o = Order()
            res1,res2=o.cancel_order(order_id)
            if(res1!=200):
                session.abort_transaction()
                session.end_session()
                return res1,res2

        except pymongo.errors.PyMongoError as e:
            session.abort_transaction()
            session.end_session()
            return 528, "{}".format(str(e))
        except Exception as e:
            session.abort_transaction()
            session.end_session()
            return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"
    
    #历史订单，表项要返回什么捏
    def search_order(self, user_id):
        session=self.client.start_session()
        session.start_transaction()
        try:
            cursor=self.conn['new_order'].find({'user_id':user_id},session=session)
            result=list()
            for i in cursor:
                result.append(i['order_id'])

        except pymongo.errors.PyMongoError as e:
            session.abort_transaction()
            session.end_session()
            return 528, "{}".format(str(e))
        except Exception as e:
            session.abort_transaction()
            session.end_session()
            return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok", result
    

    def receive_books(self,user_id, order_id) -> (int, str):
        session=self.client.start_session()
        session.start_transaction()
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.order_id_exist(order_id): 
                return error.error_invalid_order_id(order_id)
            
            cursor = self.conn['new_order'].find_one({'user_id':user_id,'order_id':order_id}, session=session)
            if(cursor['status'] != "delivered_but_not_received"):
                session.abort_transaction()
                session.end_session()
                return error.error_invalid_order_id(order_id)
            
            if(cursor['user_id']!=user_id):
                session.abort_transaction()
                session.end_session()
                return error.error_order_user_id(order_id, user_id)

            cursor = self.conn['new_order'].update_one(
                {'order_id': order_id},
                {'$set': {'status': "received"}},
                session=session
            )

        except BaseException as e:
            session.abort_transaction()
            session.end_session()
            return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"

