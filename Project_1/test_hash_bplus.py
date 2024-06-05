import psycopg2
import random
from io import StringIO
import pandas as pd
import time
try:
    conn=psycopg2.connect(host="localhost",database="609A", user='mamba', password='out')
    cur=conn.cursor()
    cur.execute("drop table if exists test_index")
    cur.execute("create table test_index(id int,msg varchar(255),primary key (id))")
    conn.commit()

    cur=conn.cursor()
    data=list()
    for i in range (0,10000000):
        
        cnt=int(random.random()*10000000+100)
        text=str(cnt)
        lst=[i,text]
        data.append(lst)
        
        if(i%10000==0):
            print(i/10000)
    data1 = pd.DataFrame(data)
    f = StringIO()
    data1.to_csv(f, sep='\t', index=False, header=False)
    f.seek(0)
    cur.copy_from(f, 'test_index', columns=('id','msg'))
    conn.commit()
    
    cur=conn.cursor()
    cur.execute("create index hash_idx on test_index using hash(msg)")
    cur.execute("create index b_plus_idx on test_index (msg)")
    conn.commit()
except Exception as e:  print(str(e))