import sys
import time
sys.path.append(r'D:\DS_bookstore\Project_1\bookstore')

import pymongo,psycopg2

client = pymongo.MongoClient()
m_conn = client['609']

p_conn=psycopg2.connect(
            host="localhost",
            database="609A",
            user="mamba",
            password="out"
        )



#图片存储mongodb时,初始化表结构
m_conn['img'].delete_many({})
m_conn['img'].create_index({'bid': 1})
cur=p_conn.cursor()
cur.execute('''
            drop table if exists test_img_1;
            ''')
cur.execute('''
create TABLE test_img_1 (  
"bid" varchar(255) NOT NULL,
"info" varchar(255),
PRIMARY KEY ("bid")
);
''')
p_conn.commit()
with open(r'D:\DS_bookstore\Project_1\bookstore\be\data\img\0.png', 'rb') as f:
    image_data = f.read()
    cur=p_conn.cursor()
    beg=time.time()
    for id in range(0,10000):
        cur.execute('insert into test_img_1 values(%s,%s)',(str(id),'1234567890'*20,))
        m_conn['img'].insert_one({'bid':str(id),'pic':image_data})
    p_conn.commit()
    end=time.time()
    print('图片存储mongodb时,插入10000本书耗时:',end-beg)




#图片存储pg时,初始化表结构
cur=p_conn.cursor()
cur.execute('''
            drop table if exists test_img_2;
            ''')
cur.execute('''
create TABLE test_img_2 (  
"bid" varchar(255) NOT NULL,
"info" varchar(255),
"pic" TEXT,
PRIMARY KEY ("bid")
);
''')
p_conn.commit()

with open(r'D:\DS_bookstore\Project_1\bookstore\be\data\img\0.png', 'rb') as f:
    image_data = f.read()
    beg=time.time()
    cur=p_conn.cursor()
    for id in range(0,10000):
        cur.execute('insert into test_img_2 values(%s,%s,%s)',(str(id),'1234567890'*20,image_data,))
    p_conn.commit()
    end=time.time()
    print('图片存储pg时,插入10000本书耗时:',end-beg)



#图片存储本地时,初始化表结构
cur=p_conn.cursor()
cur.execute('''
            drop table if exists test_img_3;
            ''')
cur.execute('''
create TABLE test_img_3 (  
"bid" varchar(255) NOT NULL,
"info" varchar(255),
PRIMARY KEY ("bid")
);
''')
p_conn.commit()

with open(r'D:\DS_bookstore\Project_1\bookstore\be\data\img\0.png', 'rb') as f:
    image_data = f.read()
    beg=time.time()
    cur=p_conn.cursor()
    for id in range(0,10000):
        cur.execute('insert into test_img_3 values(%s,%s)',(str(id),'1234567890'*20,))
        with open('D:\\tmp\\'+str(id)+'.png', 'wb') as destination_file:
            destination_file.write(image_data)
            
    p_conn.commit()
    end=time.time()
    print('图片存储本地时,插入10000本书耗时:',end-beg)




beg=time.time()

for id in range(9999,-1,-1):
    ret=cur.execute('select * from test_img_1 where bid=%s',(str(id),))
    ret=cur.fetchone()
    ret=m_conn['img'].find_one({'bid':str(id)})
end=time.time()
print('图片存储mongodb时,读取10000本书耗时:',end-beg)



beg=time.time()
cur=p_conn.cursor()
for id in range(9999,-1,-1):
    cur.execute('select * from test_img_2 where bid=%s',(str(id),))
    ret=cur.fetchone()
end=time.time()
print('图片存储pg时,读取10000本书耗时:',end-beg)




beg=time.time()
cur=p_conn.cursor()
for id in range(9999,-1,-1):
    ret=cur.execute('select * from test_img_3 where bid=%s',(str(id),))
    ret=cur.fetchone()
    with open('D:\\tmp\\'+str(id)+'.png', 'rb') as f:
        image_data = f.read()
end=time.time()
print('图片存储本地时,读取10000本书耗时:',end-beg)
