#!/usr/bin/env python
# coding=utf-8
from relation_extract_based_collection.relation_extract import *
from data_resource import conn


def application_scope_extract():
    # 直接用之前抽取好的
    query_for_scope_of_accplication = '''select * from scope_of_application'''
    cursor = conn.cursor()
    cursor.execute(query_for_scope_of_accplication)
    application_scope = cursor.fetchall()
    for res in application_scope:
        data = {
            'law_id': res[1],
            'chapter_id': -1,
            'sentence_id': -1,
            'parse_sentence': res[3],
            'subject': res[1],
            'relation': '适用范围',
            'object': res[2],
        }
        save_relation('application_scope', data)


if __name__ == '__main__':
    application_scope_extract()
