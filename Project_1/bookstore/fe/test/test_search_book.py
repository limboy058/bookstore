import time
import sys
import json
#sys.path.append("D:/dbproject/Project_1/bookstore")
import pytest
import random
from fe.access.auth import Auth
from fe import conf
import pytest
from fe.access import seller
from fe import conf
from fe.access.new_seller import register_new_seller
from fe.access import book
import uuid


class TestSearchBook:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):

        self.seller_id = "test_add_books_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_add_books_store_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.seller = register_new_seller(self.seller_id, self.password)
        self.auth=Auth(conf.URL)
        code = self.seller.create_store(self.store_id)
        assert code == 200

        book_db = book.BookDB(conf.Use_Large_DB)
        self.books = book_db.get_book_info(0, 10)
        

    def test_search_book(self):
        cnt=0
        for b in self.books:
            code = self.seller.add_book(self.store_id,cnt, b)
            assert code == 200
            cnt+=1

        
        for b in self.books:

            #test id
            book_id=b.id
            code,lst = self.auth.searchbook(page_no=0,page_size=10,id=book_id)
            assert code==200
            assert(len(lst)>0)
            for i in lst:
                res=json.loads(i)
                tmp_judge=False
                assert(res['id']==book_id)

            
            #test title
            chartitle=b.title[int(random.random()*len(b.title))]
            foozytitle=str(chartitle)
            
            code,lst = self.auth.searchbook(page_no=0,page_size=10,foozytitle=foozytitle)
            assert code==200
            assert(len(lst)>0)
            for i in lst:
                res=json.loads(i)
                tmp_judge=False
                for j in (res['title']):
                    if(j==chartitle):
                        tmp_judge=True
                        break
                if(res['original_title']!=None):
                    for j in (res['original_title']):
                        if(j==chartitle):
                            tmp_judge=True
                            break
                assert(tmp_judge)

            #test author
            author=b.author
            code,lst = self.auth.searchbook(page_no=0,page_size=10,author=author)
            assert code==200
            assert(len(lst)>0)
            for i in lst:
                res=json.loads(i)
                assert(res['author']==author)
            
            #test tags
            reqtags=list(b.tags)
            while(len(reqtags)>2):
                reqtags.pop()
            code,lst = self.auth.searchbook(page_no=0,page_size=10,reqtags=reqtags)
            assert code==200
            assert(len(lst)>0)
            for i in lst:
                res=json.loads(i)
                tmp_judge=False
                tags_copy=reqtags.copy()
                for j in res['tags']:
                    if(j in tags_copy):
                        tags_copy.remove(j)
                assert(len(tags_copy)==0)

            #test isbn
            isbn=b.isbn
            code,lst = self.auth.searchbook(page_no=0,page_size=10,isbn=isbn)
            assert code==200
            assert(len(lst)>0)
            for i in lst:
                res=json.loads(i)
                assert(res['isbn']==isbn)
            
            #test price
            lowest_price=b.price
            code,lst = self.auth.searchbook(page_no=0,page_size=10,lowest_price=lowest_price)
            assert code==200
            assert(len(lst)>0)
            for i in lst:
                res=json.loads(i)
                assert(res['price']>=lowest_price)

            highest_price=b.price
            code,lst = self.auth.searchbook(page_no=0,page_size=10,highest_price=highest_price)
            assert code==200
            assert(len(lst)>0)
            for i in lst:
                res=json.loads(i)
                assert(res['price']<=highest_price)

            #test pub year
            lowest_year=b.pub_year[0:4]
            code,lst = self.auth.searchbook(page_no=0,page_size=10,lowest_pub_year=lowest_year)
            assert code==200
            assert(len(lst)>0)
            for i in lst:
                res=json.loads(i)
                assert(res['pub_year'][0:4]>=lowest_year)

            highest_year=b.pub_year[0:4]
            code,lst = self.auth.searchbook(page_no=0,page_size=10,highest_pub_year=highest_year)
            assert code==200
            assert(len(lst)>0)
            for i in lst:
                res=json.loads(i)
                assert(res['pub_year'][0:4]<=highest_year)

            
            #test store_id
            code,lst = self.auth.searchbook(page_no=0,page_size=10,store_id=self.store_id)
            assert code==200
            assert(len(lst)>0)
            for i in lst:
                res=json.loads(i)
                assert(res['store_id']==self.store_id)

            
            #test publisher
            publisher=b.publisher
            if(publisher is not None):
                code,lst = self.auth.searchbook(page_no=0,page_size=10,publisher=publisher)
                assert code==200
                assert(len(lst)>0)
                for i in lst:
                    res=json.loads(i)
                    assert(res['publisher']==publisher)


            
            #test translator
            translator=b.translator
            if(translator is not None):
                code,lst = self.auth.searchbook(page_no=0,page_size=10,translator=translator)
                assert code==200
                assert(len(lst)>0)
                for i in lst:
                    res=json.loads(i)
                    assert(res['translator']==translator)

            #test binding
            binding=b.binding
            if(binding is not None):
                code,lst = self.auth.searchbook(page_no=0,page_size=10,binding=binding)
                assert code==200
                assert(len(lst)>0)
                for i in lst:
                    res=json.loads(i)
                    assert(res['binding']==binding)

            #test having_stock
            code,lst = self.auth.searchbook(page_no=0,page_size=10,having_stock=True,store_id=self.store_id)
            assert code==200
            assert(len(lst)==9)

            #test non exist store
            tmp_store_id=str(uuid.uuid1())+"1"
            code,lst = self.auth.searchbook(page_no=0,page_size=10,store_id=tmp_store_id)
            assert code==200
            assert(len(lst)==0)

            #test order
            code,lst = self.auth.searchbook(page_no=0,page_size=10,order_by_method=['stock_level',1])
            assert code==200
            assert(len(lst)==10)
            las_stock_level=0
            for i in lst:
                    res=json.loads(i)
                    assert(res['stock_level']>=las_stock_level)
                    las_stock_level=res['stock_level']

# if __name__ == "__main__":
#     tmp=TestSearchBook()
#     tmp.pre_run_initialization()
#     tmp.test_search_book()
