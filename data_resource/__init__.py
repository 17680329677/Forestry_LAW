# -*- coding : utf-8 -*-
# coding: utf-8
from pymongo import MongoClient
import pymysql
from DBUtils.PooledDB import PooledDB

# MongoDB连接资源
mongo_conn = MongoClient('localhost', 27017)
db = mongo_conn.forestry_law
collection = db.law

# Mysql连接资源
conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='123456',
    database='forestry_law',
    charset='utf8'
)


# 数据库连接池配置
pool = PooledDB(pymysql,
                10,                  # 连接池最少连接数
                host="127.0.0.1",
                user="root",
                passwd="123456",
                db="forestry_law",
                port=3306,
                setsession=['SET AUTOCOMMIT = 1'],
                charset='utf8'
                )
