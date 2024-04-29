## 注册用户

#### URL：
POST http://$address$/auth/register

#### Request

Body:
```
{
    "user_id":"$user name$",
    "password":"$user password$"
}
```

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 用户名 | N
password | string | 登陆密码 | N

#### Response

Status Code:


码 | 描述
--- | ---
200 | 注册成功
5XX | 注册失败，用户名重复

Body:
```
{
    "message":"$error message$"
}
```
变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
message | string | 返回错误消息，成功时为"ok" | N

## 注销用户

#### URL：
POST http://$address$/auth/unregister

#### Request

Body:
```
{
    "user_id":"$user name$",
    "password":"$user password$"
}
```

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 用户名 | N
password | string | 登陆密码 | N

#### Response

Status Code:


码 | 描述
--- | ---
200 | 注销成功
401 | 注销失败，用户名不存在或密码不正确


Body:
```
{
    "message":"$error message$"
}
```
变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
message | string | 返回错误消息，成功时为"ok" | N

## 用户登录

#### URL：
POST http://$address$/auth/login

#### Request

Body:
```
{
    "user_id":"$user name$",
    "password":"$user password$",
    "terminal":"$terminal code$"
}
```

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 用户名 | N
password | string | 登陆密码 | N
terminal | string | 终端代码 | N

#### Response

Status Code:

码 | 描述
--- | ---
200 | 登录成功
401 | 登录失败，用户名或密码错误

Body:
```
{
    "message":"$error message$",
    "token":"$access token$"
}
```
变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
message | string | 返回错误消息，成功时为"ok" | N
token | string | 访问token，用户登录后每个需要授权的请求应在headers中传入这个token | 成功时不为空

#### 说明 

1.terminal标识是哪个设备登录的，不同的设备拥有不同的ID，测试时可以随机生成。 

2.token是登录后，在客户端中缓存的令牌，在用户登录时由服务端生成，用户在接下来的访问请求时不需要密码。token会定期地失效，对于不同的设备，token是不同的。token只对特定的时期特定的设备是有效的。

## 用户更改密码

#### URL：
POST http://$address$/auth/password

#### Request

Body:
```
{
    "user_id":"$user name$",
    "oldPassword":"$old password$",
    "newPassword":"$new password$"
}
```

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 用户名 | N
oldPassword | string | 旧的登陆密码 | N
newPassword | string | 新的登陆密码 | N

#### Response

Status Code:

码 | 描述
--- | ---
200 | 更改密码成功
401 | 更改密码失败

Body:
```
{
    "message":"$error message$",
}
```
变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
message | string | 返回错误消息，成功时为"ok" | N

## 用户登出

#### URL：
POST http://$address$/auth/logout

#### Request

Headers:

key | 类型 | 描述
---|---|---
token | string | 访问token

Body:
```
{
    "user_id":"$user name$"
}
```

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 用户名 | N

#### Response

Status Code:

码 | 描述
--- | ---
200 | 登出成功
401 | 登出失败，用户名或token错误

Body:
```
{
    "message":"$error message$"
}
```
变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
message | string | 返回错误消息，成功时为"ok" | N



## 搜索书本

#### URL：
POST http://$address$/auth/searchbook

#### Request

Body:
```json
{
    "page_no":"$page number(the first page is 0)$"
    "page_size":"$number of books per page$"
    "foozytitle":"$ambiguous book title(optional)$"
    "reqtags":"$tags that book must have$"
    "id":"$book id$"
    "isbn":"$book isbn$"
    "author":"$book author$"
    "lowest_price":"$book lowest price$"
    "highest_price":"$book highest price$"
    "lowest_pub_year":"$book lowest publish year$"
    "highest_pub_year":"$book lowest publish year$"
    "store_id":"$store id$"
    "publisher":"$book publisher$"
    "translator":"$book translator$"
    "binding":"$book binding$"
    "order_by_method":"$the order_by key of results$"
    "having_stock":"$whether the book is in stock$"
}
```

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
page_no | int | 页码（第一页为0） | N
page_size | int | 每个页展示书的数量 | N
foozytitle | string | 书的模糊标题 | Y
reqtags | list[string] | 书所包含的标签 | Y
id | string | 书的id | Y
isbn | string | 书的isbn号 | Y
author | string | 书的作者 | Y
lowest_price | int | 书的最低价格 | Y
highest_price | int | 书的最高价格 | Y
lowest_pub_year | string | 书的最早发布年份 | Y
hightest_pub_year | string | 书的最晚发布年份 | Y
store_id | string | 书所属的书店id | Y 
publisher | string | 书的出版商 | Y 
translator | string | 书的译者 | Y 
binding | string | 书的包装（如 精装 平装 等） | Y 
order_by_method | list(string,int) | 输出结果的排序顺序，列表中第一个元素为排序属性，可选项有：["stock_level", "sales", "pub_time", "price"]，列表中第二元素为排序方式，可选项有1(表示升序)，-1（表示降序） | Y 
having_stock | bool | 书是否有存货 | Y 

#### Response

Status Code:

码 | 描述
--- | ---
200 | 登出成功
522 | 输入的order_by_method参数不合法 
528 | mongodb出现未知错误 
530 | python运行出现未知错误 

Body:
```
{
    "message":"$error message$"
}
```
变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
message | string | 返回错误消息，成功时为"ok" | N
book_info | list[json] | 列表中每一个元素是一本书的json。一本书的json中包括：id,title,author,publisher,original_title,translator,pub_year,pages,price,binding,isbn,author_intro,book_intro,content,tags,pictures,store_id,stock_level,sales | N 





## 搜索订单详情

#### URL：

POST http://$address$/auth/search_order_detail



#### Request

Body:

```json
{
    "order_id":"order_id"
}
```

| 变量名   | 类型   | 描述   | 是否可为空 |
| -------- | ------ | ------ | ---------- |
| order_id | string | 订单号 | N          |

#### Response

Status Code:

| 码   | 描述             |
| ---- | ---------------- |
| 200  | 检索详细信息成功 |
| 5XX  | 无效参数         |
| 528  | 数据库错误       |

Body:

```json
{
    "message":"$error message$",
    "order_detail_list":"order_detail_list"
}
```

| 变量名            | 类型   | 描述                       | 是否可为空 |
| ----------------- | ------ | -------------------------- | ---------- |
| message           | string | 返回错误消息，成功时为"ok" | N          |
| order_detail_list | list   | 返回订单各项详细信息       | Yes        |
