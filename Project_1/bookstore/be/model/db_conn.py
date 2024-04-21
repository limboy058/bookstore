#from be.model import store
import store


class DBConn:
    def __init__(self):
        self.conn = store.get_db_conn()

    def user_id_exist(self, user_id):
        res=self.conn['user'].find({'user_id': user_id})
        results=[result for result in res]
        if(len(results)==0):
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        res=self.conn['store'].find({'store_id':store_id,'book_id':book_id})
        results=[result for result in res]
        if(len(results)==0):
            return False
        else:
            return True
        # cursor = self.conn.execute(
        #     "SELECT book_id FROM store WHERE store_id = ? AND book_id = ?;",
        #     (store_id, book_id),
        # )
        # row = cursor.fetchone()

    def store_id_exist(self, store_id):
        res=self.conn['user_store'].find({'store_id':store_id})
        results=[result for result in res]
        if(len(results)==0):
            return False
        else:
            return True


        # cursor = self.conn.execute(
        #     "SELECT store_id FROM user_store WHERE store_id = ?;", (store_id,)
        # )
        # row = cursor.fetchone()
        # if row is None:
        #     return False
        # else:
        #     return True


# if __name__ == "__main__":
#     dbcon=DBConn()
#     dbcon.conn['user'].insert_one({'name':'test','user_id':1234})
#     dbcon.conn['user'].insert_one({'name':'test'})
#     print(dbcon.user_id_exist(1234))