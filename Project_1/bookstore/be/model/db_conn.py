from be.model import store


class DBConn:

    def __init__(self):
        self.conn = store.get_db_conn()

    def update_conn(self):#when you need a connection
        self.conn=store.get_db_conn()
    def user_id_exist(self, user_id):
        res = None
        with self.conn.cursor() as cur:
            cur.execute("select * from \"user\" where user_id=%s",[user_id])
            res=cur.fetchone()
            if res==None:
                cur.execute("select * from dead_user where user_id=%s",[user_id])
                res=cur.fetchone()
                return res!=None
            else:
                return True

    def book_id_exist(self, store_id, book_id):
        res = None
        with self.conn.cursor() as cur:
            cur.execute("select * from store where book_id= %s and store_id= %s",[book_id,store_id])
            res=cur.fetchone()
            return res!=None

    def store_id_exist(self, store_id):
        res = None
        with self.conn.cursor() as cur:
            cur.execute("select * from store where store_id= \""+store_id+"\"")
            res=cur.fetchone()
            return res!=None

    def order_id_exist(self, order_id):
        res = None
        with self.conn.cursor() as cur:
            cur.execute("select * from new_order where order_id= \""+order_id+"\"")
            res=cur.fetchone()
            return res!=None
        
