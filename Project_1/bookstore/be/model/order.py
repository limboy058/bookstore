import sqlite3 as sqlite
from be.model import db_conn
from be.model import error
import time


class Order(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def cancel_order(
            self, order_id: str) -> (int, str):
        order_available = "canceled"
        order_status = "canceled"
        try:
            cursor = self.conn.execute(
                "SELECT order_available from new_order where order_id = ?", (
                    order_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_order_id()

            if row[0] != "valid":
                return error.error_prossessing_order_id()

            cursor = self.conn.execute(
                "UPDATE new_order SET available = ?, status = ? WHERE order_id = ?",
                (order_available, order_status, order_id),
            )

            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def cancel_unpaid_orders(self) -> (int, str):
        valid_time = 20
        current_time = time.time()
        order_cancel_status = "unpaid"
        order_available = "canceled"
        order_status = "canceled"
        try:
            cursor = self.conn.execute(
                "update new_order set available = ?, status = ? and where order_time >= ? and order_time < ? and status = ?", (
                order_available, order_status, current_time - valid_time*2, current_time - valid_time , order_cancel_status,)
            )

            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"