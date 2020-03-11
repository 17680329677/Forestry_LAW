# -*- coding : utf-8 -*-
# coding: utf-8
# 法律信息保存到mongo备用
import os
from pymongo import MongoClient
from data.property_collect import law_parse


conn = MongoClient('localhost', 27017)
db = conn.forestry_law
collection = db.law


def save_to_mongo(law_content):
    collection.insert_one(law_content)
    print(law_content['name'] + ': 插入成功')


if __name__ == '__main__':
    dir_path = "C:\\Users\\dhz\\Desktop\\wenben"
    for file in os.listdir(dir_path):
        law_content = law_parse(dir_path + "\\" + file)
        save_to_mongo(law_content)
    print('插入：' + collection.count_documents({}) + '条数据')
    