#!/usr/bin/env python
# coding=utf-8
from data_resource import conn
import re

CURSOR = conn.cursor()


def get_article_1_map_dict():        # 获取article_1中sentence、chapter与law之间的对应关系
    query_article_1_sql = '''select id, chapter_id from article_1'''
    query_chapter_sql = '''select id, law_id from chapter'''
    CURSOR.execute(query_article_1_sql)
    article_results = CURSOR.fetchall()
    article_chapter_dict = dict()
    for res in article_results:
        article_chapter_dict.update({res[0]: res[1]})

    CURSOR.execute(query_chapter_sql)
    chapter_results = CURSOR.fetchall()
    chapter_law_dict = dict()
    for res in chapter_results:
        chapter_law_dict.update({res[0]: res[1]})
    return article_chapter_dict, chapter_law_dict


# 通过对应的dict获取chapter_id，law_id
def get_article_1_mapping(article_id, article_chapter_dict, chapter_law_dict):
    chapter_id = article_chapter_dict[article_id]
    law_id = chapter_law_dict[chapter_id]
    return chapter_id, law_id


def get_article_2_map_dict():
    select_sql = '''select id, law_id from article_2'''
    cursor = conn.cursor()
    cursor.execute(select_sql)
    results = cursor.fetchall()
    article_2_map_dict = dict()
    for res in results:
        article_2_map_dict.update({res[0]: res[1]})
    return article_2_map_dict


def get_article_1_content():
    select_sql = '''select * from article_1_sentence'''
    CURSOR.execute(select_sql)
    single_contents = CURSOR.fetchall()
    article_chapter_dict, chapter_law_dict = get_article_1_map_dict()
    result = []
    forbid_pattern = "禁止(.*)"
    for s_content in single_contents:
        sentence_id = s_content[0]  # 获取sentence_id
        article_1_id = s_content[1]  # 获取article_1_id
        is_singel = s_content[2]
        sentence_content = str(s_content[3]).strip()
        pattern_res = re.search(forbid_pattern, sentence_content, re.M | re.I)
        if pattern_res:
            chapter_id, law_id = get_article_1_mapping(article_1_id, article_chapter_dict, chapter_law_dict)
            result.append(tuple((law_id, 1, chapter_id, sentence_id, sentence_content, is_singel)))
    return result


def get_article_2_content():
    select_sql = '''select * from article_2_sentence'''
    CURSOR.execute(select_sql)
    single_contents = CURSOR.fetchall()
    article_2_map_dict = get_article_2_map_dict()
    forbid_pattern = "禁止(.*)"
    result = []
    for s_content in single_contents:
        sentence_id = s_content[0]  # 获取sentence_id
        article_2_id = s_content[1]  # 获取article_2_id
        is_singel = s_content[2]
        sentence_content = str(s_content[3]).strip()
        law_id = article_2_map_dict[article_2_id]
        pattern_res = re.search(forbid_pattern, sentence_content, re.M | re.I)
        if pattern_res:
            result.append(tuple((law_id, 2, -1, sentence_id, sentence_content, is_singel)))
    return result


def forbid_relation_extract_core(sentence_list):
    patter_1 = "(.*)内(.*)禁止(下列|以下)(.*)"
    patter_2 = "禁止(下列|以下)(.*)的行为"
    patter_3 = "禁止(.*)。"
    forbid_list_1 = []
    forbid_list_2 = []
    forbid_list_3 = []
    for sentence in sentence_list:
        law_id = sentence[0]
        article_type = sentence[1]
        chapter_id = sentence[2]
        sentence_id = sentence[3]
        content = sentence[4]
        is_single = sentence[5]
        pattern_res_1 = re.search(patter_1, content, re.M | re.I)
        pattern_res_2 = re.search(patter_2, content, re.M | re.I)
        pattern_res_3 = re.search(patter_3, content, re.M | re.I)
        if pattern_res_1:
            # print(pattern_res_1.group(1))
            if is_single == 1:
                forbid_action = content.split('\n')[1:]
                for act in forbid_action:
                    # print(act)
                    forbid_list_1.append(tuple((law_id, article_type, chapter_id, sentence_id, pattern_res_1.group(1), act)))
            else:
                if article_type == 1 or article_type == '1':
                    select_sql = '''select clause_content from article_1_clause where article_1_sentence_id = %s'''
                else:
                    select_sql = '''select clause_content from article_2_clause where article_2_sentence_id = %s'''
                CURSOR.execute(select_sql, (sentence_id,))
                forbid_action = CURSOR.fetchall()
                for act in forbid_action:
                    # print(act[0])
                    forbid_list_1.append(tuple((law_id, article_type, chapter_id, sentence_id, pattern_res_1.group(1), act[0])))
        elif pattern_res_2:
            # print("2--", pattern_res_2.group(2))
            if is_single == 1:
                forbid_action = content.split('\n')[1:]
                for act in forbid_action:
                    # print(act)
                    forbid_list_2.append(tuple((law_id, article_type, chapter_id, sentence_id, pattern_res_2.group(2), act)))
            else:
                if article_type == 1 or article_type == '1':
                    select_sql = '''select clause_content from article_1_clause where article_1_sentence_id = %s'''
                else:
                    select_sql = '''select clause_content from article_2_clause where article_2_sentence_id = %s'''
                CURSOR.execute(select_sql, (sentence_id,))
                forbid_action = CURSOR.fetchall()
                for act in forbid_action:
                    # print(act[0])
                    forbid_list_2.append(tuple((law_id, article_type, chapter_id, sentence_id, pattern_res_2.group(2), act[0])))
            pass
        elif pattern_res_3:
            # print("3--", pattern_res_3.group(1))
            forbid_list_3.append(tuple((law_id, article_type, chapter_id, sentence_id, pattern_res_3.group(1))))
    return forbid_list_1, forbid_list_2, forbid_list_3


def forbid_act_save(forbid_list_1, forbid_list_2, forbid_list_3):
    insert_sql_1 = '''insert into forbid_1 (law_id, chapter_id, sentence_id, forbid_subject, forbid_action) 
                      value (%s, %s, %s, %s, %s)'''
    insert_sql_2 = '''insert into forbid_2 (law_id, chapter_id, sentence_id, forbid_subject, forbid_action) 
                          value (%s, %s, %s, %s, %s)'''
    insert_sql_3 = '''insert into forbid_3 (law_id, chapter_id, sentence_id, forbid_action) value (%s, %s, %s, %s)'''
    for forbid_act in forbid_list_1:
        law_id = forbid_act[0]
        chapter_id = forbid_act[2]
        sentence_id = forbid_act[3]
        forbid_subject = forbid_act[4]
        forbid_action = forbid_act[5]
        CURSOR.execute(insert_sql_1, (law_id, chapter_id, sentence_id, forbid_subject, forbid_action))
        conn.commit()
        print(forbid_act)

    for forbid_act in forbid_list_2:
        law_id = forbid_act[0]
        chapter_id = forbid_act[2]
        sentence_id = forbid_act[3]
        forbid_subject = forbid_act[4]
        forbid_action = forbid_act[5]
        CURSOR.execute(insert_sql_2, (law_id, chapter_id, sentence_id, forbid_subject, forbid_action))
        conn.commit()
        print(forbid_act)

    for forbid_act in forbid_list_3:
        law_id = forbid_act[0]
        chapter_id = forbid_act[2]
        sentence_id = forbid_act[3]
        forbid_action = forbid_act[4]
        CURSOR.execute(insert_sql_3, (law_id, chapter_id, sentence_id, forbid_action))
        conn.commit()
        print(forbid_act)


def forbid_1_wash():
    select_sql = '''select * from forbid_1'''
    update_sql = '''update forbid_1 set forbid_subject = %s where id = %s'''
    CURSOR.execute(select_sql)
    results = CURSOR.fetchall()
    for res in results:
        id = res[0]
        forbid_subject = str(res[4]).strip()
        if forbid_subject.startswith('在'):
            forbid_subject = forbid_subject[1:]
        CURSOR.execute(update_sql, (forbid_subject, id))
        conn.commit()
        print(id, forbid_subject)


def update_forestry_subject():
    query_forestry_subject = '''select * from forestry_subject'''
    query_forbid_1 = '''select forbid_subject from forbid_1 group by forbid_subject'''
    insert_sql = '''insert into forestry_subject (subject) value (%s)'''
    subject_list = []
    CURSOR.execute(query_forestry_subject)
    forestry_subjects = CURSOR.fetchall()
    for subject in forestry_subjects:
        subject_list.append(subject[1])
    CURSOR.execute(query_forbid_1)
    results = CURSOR.fetchall()
    for res in results:
        if res[0] in subject_list:
            continue
        else:
            subject_list.append(res[0])
            CURSOR.execute(insert_sql, (res[0],))
            conn.commit()
            print(res[0])


def merge_forbid_action():
    select_fobid_2 = '''select law_id, chapter_id, sentence_id, forbid_subject from forbid_2 
                        GROUP BY law_id, forbid_subject, chapter_id, sentence_id'''
    select_forbid_3 = '''select law_id, chapter_id, sentence_id, forbid_action from forbid_3'''
    insert_sql = '''insert into forbid_action (law_id, chapter_id, sentence_id, forbid_action) value (%s, %s, %s, %s)'''
    CURSOR.execute(select_fobid_2)
    results_2 = CURSOR.fetchall()
    for res in results_2:
        law_id = res[0]
        chapter_id = res[1]
        sentence_id = res[2]
        forbid_action = res[3]
        CURSOR.execute(insert_sql, (law_id, chapter_id, sentence_id, forbid_action))
        conn.commit()
    CURSOR.execute(select_forbid_3)
    results_3 = CURSOR.fetchall()
    for res in results_3:
        law_id = res[0]
        chapter_id = res[1]
        sentence_id = res[2]
        forbid_action = res[3]
        CURSOR.execute(insert_sql, (law_id, chapter_id, sentence_id, forbid_action))
        conn.commit()


if __name__ == '__main__':
    # results_1 = get_article_1_content()
    # results_2 = get_article_2_content()
    # forbid_list_1, forbid_list_2, forbid_list_3 = forbid_relation_extract_core(results_2)
    # forbid_act_save(forbid_list_1, forbid_list_2, forbid_list_3)
    # forbid_1_wash()
    # update_forestry_subject()
    merge_forbid_action()