# -*- coding : utf-8 -*-
# coding: utf-8
from pymongo import MongoClient
import pymysql

# MongoDB连接资源
mongo_conn = MongoClient('localhost', 27017)
db = mongo_conn.forestry_law
collection = db.law

# Mysql连接资源
conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='123456',
    database='forestry_law',
    charset='utf8'
)
