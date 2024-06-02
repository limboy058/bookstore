#live_time订单有效时间默认1200,scan_interval为扫描间隔默认10  单位均为秒

import time, datetime
import psycopg2

import sys
sys.path.append(r'D:\DS_bookstore\Project_1\bookstore')
from be.model import db_conn


class Scanner(db_conn.DBConn):

    def __init__(self, live_time=1200, scan_interval=10):
        db_conn.DBConn.__init__(self)
        self.live_time = live_time
        self.scan_interval = scan_interval

    def keep_running(self, keep=False):
        t = 0
        
        try:
            with self.get_conn() as conn:
                while t < 10:
                    with conn.cursor() as cur:
                        conn.autocommit = False

                        cur_time = datetime.datetime.now()
                        # cur.execute('''update new_order 
                        #             set status=%s 
                        #             where status=%s and time>=%s and time <%s 
                        #             returning order_id,store_id,order_detail
                        #             ''',
                        #             ('canceled','unpaid',
                        #              cur_time-datetime.timedelta(seconds=self.live_time+self.scan_interval),
                        #              cur_time-datetime.timedelta(seconds=self.live_time-self.scan_interval),))
                        #              #cur_time,))

                        cur.execute('''
                                    insert into old_order 
                                    select order_id,store_id,buyer_id,'canceled',time,total_price,order_detail 
                                    from new_order where status=%s and time>=%s and time <%s 
                                    returning order_id,store_id,order_detail
                                    ''',
                                    ('unpaid',
                                     cur_time-datetime.timedelta(seconds=self.live_time+self.scan_interval),
                                     cur_time-datetime.timedelta(seconds=self.live_time-self.scan_interval),))
                        ret=cur.fetchall()
                        cnt=cur.rowcount

                        cur.execute('''
                                    delete from new_order where status=%s and time>=%s and time <%s 
                                    ''',
                                    ('unpaid',
                                     cur_time-datetime.timedelta(seconds=self.live_time+self.scan_interval),
                                     cur_time-datetime.timedelta(seconds=self.live_time-self.scan_interval),))

                        
                        
                        for item in ret:
                            for bc in item[2].split('\n'):
                                if bc=='':continue
                                b_c=bc.split(' ')

                                cur.execute('''
                                            update book_info 
                                            set stock_level=stock_level+%s,sales=sales-%s 
                                            where book_id=%s and store_id=%s
                                            '''
                                            ,(int(b_c[1]),int(b_c[1]),b_c[0],item[1]))

                        conn.commit()
                        yield 200, cnt
                time.sleep(self.scan_interval)
                if not keep:
                    t += 1
        except GeneratorExit as e:
            return
        except psycopg2.Error as e:
            yield 528, "{}".format(str(e))
            return
        except BaseException as e:
            yield 530, "{}".format(str(e))
            return
        
# if __name__=='__main__':
#     s=Scanner(live_time=10,scan_interval=2)
#     g = s.keep_running()

#     while(1):
#         time.sleep(1)
#         try:
#             s = next(g)
#             print(s)
#         except:
#             assert 0