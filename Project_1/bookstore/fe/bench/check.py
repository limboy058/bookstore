import psycopg2
from be.model.store import get_db_conn


def checkSumMoney(money):
    conn = get_db_conn()
    cur=conn.cursor()
    cur.execute("select sum(balance) from \"user\" ")
    res=cur.fetchone()
    if(res is not None and res[0] is not None):
        money-=res[0]
    cur.execute("select sum(total_price) from new_order where status='paid_but_not_delivered' or status='delivered_but_not_received'")
    res=cur.fetchone()
    if(res is not None and res[0] is not None):
        money-=res[0]
    assert (money == 0)
