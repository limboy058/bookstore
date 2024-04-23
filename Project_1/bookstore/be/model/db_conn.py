from be.model import store
#import store


class DBConn:
    def __init__(self):
        self.conn = store.get_db_conn()
        self.client=store.get_db_client()
    def user_id_exist(self, user_id):
        res=self.conn['user'].find_one({'user_id': user_id})
        if res is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        res=self.conn['store'].find_one({'store_id':store_id,'book_id':book_id})
        if res is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        res=self.conn['user_store'].find_one({'store_id':store_id})
        if res is None:
            return False
        else:
            return True
    def order_id_exist(self, order_id):
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