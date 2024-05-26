import pymongo
from be.model.store import get_db_conn


def checkSumMoney(money):
    conn = get_db_conn()
    cursor = conn['user'].find({})
    for i in cursor:
        money -= i['balance']
    cursor = conn['new_order'].find({
        '$or': [{
            'status': 'paid_but_not_delivered'
        }, {
            'status': 'delivered_but_not_received'
        }]
    })
    for i in cursor:
        money -= i['total_price']
    assert (money == 0)
