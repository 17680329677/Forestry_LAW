# -*- coding : utf-8 -*-
# coding: utf-8
from relation_wash.insert_new_subject import *
from data_resource import conn
import re


def get_law_name(law_id):
    select_law = '''select id, name from law where id = %s'''
    cursor = conn.cursor()
    cursor.execute(select_law, (law_id,))
    law_name = cursor.fetchone()[1]
    return law_name


def get_law_aim():
    cursor = conn.cursor()
    select_sql = '''select * from law_aim group by law_id'''
    cursor.execute(select_sql)
    aim_results = cursor.fetchall()
    aim_dict = {}
    for aim in aim_results:
        law_id = aim[1]
        aim_content = aim[2]
        aim_dict.update({law_id: aim_content})
    return aim_dict


def get_relation_by_type(relation_type):
    cursor = conn.cursor()
    select_sql = '''select * from new_relation where relation_type = %s'''
    cursor.execute(select_sql, (relation_type))
    relation_results = cursor.fetchall()

    return relation_results


def relation_wash(define_relation_list, relation_type):
    law_reg = "本(.*)所称(.*)"
    duty_reg = "(.*)的主要职责"
    head_reg = "^[一二三四五六七八九]"
    special_reg1 = "[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”《》〔〕：；！，。？、~@#￥%……&*（）]+"
    special_reg2 = "[１２３４５６７８９０．]+"
    num_reg = "^[(（]"
    update_sql = '''update new_relation set subject = %s where id = %s'''
    update_sql2 = '''update new_relation set subject = %s, relation_type = %s where id = %s'''
    cursor = conn.cursor()

    subject_list = []
    law_aim_dict = get_law_aim()
    for relation in define_relation_list:
        id = relation[0]
        law_id = relation[1]
        chapter_id = relation[2]
        sentence_id = relation[3]
        parse_sentence = relation[4]
        subject = relation[5]
        object = relation[7]

        subject = re.sub(special_reg2, '', subject)
        object = re.sub(special_reg2, '', object)
        if re.search(num_reg, subject):
            subject = subject[3:]
        if subject.startswith('、'):
            subject = subject[1:]
        if subject.endswith('，') or subject.endswith('、') or subject.endswith(',') or\
                subject.endswith('。') or subject.endswith('；') or subject.endswith('：'):
            subject = subject[:-1]

        if object.startswith('、'):
            object = object[1:]
        if object.endswith('，') or object.endswith('、') or object.endswith(',') or \
                object.endswith('。') or object.endswith('；') or object.endswith('：'):
            object = object[:-1]

        if len(subject) < 15:
            subject_list.append(subject)

        data = {
            'law_id': law_id,
            'chapter_id': chapter_id,
            'sentence_id': sentence_id,
            'parse_sentence': parse_sentence,
            'subject': subject,
            'relation': '权利/义务',
            'object': object
        }
        insert_new_relation_base_type(relation_type, data)
    subject_set = list(set(subject_list))
    insert_new_forestry_subject(subject_set)


if __name__ == '__main__':
    relation_wash(get_relation_by_type('right'), 'right')