import pymongo.errors
import psycopg2

try:
    with psycopg2.connect(host="localhost",database="609A", user='mamba', password='out') as conn:
        cur=conn.cursor()
        cur.execute("delete from store")
        for i in range(0,5000):
            cur.execute("insert into store (store_id) values(%s)",[i,])
        conn.commit()
except Exception as e:  print(str(e))