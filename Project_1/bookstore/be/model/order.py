import pymongo.errors
from be.model import db_conn
from be.model import error
# import db_conn
# import error
import time


class Order(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def cancel_order(
            self, order_id: str) -> (int, str):
        session=self.client.start_session()
        session.start_transaction()
        order_status = "canceled"
        unprosssing_status =["unpaid", "paid_but_not_delivered"]
        try:
            cursor=self.conn['new_order'].find_one({'order_id':order_id},session=session)
            if(len(cursor)==0):
                session.abort_transaction()
                session.end_session()
                return error.error_non_exist_order_id(order_id)
            
            if(cursor['status'] not in unprosssing_status):
                session.abort_transaction()
                session.end_session()
                return error.error_invalid_order_id(order_id)
            
            cursor = self.conn['new_order'].update_one(
                {'order_id': order_id},
                {'$set': {'status': order_status}}
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
        interval_time =1
        exist_time=20
        current_time = time.time()/60
        order_cancel_status = "unpaid"
        order_status = "canceled"
        try:
            cursor= self.conn['new_order'].update_many(
                {
                    'order_time': {
                        '$gte': current_time - interval_time*2-exist_time,
                        '$lt': current_time - exist_time
                    },
                    'status': order_cancel_status
                },
                {
                    '$set': {
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
    
if __name__ == "__main__":
    print(time.time())