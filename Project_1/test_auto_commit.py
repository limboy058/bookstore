import pymongo.errors
import psycopg2

try:
    with psycopg2.connect(host="localhost",database="609A", user='mamba', password='out') as conn:
        cur=conn.cursor()
        cur.execute("create table test_auto_commit (id int)")
        assert(0)
except Exception as e:  print(str(e))