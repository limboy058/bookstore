#注意:还未在表new_order上order_time处建立索引
#live_time订单有效时间默认1200,scan_interval为扫描间隔默认10  单位均为秒
#用法: 命令行输入:
# C:/Users/Limbo/AppData/Local/Programs/Python/Python311/python.exe d:/DS_bookstore/Project_1/bookstore/be/scanner.py(程序路经) 60 1
# (python路径) (程序路经) (有效时间) (扫描周期)
 
import time,datetime
import pymongo.errors
import sys
#sys.path.append('D:\\DS_bookstore\\Project_1\\bookstore')
from be.model import db_conn

if len(sys.argv)>3:
    print('error:too many arguments(should <= 3)')
    exit()

live_time=20*60
scan_interval=10

if len(sys.argv)>=2:
    live_time=int(sys.argv[1])
if len(sys.argv)>=3:
    scan_interval=int(sys.argv[2])
    

scanner=db_conn.DBConn()

while 1:
        session=scanner.client.start_session()
        session.start_transaction()
        try:
            ret=scanner.conn['new_order'].find()
            for item in ret:
                print('此订单时间为',datetime.datetime.fromtimestamp(item['order_time']),'状态为',item['status'])
            ret = scanner.conn['new_order'].update_many(
                {
                    'order_time': {
                        '$gte': int(time.time()) - live_time - scan_interval,
                        '$lt': int(time.time()) - live_time + scan_interval
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
            print('cancel success:',ret.modified_count)
        except pymongo.errors.PyMongoError as e:
            session.abort_transaction()
            session.end_session()
            print( 528, "{}".format(str(e)))
            break
        except Exception as e:
            session.abort_transaction()
            session.end_session()
            print( 530, "{}".format(str(e)))
            break
        session.commit_transaction()
        session.end_session()
        time.sleep(scan_interval)

