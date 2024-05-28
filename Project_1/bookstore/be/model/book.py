import pymongo
import psycopg2
import json
import logging
import pymongo.errors
from be.model import db_conn
from be.model import error


class searchBook(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)
        self.order_by_conditions = [
            'stock_level', 'sales', 'pub_year', 'price'
        ]

    def find_book(
        self,
        page_no,
        page_size,
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
        order_by_method=None,  # [stock_level, sales, pub_time, price] + [1,-1]  1 means increasingly and -1 means decreasingly
        having_stock=None,
    ):
        books = list()
        query="select * from book_info "
        conditions = " where "
        fill=list()
        try:
            if (foozytitle != None):
                conditions+=" title like %s and"
                fill.append("%"+foozytitle+"%")
            if (reqtags != None):
                conditions+= " tags @> %s and"
                fill.append(reqtags)
            if (id != None):
                conditions+=" book_id=%s and"
                fill.append(id)
            if (isbn != None):
                conditions+=" isbn=%s and"
                fill.append(isbn)
            if (author != None):
                conditions+=" author=%s and"
                fill.append(author)
            if (lowest_price != None):
                conditions+=" price>=%s and"
                fill.append(lowest_price)
            if (highest_price != None):
                conditions+=" price<=%s and"
                fill.append(highest_price)
            if (store_id != None):
                conditions+=" store_id=%s and"
                fill.append(store_id)
            if (lowest_pub_year != None):
                conditions+=" pub_year>=%s and"
                fill.append(lowest_pub_year)
            if (highest_pub_year != None):
                conditions+=" pub_year<%s and"
                fill.append(str(int(highest_pub_year)+1))
            if (publisher != None):
                conditions+=" publisher=%s and"
                fill.append(publisher)
            if (translator != None):
                conditions+=" translator=%s and"
                fill.append(translator)
            if (binding != None):
                conditions+=" binding=%s and"
                fill.append(binding)
            if (having_stock == True):
                conditions+=" stock_level>0 and"

            if(len(conditions)>7):
                conditions=conditions[:-3]
            else:
                conditions=" "
            if (order_by_method != None):
                if (order_by_method[0] not in self.order_by_conditions or
                    (order_by_method[1] != 1 and order_by_method[1] != -1)):
                    return 522, error.error_illegal_order_condition(
                        str(order_by_method[0] + ' ' + order_by_method[1])), ""
                conditions+=" order by "+"\""+order_by_method[0]+"\" "
                if(order_by_method[1]==1):
                    conditions+="asc "
                else:
                    conditions+="desc "
            
            conn=self.get_conn()
            cur=conn.cursor()
            cur.execute(query+conditions+" limit "+str(page_size)+" offset "+str(page_no*page_size),fill)
            res=cur.fetchall()
            for row in res:
                book=dict()
                book['book_id']=row[0]
                book['store_id']=row[1]
                book['price']=row[2]
                book['stock_level']=row[3]
                book['sales']=row[4]
                book['title']=row[5]
                book['author']=row[6]
                book['tags']=row[7]

                book['publisher']=row[8]
                book['original_title']=row[9]
                book['translator']=row[10]
                book['pub_year']=row[11]
                book['pages']=row[12]
                book['currency_unit']=row[13]
                book['binding']=row[14]
                book['isbn']=row[15]
                book['author_intro']=row[16]
                book['book_intro']=row[17]
                book['content']=row[18]
                book['picture']=row[19]
                books.append(json.dumps(book))
        except psycopg2.Error as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""
        
        return 200, "ok", books