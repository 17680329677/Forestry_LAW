#!/usr/bin/env python
# coding=utf-8
from data_resource import conn

SINGLE_RELATION_CLASS = ['define', 'contain', 'duty', 'accord', 'right_and_obligations']


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


if __name__ == '__main__':
    subject_save(query_for_subject())