from be.model import store

class DBConn:
    def __init__(self):
        self.conn = store.get_db_conn()
        self.client=store.get_db_client()
    def user_id_exist(self, user_id,session=None):
        res=None
        if(session is not None):
            res=self.conn['user'].find_one({'user_id': user_id},session=session)
        else:
            res=self.conn['user'].find_one({'user_id': user_id})
        if res is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id,session=None):
        res=None
        if(session!=None):
            res=self.conn['store'].find_one({'store_id':store_id,'book_id':book_id},session=session)
        else:
            res=self.conn['store'].find_one({'store_id':store_id,'book_id':book_id})
        if res is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id,session=None):
        res=None
        if(session!=None):
            res=self.conn['user'].find_one({'store_id':store_id},session=session)
        else:
            res=self.conn['user'].find_one({'store_id':store_id})
        if res is None:
            return False
        else:
            return True
    def order_id_exist(self, order_id,session=None):
        res=None
        if(session!=None):
            res=self.conn['new_order'].find_one({'order_id':order_id},session=session)
        else:
            res=self.conn['new_order'].find_one({'order_id':order_id})
        if res is None:
            return False
        else:
            return True


# if __name__ == "__main__":
#     dbcon=DBConn()
#     dbcon.conn['user'].insert_one({'name':'test','user_id':1234})
#     dbcon.conn['user'].insert_one({'name':'test'})
#     print(dbcon.user_id_exist(1234))