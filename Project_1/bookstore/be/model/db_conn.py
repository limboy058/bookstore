from be.model import store


class DBConn:

    def __init__(self):
        pass
    def get_conn(self):#when you need a connection
        return store.get_db_conn()
    def user_id_exist(self, user_id, cur):
        res = None
        cur.execute("select count(1) from \"user\" where user_id=%s",[user_id])
        res=cur.fetchone()
        if res[0]==0:
            cur.execute("select count(1) from dead_user where user_id=%s",[user_id])
            res=cur.fetchone()
            return res[0]!=0
        else:
            return True

    def book_id_exist(self, store_id, book_id, cur):
        res = None
        cur.execute("select count(1) from book_info where book_id= %s and store_id= %s",[book_id,store_id])
        res=cur.fetchone()
        return res[0]>0

    def store_id_exist(self, store_id, cur):
        res = None
        cur.execute("select count(1) from store where store_id= %s ",(store_id,))
        res=cur.fetchone()
        return res[0]>0

    def order_id_exist(self, order_id, cur):
        res = None
        cur.execute("select count(1) from new_order where order_id= %s",(order_id,))
        res=cur.fetchone()
        return res[0]>0
        
