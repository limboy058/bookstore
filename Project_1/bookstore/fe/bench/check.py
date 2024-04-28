import pymongo
from be.model.store import get_db_conn
def checkSumMoney(money):
    conn=get_db_conn()
    cursor=conn['user'].find({})
    for i in cursor:
        money-=i['balance']
    assert(money==0)

def checkSumMoneyForHotTest(money):
    conn=get_db_conn()
    cursor=conn['user'].find({})
    for i in cursor:
        money-=i['balance']
    cursor=conn['new_order'].find({'status':'paid_but_not_delivered'})
    for i in cursor:
        money-=i['total_price']
    assert(money==0)