import pymongo
import uuid
import json
import logging
import sys
sys.path.append("D:/dbproject/Project_1/bookstore")
from fe.access.book import Book
import pymongo.errors
from be.model import db_conn
from be.model import error


class searchBook(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)
    def find_book(self, user_id: str, password: str, order_id: str) -> (int, str):
        conn = self.conn
        session=self.client.start_session()
        session.start_transaction()
        try:
            pass
        except BaseException as e:
            return 530, "{}".format(str(e))
        session.commit_transaction()
        session.end_session()
        return 200, "ok"
    
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
                      store_id=None
                      ):
        books = []
        conditions={}
        try:
            if(foozytitle!=None):
                conditions['book_info.title']={'$regex':foozytitle}
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
                conditions['book_info.author']={'$regex':author}
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
            cursor = self.conn['store'].find(conditions).limit(page_size).skip(page_size*page_no)
            empty_judge=True
            for row in cursor:
                    empty_judge=False
                    #row['book_info']=json.dumps(row['book_info'])
                    row['book_info']['store_id']=row['store_id']
                    row['book_info']['stock_level']=row['stock_level']
                    books.append(row)
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""
        # result_books={}
        # for i in range(0,len(books)):
        #     result_books[i]=json.dumps(books[i])
        lst=list()
        for i in books:
            lst.append(json.dumps(i['book_info']))
        return 200,"ok",lst
# if __name__ == "__main__":
#     book=searchBook()
#     _,_,res=book.find_book(0,5,foozytitle='生死')
#     lst=list()
#     for i in res:
#         #print(i['pub_year'])
#         res1=json.dumps(i['book_info'])
#         lst.append(res1)
#     res=json.dumps(lst)
#     print(res)