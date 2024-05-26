#live_time订单有效时间默认1200,scan_interval为扫描间隔默认10  单位均为秒

import time, datetime
import pymongo.errors
from be.model import db_conn


class Scanner(db_conn.DBConn):

    def __init__(self, live_time=1200, scan_interval=10):
        db_conn.DBConn.__init__(self)
        self.live_time = live_time
        self.scan_interval = scan_interval

    def keep_running(self, keep=False):
        t = 0
        while t < 10:
            session = self.client.start_session()
            session.start_transaction()
            try:
                # ret=self.conn['new_order'].find()
                # for item in ret:
                #     print('此订单时间为',datetime.datetime.fromtimestamp(item['order_time']),'状态为',item['status'])
                cur_time = int(time.time())
                cursor = self.conn['new_order'].find(
                    {
                        'order_time': {
                            '$gte':
                            cur_time - self.live_time - self.scan_interval,
                            '$lt':
                            cur_time - self.live_time + self.scan_interval
                        },
                        'status': 'unpaid'
                    }, {
                        'order_id': 1,
                        'store_id': 1,
                        'detail': 1
                    },
                    session=session)
                for i in cursor:
                    detail = list(i['detail'])
                    store_id = i['store_id']
                    for j in detail:
                        self.conn['store'].update_many(
                            {
                                'store_id': store_id,
                                'book_id': j[0]
                            }, {'$inc': {
                                'stock_level': j[1],
                                'sales': -j[1]
                            }},
                            session=session)
                ret = self.conn['new_order'].update_many(
                    {
                        'order_time': {
                            '$gte':
                            cur_time - self.live_time - self.scan_interval,
                            '$lt':
                            cur_time - self.live_time + self.scan_interval
                        },
                        'status': 'unpaid'
                    }, {'$set': {
                        'status': 'canceled'
                    }},
                    session=session)
                yield 200, ret.modified_count
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
                t += 1
