#!/usr/bin/env python
# coding=utf-8
from data_resource import conn
import re

SINGLE_RELATION_CLASS = ['define', 'contain', 'duty', 'accord', 'right_and_obligations']


def entity_wash():
    cursor = conn.cursor()
    chinese_pattern = "[\\u4e00-\\u9fa5\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b]+"
    for class_type in SINGLE_RELATION_CLASS:
        table_name = class_type + '_relation'
        select_sql = 'select * from %s' % table_name
        cursor.execute(select_sql)
        results = cursor.fetchall()
        for relation in results:
            id = relation[0]
            subject = relation[4]
            object = relation[6]
            cn_pattern_res = re.search(chinese_pattern, subject, re.M | re.I)
            if cn_pattern_res and cn_pattern_res.start() > 0 and cn_pattern_res.start() < 4:
                subject = cn_pattern_res.group(0)
            if subject[-1] == '，' or subject[-1] == '。' or subject[-1] == ',':
                subject = subject[:-1]
            if object[-1] == '，' or object[-1] == '。' or object[-1] == ',':
                object = object[:-1]
            update_sql = 'update %s ' % table_name + 'set subject = %s, object = %s where id = %s'
            cursor.execute(update_sql, (subject, object, id))
            conn.commit()
            print(class_type, id, subject, object)


def query_for_subject():
    cursor = conn.cursor()
    subject_list = []
    for class_type in SINGLE_RELATION_CLASS:
        table_name = class_type + '_relation'
        query_sql = 'select * from %s' % table_name
        cursor.execute(query_sql)
        results = cursor.fetchall()
        for relation in results:
            subject = relation[4]
            subject_list.append(subject)
    subject_set = set(subject_list)
    return subject_set


def subject_save(subject_set):
    cursor = conn.cursor()
    insert_sql = '''insert into forestry_subject (subject) value (%s)'''
    for subject in subject_set:
        cursor.execute(insert_sql, (subject,))
        conn.commit()
        print(subject)
    print(len(subject_set))


def scope_of_application_process():
    select_scope_of_application = 'select * from scope_of_application'
    select_right_and_obligation = 'select * from right_and_obligations_relation'
    origin_law_list = []
    new_list = []
    cursor = conn.cursor()
    cursor.execute(select_scope_of_application)
    origin_results = cursor.fetchall()
    cursor.execute(select_right_and_obligation)
    new_results = cursor.fetchall()
    for res in origin_results:
        origin_law_list.append(res[1])
    for res in new_results:
        if '适用' in res[5]:
            new_list.append(res[1])
    origin_law_set = set(origin_law_list)
    new_set = set(new_list)
    print(len(origin_law_set), len(new_set))


def accord_relation_process():
    cursor = conn.cursor()
    select_sql = 'select * from accord_relation'
    cursor.execute(select_sql)
    results = cursor.fetchall()
    accord_list = []
    for res in results:
        relation = res[5]
        for accord in str(relation).split('/'):
            accord_list.append(accord)
    accord_set = set(accord_list)
    for accord in accord_set:
        print(accord)


if __name__ == '__main__':
    # entity_wash()
    # subject_save(query_for_subject())
    # scope_of_application_process()
    accord_relation_process()
