import jwt

# import sys
# sys.path.append('D:\\DS_bookstore\\Project_1\\bookstore')

import time
import logging
from be.model import error
from be.model import db_conn
import pymongo.errors

# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }


def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
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
        session=self.client.start_session()
        session.start_transaction()
        try:
            ret = self.conn['user'].find_one({'user_id':user_id},session=session)
            if ret is not None:
                return error.error_exist_user_id(user_id)
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            ret=self.conn['user'].insert_one({'user_id':user_id,'password':password,'balance':0,'token':token,'terminal':terminal},session=session)
            if not ret.acknowledged:  return 528, "{}".format(str(ret))
        except BaseException as e:
            return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"

    def check_token(self, user_id: str, token: str,session=None) -> (int, str):
        ret=1
        if(session!=None):
            ret=self.conn['user'].find_one({'user_id':user_id},{'_id':0,'token':1},session=session)
        else:
            ret=self.conn['user'].find_one({'user_id':user_id},{'_id':0,'token':1})
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
        ret = 1
        if (session != None):
            ret = self.conn['user'].find_one({'user_id': user_id}, {
                '_id': 0,
                'password': 1
            },
                                             session=session)
        else:
            ret = self.conn['user'].find_one({'user_id': user_id}, {
                '_id': 0,
                'password': 1
            })
        if ret is None:
            return error.error_authorization_fail()

        if password != ret['password']:
            return error.error_authorization_fail()

        return 200, "ok"


    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        session=self.client.start_session()
        session.start_transaction()
        token = ""
        try:
            code, message = self.check_password(user_id, password,session=session)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            ret=self.conn['user'].update_one({'user_id':user_id},{'$set':{'token':token,'terminal':terminal}},session=session)
            if not ret.acknowledged:  return 528, "{}".format(str(ret))
            if ret.modified_count == 0:
                return error.error_authorization_fail() + ("", )
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e)), ""
        session.commit_transaction()
        session.end_session()
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> bool:
        session=self.client.start_session()
        session.start_transaction()
        try:
            code, message = self.check_token(user_id, token,session=session)
            if code != 200:
                return code, message
            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)
            ret=self.conn['user'].update_one({'user_id':user_id},{'$set':{'token':dummy_token,'terminal':terminal}},session=session)
            if not ret.acknowledged:  return 528, "{}".format(str(ret))
            if ret.modified_count == 0:
                return error.error_authorization_fail()
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        session=self.client.start_session()
        session.start_transaction()
        try:
            code, message = self.check_password(user_id, password,session=session)
            if code != 200:
                return code, message
              
            cursor = self.conn['new_order'].find({'user_id': user_id},session=session)
            for item in cursor:
                if item['status'] !='received' and item['status'] != 'canceled':
                    return error.error_unfished_buyer_orders()
                
            store_list=list()
            cursor = self.conn['user_store'].find({'user_id': user_id},session=session)
            for item in cursor:
                store_list.append(item['store_id'])
            if len(store_list)!=0:
                cursor = self.conn['new_order'].find({'store_id': {'$in':store_list}},session=session)
                for item in cursor:
                    if item['status'] !='received' and item['status'] != 'canceled':
                        return error.error_unfished_seller_orders()
                    
                ret = self.conn['store'].update_many({'store_id': {'$in':store_list}},{'$set':{'stock_level':0}},session=session)

            ret = self.conn['user'].delete_one({'user_id': user_id},session=session)

        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> bool:
        session=self.client.start_session()
        session.start_transaction()
        try:
            code, message = self.check_password(user_id, old_password,session=session)
            if code != 200:
                return code, message
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            ret=self.conn['user'].update_one({'user_id':user_id},{'$set':{'password':new_password,'token':token,'terminal':terminal}},session=session)
            if not ret.acknowledged:  return 528, "{}".format(str(ret))
            if ret.modified_count == 0:
                return error.error_authorization_fail()
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"


# import be.model

# if __name__ == "__main__":
#     tmp=User()
#     st=be.model.store.Store()
#     st.clear_tables()

    

#     print(tmp.register('uid1','333'))
#     print(tmp.register('uid2','333'))
#     for item in tmp.conn['user'].find():
#         print(item)

#     buyer=be.model.buyer.Buyer()
#     seller=be.model.seller.Seller()
#     print(seller.create_store('uid1','sid1'))
#     print(seller.conn['store'].insert_one({'store_id':'sid1','book_id':'bid1','stock_level':10}))

#     ret=buyer.new_order('uid2','sid1',[('bid1',1)])
#     print(ret)

    
#     print(tmp.unregister('uid1','333'))
#     print(tmp.unregister('uid2','333'))
#     print(buyer.cancel('uid1',ret[2]))
#     print(tmp.unregister('uid1','333'))
#     print(tmp.unregister('uid2','333'))