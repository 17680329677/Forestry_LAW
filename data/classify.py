# -*- coding : utf-8 -*-
# coding: utf-8
# 法律信息保存到mongo备用
from pymongo import MongoClient


conn = MongoClient('localhost', 27017)
db = conn.forestry_law


def classify_statistic():
    collection = db.law
    classes = collection.find({}, {'_id': 0, 'classify': 1})
    class_set = set()
    for i in classes:
        class_set.add(i['classify'])
    class_set.remove('')
    return class_set


def save_to_db(class_set):
    collection = db.classify
    for i in class_set:
        collection.insert_one({'name': i})


if __name__ == '__main__':
    class_set = classify_statistic()
    save_to_db(class_set)