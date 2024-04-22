import pymongo.errors
from be.model import db_conn
from be.model import error
import time


class Order(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def cancel_order(
            self, order_id: str) -> (int, str):
        session=self.client.start_session()
        session.start_transaction()
        order_available = "canceled"
        order_status = "canceled"
        valid_status = "valid"
        try:
            cursor=self.conn['new_order'].find_one({'order_id':order_id},session=session)
            if(len(cursor)==0):
                session.abort_transaction()
                session.end_session()
                return error.error_non_exist_order_id(order_id)
            
            if(cursor['status']!=valid_status):
                session.abort_transaction()
                session.end_session()
                return error.error_prossessing_order_id(order_id)
            
            cursor = self.conn['new_order'].update_one(
                {'order_id': order_id},
                {'$set': {'available': order_available, 'status': order_status}}
            )
        except pymongo.errors as e:
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

    def cancel_unpaid_orders(self) -> (int, str):
        session=self.client.start_session()
        session.start_transaction()
        valid_time = 20
        current_time = time.time()
        order_cancel_status = "unpaid"
        order_available = "canceled"
        order_status = "canceled"
        try:
            cursor= self.conn['new_order'].update_many(
                {
                    'order_time': {
                        '$gte': current_time - valid_time * 2,
                        '$lt': current_time - valid_time
                    },
                    'status': order_cancel_status
                },
                {
                    '$set': {
                        'available': order_available,
                        'status': order_status
                    }
                }
            )

        except pymongo.errors as e:
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