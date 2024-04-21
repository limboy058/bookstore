import pymongo
from be.model import error
from be.model import user# 仅用于测试
from be.model import db_conn
# 未做事务处理

class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
        book_json_str: str,
        stock_level: int,
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            ret = self.conn['store'].insert_one({'store_id':store_id,'book_id':book_id,'book_info':book_json_str,'stock_level':stock_level})
            if not ret.acknowledged:  return 528, "{}".format(str(ret))  
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(
        self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)
            
            ret = self.conn['store'].update_one({'store_id':store_id,'book_id':book_id},{'$inc': {'stock_level': add_stock_level}})
            if not ret.acknowledged:  return 528, "{}".format(str(ret)) 
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            
            ret = self.conn['user_store'].insert_one({'store_id':store_id,'user_id':user_id})
            if not ret.acknowledged:  return 528, "{}".format(str(ret))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

# if __name__ == "__main__":
#     tmp=Seller()
#     us=user.User()
#     print(us.register('uid1','333'))
#     for item in tmp.conn['user'].find():
#         print(item)
    
#     print(tmp.create_store('uid2','sid1'))
#     print(tmp.create_store('uid1','sid1'))
#     for item in tmp.conn['user_store'].find():
#         print(item)

#     print(tmp.add_book('uid1','sid2','bid1','hellow orld',10))
#     print(tmp.add_book('uid2','sid1','bid3','hellow orld',10))

#     print(tmp.add_book('uid1','sid1','bid1','hellow orld',10))
#     for item in tmp.conn['store'].find():
#         print(item)

#     print(tmp.add_stock_level('uid1','sid1','bid1',10))
#     for item in tmp.conn['store'].find():
#         print(item)
    
