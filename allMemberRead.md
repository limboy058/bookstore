### 1.事务冲突异常捕捉+常数次重试（等待随机时间重试）

### 2.图片/大文本在数据库中存相对路径，在项目文件夹内建专门存图片

### 3.ER图

### 4.mongodb转sql（先不考虑1，2，5；做完4后在此基础上进行修改；图片与大文本可以先直接存数据库）

### 5.事务隔离性设置





## 上手：

1.装pg，个人版本是16.2，装高版本就可以，不需要完全一致。

2.pg内执行语句如下：

```
create user mamba with password 'out';
create database "609A" owner mamba;
select datname from pg_database;
```

第二句执行后出现609A即成功。

之后可以尝试运行一下be/model/store.py或buyer.py的main函数，检测一下是否可以执行成功
