# -*- coding : utf-8 -*-
# coding: utf-8
from data_resource import conn


def insert_new_forestry_subject(subject_set):
    insert_sql = '''insert into new_forestry_subject (subject) value (%s)'''
    cursor = conn.cursor()
    for subject in subject_set:
        cursor.execute(insert_sql, (subject,))
        conn.commit()
        print(subject, 'insert success!')


def insert_new_relation_base_type(relation_type, data):
    cursor = conn.cursor()
    table = 'new_' + relation_type + '_relation'
    insert_sql = "insert into %s" % table + \
                 "(law_id, chapter_id, sentence_id, parse_sentence, subject, relation, object, relation_type) " \
                 "value (%s, %s, %s, %s, %s, %s, %s, %s)"

    cursor.execute(insert_sql, (data['law_id'], data['chapter_id'], data['sentence_id'], data['parse_sentence'],
                                data['subject'], data['relation'], data['object'], relation_type,))
    conn.commit()
    print(relation_type, 'insert success!')


def wash_subject():
    select_sql_1 = '''select id, subject from new_define_relation'''
    select_sql_2 = '''select id, subject from new_accord_relation'''
    select_sql_3 = '''select id, subject from new_forestry_subject'''
    update_sql_1 = '''update new_define_relation set subject = %s where id = %s'''
    update_sql_2 = '''update new_accord_relation set subject = %s where id = %s'''
    update_sql_3 = '''update new_forestry_subject set subject = %s where id = %s'''
    cursor = conn.cursor()
    cursor.execute(select_sql_3)
    results = cursor.fetchall()
    for res in results:
        id = res[0]
        subject = res[1]
        if str(subject).endswith('，') or str(subject).endswith('、'):
            subject = subject[:-1]
            cursor.execute(update_sql_3, (subject, id))
            conn.commit()
            print(id, subject, 'success')


def filter_subject():
    cursor = conn.cursor()
    select_sql = '''select * from new_forestry_subject'''
    insert_sql = '''insert into new_forestry_subject_final (subject) value (%s)'''
    cursor.execute(select_sql)
    results = cursor.fetchall()
    subject_list = []
    for res in results:
        subject = res[1]
        subject_list.append(subject)
    subject_set = list(set(subject_list))
    for s in subject_set:
        cursor.execute(insert_sql, (s,))
        conn.commit()
        print(s, 'success!')


if __name__ == '__main__':
    filter_subject()