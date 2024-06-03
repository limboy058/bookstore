import psycopg2
import time

conn = psycopg2.connect(host="localhost",
                        database="test",
                        user="postgres",
                        password="PS333333")
conn.autocommit=False
start_t=time.time()
cur=conn.cursor()

