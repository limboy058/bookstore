import pymongo
import uuid
import json
import logging
import sys
#sys.path.append("D:/dbproject/Project_1/bookstore")
from fe.access.book import Book
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
                conditions['$or']=list()
                conditions['$or'].append({'book_info.title':{'$regex':foozytitle}})
                conditions['$or'].append({'book_info.original_title':{'$regex':foozytitle}})
            if(reqtags!=None):
                lst=list()
                for tag in reqtags:
                    lst.append({'book_info.tags':{'$regex':tag}})
                conditions['$and']=lst
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
                    conditions['book_info.pub_year']['$lte']=highest_pub_year
                else:
                    conditions['book_info.pub_year']={'$lte':highest_pub_year}
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
                sort.append((order_by_method[0],order_by_method[1]))
                if(order_by_method[0]=='price' or order_by_method[0]=='pub_year'):
                    order_by_method[0]='book_info.'+order_by_method[0]
            cursor = self.conn['store'].find(conditions,limit=page_size,skip=page_size*page_no,sort=sort)
            #cursor = self.conn['store'].find(conditions,limit=page_size,skip=page_size*page_no)#.limit(page_size).skip(page_size*page_no)
            for row in cursor:
                    # row.pop('_id')
                    # row['stock_level']=0
                    # self.conn['store'].insert_one(row)
                    row['book_info']['store_id']=row['store_id']
                    row['book_info']['stock_level']=row['stock_level']
                    #print(row['_id'])
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
        # if(len(lst)==0):
        #     lst=
        return 200,"ok",lst
# if __name__ == "__main__":
#     book=searchBook()
    # _1,_2,res=book.find_book(0,5,foozytitle='龙',
    # store_id='test_receive_order_store_id_a8bc4f08-0214-11ef-9059-d4548b9011a8',
    # reqtags=['江南','奇幻'],
    # id='6434543',
    # author='江南',
    # publisher= '长江出版社',
    # lowest_pub_year='2011',
    # highest_pub_year='2011',
    # lowest_price=2980,
    # highest_price=2980,
    # binding='平装',
    # isbn='9787549204304',
    # #having_stock=True,
    # order_by_method=['price',1]
    # )
    # _1,_2,res=book.find_book(0,5,lowest_price=5000)
    # print(len(res),_1,_2)
    # for i in res:
    #     res1=json.loads(i)
    #     print(res1['price'])