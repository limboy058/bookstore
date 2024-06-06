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
def gen_name(x):
    text=""
    len=x+5
    for i in range(0,len):
        text+=chr(97+i)
    return text
try:
    conn=psycopg2.connect(host="localhost",database="609A", user='mamba', password='out')
    # cur=conn.cursor()
    # cur.execute("drop table if exists test_order_detail")
    # data=list()
    # cur.execute("create table test_order_detail(id int,store_id int,detail Text,primary key(id))")
    # for i in range (0,10000000):
    #     text=""
    #     for j in range(0,10):
    #         cnt=int(random.random()*100)
    #         text+=gen_name(j)+" "+str(cnt)+" "
    #     lst=[i,i,text]
    #     data.append(lst)
    #     if(i%10000==0):
    #         print(i/10000)
    # data1 = pd.DataFrame(data)
    # f = StringIO()
    # data1.to_csv(f, sep='\t', index=False, header=False)
    # f.seek(0)
    # cur.copy_from(f, 'test_order_detail', columns=('id','store_id','detail'))
    # conn.commit()

    # cur=conn.cursor()
    # cur.execute("drop table if exists test_order")
    # cur.execute("drop table if exists test_detail")
    # cur.execute("create table test_order(id int,store_id int,primary key(id))")
    # cur.execute("create table test_detail(id int,book_id varchar(255),count int,primary key(id,book_id))")
    # data_order=list()
    # data_detail=list()
    # for i in range (0,10000000):
    #     for j in range(0,10):
    #         cnt=int(random.random()*100)
    #         data_detail.append([i,gen_name(j),cnt])
    #         #cur.execute("insert into test_detail values(%s,%s,%s)",[i,gen_name(),cnt])
    #     data_order.append([i,i])
    #     #cur.execute("insert into test_order values(%s,%s)",[i,i])
    
    # datadetail = pd.DataFrame(data_detail)
    # dataorder=pd.DataFrame(data_order)
    # f = StringIO()
    # datadetail.to_csv(f, sep='\t', index=False, header=False)
    # f.seek(0)
    # cur.copy_from(f, 'test_detail', columns=('id','book_id','count'))
    # f = StringIO()
    # dataorder.to_csv(f, sep='\t', index=False, header=False)
    # f.seek(0)
    # cur.copy_from(f, 'test_order', columns=('id','store_id'))
    # conn.commit()

    begin_time=time.time()
    cur=conn.cursor()
    cur.execute("select * from test_order_detail where id=%s",[1234567,])
    end_time=time.time()
    print(end_time-begin_time)
    conn.commit()

    begin_time=time.time()
    cur=conn.cursor()
    cur.execute("select test_detail.book_id from test_order inner join test_detail on test_order.id=test_detail.id where test_order.id=%s",[1234567,])
    end_time=time.time()
    print(end_time-begin_time)
except Exception as e:  print(str(e))