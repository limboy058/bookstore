import pymongo
import uuid
import json
import logging
import time
import pymongo.errors
import psycopg2
import random
import pandas as pd
from io import StringIO
import threading
class Session(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        self.conn=psycopg2.connect(host="localhost",database="609A", user='mamba', password='out')
        self.conn.autocommit=True
        self.cur=conn.cursor()
        self.cur.execute("select cnt from test_isolation where id=1")
        cnt=self.cur.fetchone()[0]
        if(cnt>=5):
            self.cur.execute("update test_isolation set cnt=cnt-5 where id=1")
            #self.cur.execute("update test_isolation set cnt=cnt-5 where id=1 and cnt>=5")
        self.conn.commit()
#请首先在psql中设置以下参数：
#alter system set max_connections=1000;
#然后重启postgres服务，执行show max_connections;
#若显示最大连接数为1000则说明修改成功
#使用read-committed隔离级别时，运行本文件，将有概率使得结果为负数。因此在update时使用此类更新代码在该隔离级别下对于我们的服务来说不可接受。
try:
    conn=psycopg2.connect(host="localhost",database="609A", user='mamba', password='out')
    cur=conn.cursor()
    cur.execute("drop table if exists test_isolation")
    cur.execute("create table test_isolation (id int,cnt int,primary key(id))")
    cur.execute("insert into test_isolation values(1,300)")
    conn.commit()
    sessions=list()
    for i in range(0,100):
        ss = Session()
        sessions.append(ss)

    for ss in sessions:
        ss.start()
    for ss in sessions:
        ss.join()
    cur=conn.cursor()
    cur.execute("select cnt from test_isolation where id=1")
    sum=cur.fetchone()[0]
    #assert(sum==5*5*1000)
    print(sum)
except Exception as e:  print(str(e))