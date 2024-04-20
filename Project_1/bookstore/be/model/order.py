import sqlite3 as sqlite
import uuid
import json
import logging
from be.model import db_conn
from be.model import error

#取消定单功能实现ing

class Order(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

# conn.execute(
#     "CREATE TABLE IF NOT EXISTS new_order( "
#     "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT)"
# )

    def cancel_order(
        self, order_id: str, user_id: str, store_id: str, int
    ) -> (int, str):
        order_available="canceled"
        order_status="canceled"
        try:
            # if not self.user_id_exist(user_id):
            #     return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)

            cursor = self.conn.execute(
                "SELECT user_id, store_id, order_available from new_order where order_id=?", (order_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_order_id()

            if row[0] != user_id:
                return error.error_invalid_user_id()

            if row[1] != store_id:
                return error.error_invalid_store_id()

            if row[2] != "valid":
                return error.error_prossessing_order_id()

            cursor = self.conn.execute(
                "UPDATE new_order SET available = ? and status = ? WHERE order_id = ?",
                (order_available, order_status, order_id),
            )

            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
