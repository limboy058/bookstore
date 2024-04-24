import sys
#sys.path.append('D:\\DS_bookstore\\Project_1\\bookstore')

from be.model import buyer,store,user,seller

st=store.Store()
#st.clear_tables()

b=buyer.Buyer()
u=user.User()
print(u.register('uid1','psd1'))
print(u.register('uid2','psd2'))

s=seller.Seller()
print(s.create_store('uid1','sid1'))
print(s.add_book('uid2','sid1','bid3','infos',10))

print(b.new_order('uid1','sid1',[('bid1',1)]))