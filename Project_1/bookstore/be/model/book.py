import pymongo
import json
import logging
import pymongo.errors
from be.model import db_conn
from be.model import error


class searchBook(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)
        self.order_by_conditions=['stock_level', 'sales', 'pub_year', 'price']
    def find_book(self, page_no, page_size,
                      foozytitle=None,
                      reqtags=None,
                      id=None,
                      isbn=None,
                      author=None,
                      lowest_price=None,
                      highest_price=None,
                      lowest_pub_year=None,
                      highest_pub_year=None,
                      store_id=None,
                      publisher=None,
                      translator=None,
                      binding=None,
                      order_by_method=None,# [stock_level, sales, pub_time, price] + [1,-1]  1 means increasingly and -1 means decreasingly
                      having_stock=None,
                      ):
        books = []
        conditions={}
        try:
            if(foozytitle!=None):
                conditions['$text']={'$search':foozytitle}
            if(reqtags!=None):
                conditions['book_info.tags']={'$all':list(reqtags)}
            if(id!=None):
                conditions['book_info.id']=str(id)
            if(isbn!=None):
                conditions['book_info.isbn']=str(isbn)
            if(author!=None):
                conditions['book_info.author']=str(author)
            if(lowest_price!=None):
                conditions['book_info.price']={'$gte':lowest_price}
            if(highest_price!=None):
                if(lowest_price!=None):
                    conditions['book_info.price']['$lte']=highest_price
                else:
                    conditions['book_info.price']={'$lte':highest_price}
            if(store_id!=None):
                conditions['store_id']=str(store_id)
            if(lowest_pub_year!=None):
                conditions['book_info.pub_year']={'$gte':lowest_pub_year}
            if(highest_pub_year!=None):
                highest_pub_year=str(int(highest_pub_year)+1)
                if(lowest_pub_year!=None):
                    conditions['book_info.pub_year']['$lt']=highest_pub_year
                else:
                    conditions['book_info.pub_year']={'$lt':highest_pub_year}
            if(publisher!=None):
                conditions['book_info.publisher']=str(publisher)
            if(translator!=None):
                conditions['book_info.translator']=str(translator)
            if(binding!=None):
                conditions['book_info.binding']=str(binding)
            if(having_stock!=None and having_stock==True):
                conditions['stock_level']={'$gt':0}
            sort=[]
            if(order_by_method!=None):
                if(order_by_method[0]not in self.order_by_conditions or (order_by_method[1] !=1 and order_by_method[1] !=-1)):
                    return 522,error.error_illegal_order_condition(str(order_by_method[0]+' '+order_by_method[1])),""
                if(order_by_method[0]=='price' or order_by_method[0]=='pub_year'):
                    order_by_method[0]='book_info.'+order_by_method[0]
                sort.append((order_by_method[0],order_by_method[1]))
            cursor = self.conn['store'].find(conditions,limit=page_size,skip=page_size*page_no,sort=sort)
            for row in cursor:
                    row['book_info']['store_id']=row['store_id']
                    row['book_info']['stock_level']=row['stock_level']
                    row['book_info']['sales']=row['sales']
                    books.append(row)
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""
        lst=list()
        for i in books:
            lst.append(json.dumps(i['book_info']))
        return 200,"ok",lst