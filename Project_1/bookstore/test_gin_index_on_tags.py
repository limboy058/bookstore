import pymongo
import sys
sys.path.append("D:\dbproject\Project_1\\bookstore")
import uuid
import json
import logging
import time
import datetime
import pymongo.errors
import psycopg2
import random
from be.model import db_conn
from be.model import error
import pandas as pd
from io import StringIO
try:
    conn=psycopg2.connect(host="localhost",database="609A", user='mamba', password='out')
    # cur=conn.cursor()
    # cur.execute("drop table if exists test_tags")
    # cur.execute("create table test_tags(store_id int,tags text[])")
    # tagsList=list()
    # for i in range(0,3000000):
    #     tags=list()
    #     for j in range(0,3):
    #         tag=""
    #         for k in range(0,5):
    #             tag+=(chr)(97+(int)(random.random()*26))
    #         tags.append(tag)
    #     tagsList.append((i,tags))
    # print("BG!")
    # cur.executemany("insert into test_tags values(%s,%s)",tagsList)
    # conn.commit()
    # cur.close()
    # conn.close()
    # print(tagsList[12345][1])
    # conn=psycopg2.connect(host="localhost",database="609A", user='mamba', password='out')
    # cur=conn.cursor()
    # start_time=time.time()
    # cur.execute("select * from test_tags where tags @> %s",[tagsList[12345][1],])
    # end_time=time.time()
    # print(end_time-start_time)
    # res=cur.fetchall()
    # print(len(res))
    # for i in res:
    #     print(i)
    # conn.commit()

    # cur=conn.cursor()

    # cur.execute("create index array_index on test_tags using GIN (tags)")

    
    # res=cur.fetchall()
    # print(len(res))
    # for i in res:
    #     print(i)
    # conn.commit()

    cur=conn.cursor()
    cur.execute("select * from test_tags")
    tagsList=cur.fetchall()
    
    start_time=time.time()
    cur.execute("select * from test_tags where tags @> %s",[tagsList[12345][1],])
    end_time=time.time()
    print(end_time-start_time)
    for i in cur.fetchall(): 
        print(i)

    # cur.execute("drop table if exists test_tags_store")
    # cur.execute("create table test_tags_store(store_id int)")
    # cur.execute("drop table if exists test_tags_tag")
    # cur.execute("create table test_tags_tag(store_id int,tag varchar(255))")
    # cur.execute("create index normal_index on test_tags_tag (tag)")
    # new_tags_list=list()
    # for i in tagsList:
    #     new_tags_list.append(i[0])
    # data1 = pd.DataFrame(new_tags_list)
    # f = StringIO()
    # data1.to_csv(f, sep='\t', index=False, header=False)
    # f.seek(0)
    # cur.copy_from(f, 'test_tags_store', columns=('store_id',))

    # new_tags_list=list()
    # for i in tagsList:
    #     for j in i[1]:
    #         new_tags_list.append([i[0],j])
    # data1 = pd.DataFrame(new_tags_list)
    # f = StringIO()
    # data1.to_csv(f, sep='\t', index=False, header=False)
    # f.seek(0)
    # cur.copy_from(f, 'test_tags_tag', columns=('store_id','tag'))

    start_time=time.time()
    cur.execute("select test_tags_store.store_id from test_tags_tag inner join test_tags_store on test_tags_tag.store_id=test_tags_store.store_id "+
                "where test_tags_tag.tag in (%s,%s,%s) group by test_tags_store.store_id having count(1)>=3",[tagsList[12345][1][0],tagsList[12345][1][1],tagsList[12345][1][2]])
    end_time=time.time()
    for i in cur.fetchall():
        print(i)
    print(end_time-start_time)

    conn.commit()

except Exception as e:  print(str(e))