#注意:还未在表new_order上order_time处建立索引
#live_time订单有效时间默认1200,scan_interval为扫描间隔默认10  单位均为秒
 
import time,datetime
import pymongo.errors
import sys
sys.path.append('D:\\DS_bookstore\\Project_1\\bookstore')
from be.model import db_conn

class Scanner(db_conn.DBConn):
    def __init__(self,live_time=1200,scan_interval=10):
        db_conn.DBConn.__init__(self)
        self.live_time=live_time
        self.scan_interval=scan_interval

    def keep_running(self,keep=False):
        t=0
        while t<10:
            session=self.client.start_session()
            session.start_transaction()
            try:
                # ret=self.conn['new_order'].find()
                # for item in ret:
                #     print('此订单时间为',datetime.datetime.fromtimestamp(item['order_time']),'状态为',item['status'])
                ret = self.conn['new_order'].update_many(
                    {
                        'order_time': {
                            '$gte': int(time.time()) - self.live_time - self.scan_interval,
                            '$lt': int(time.time()) - self.live_time + self.scan_interval
                        },
                        'status': 'unpaid'
                    },
                    {
                        '$set': {
                            'status': 'canceled'
                        }
                    },
                    session=session
                )
                yield 200,ret.modified_count
                #return
            except pymongo.errors.PyMongoError as e:
                yield 528, "{}".format(str(e))
                return
            except Exception as e:
                yield 530, "{}".format(str(e))
                return
            session.commit_transaction()
            session.end_session()
            time.sleep(self.scan_interval)
            if not keep:
                t+=1
        

# if __name__ == "__main__":
#     tmp=Scanner(10,2)
#     g=tmp.keep_running(keep=True)
#     while 1:
#         try:
#             print(next(g))
#         except:
#             break