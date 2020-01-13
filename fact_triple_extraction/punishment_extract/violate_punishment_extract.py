#!/usr/bin/env python
# coding=utf-8
from data_resource import conn
import re
import string


PUNISHMENT_PATTERN_ALL = "(.*)违反(.*)[处|处以](.*)"
PUNISHMENT_PATTERN_DETAIL = r"(.*)违反(.*)第(.*)条第(.*)款规定(.*)[处|处以](.*)"
PUNISHMENT_AND_ACCORD_PATTERN = r"违反(.*)第(.*)条(.*)[依照|依据|按照]本(.*)第(.*)条"


def query_and_match(query_sql, article_type):
    cursor = conn.cursor()
    cursor.execute(query_sql)
    results_1 = cursor.fetchall()
    results_detail = []
    results_accord = []
    accord_count = 0
    detail_count = 0
    output_file = "C:\\Users\\dhz\\Desktop\\template\\punishment_content.txt"
    with open(output_file, "a") as w:
        for res in results_1:
            content = str(res[3]).strip()
            pattern_res_detail = re.search(PUNISHMENT_PATTERN_DETAIL, content, re.M | re.I)
            pattern_res_accord = re.search(PUNISHMENT_AND_ACCORD_PATTERN, content, re.M | re.I)
            if pattern_res_accord:
                accord_count = accord_count + 1
                results_accord.append(res)
            elif pattern_res_detail:
                # w.write(content.replace("\n", "") + '\n')
                detail_count = detail_count + 1
                results_detail.append(res)
    print(detail_count)
    print(accord_count)
    return results_detail, results_accord, article_type


def get_article_1_map_dict():
    article_to_chapter_dict = dict()
    chapter_to_law_dict = dict()
    query_for_article_1 = '''select id, a_key, chapter_id from article_1'''
    query_for_chapter = '''select id, law_id from chapter'''
    cursor = conn.cursor()
    cursor.execute(query_for_article_1)
    article_results = cursor.fetchall()
    for a_res in article_results:
        article_to_chapter_dict.update({a_res[0]: tuple((a_res[1], a_res[2]))})

    cursor.execute(query_for_chapter)
    chapter_results = cursor.fetchall()
    for c_res in chapter_results:
        chapter_to_law_dict.update({c_res[0]: c_res[1]})
    return article_to_chapter_dict, chapter_to_law_dict


def get_article_1_map_info(sentence_id, article_to_chapter_dict, chapter_to_law_dict):
    article_key = article_to_chapter_dict[sentence_id][0]
    chapter_id = article_to_chapter_dict[sentence_id][1]
    law_id = chapter_to_law_dict[chapter_id]
    return chapter_id, article_key, law_id


def get_article_2_map_dict():
    article_to_law_dict = dict()
    cursor = conn.cursor()
    query_for_article_2_sql = '''select id, a_key, law_id from article_2'''
    cursor.execute(query_for_article_2_sql)
    results = cursor.fetchall()
    for res in results:
        article_to_law_dict.update({res[0]: tuple((res[1], res[2]))})
    return article_to_law_dict


def get_article_2_map_info(article_2_id, article_to_law_dict):
    article_to_law_info = article_to_law_dict[article_2_id]
    punishment_article_key = article_to_law_info[0]
    punishment_law_id = article_to_law_info[1]
    return punishment_article_key, punishment_law_id


def process_and_save(contents, is_contain_accord, article_type):
    if article_type == 1:
        article_to_chapter_dict, chapter_to_law_dict = get_article_1_map_dict()
        for content in contents:
            punishment_sentence_id = content[0]
            punishment_article_id = content[1]
            punishment_chapter_id, \
            punishment_article_key, \
            punishment_law_id = get_article_1_map_info(punishment_article_id,
                                                       article_to_chapter_dict,
                                                       chapter_to_law_dict)
            sentence = content[3]
            if is_contain_accord == 1:
                pattern_accord_res = re.search(PUNISHMENT_AND_ACCORD_PATTERN,
                                               sentence.strip().replace("\n", ""),
                                               re.M | re.I)
                violate_key = '第' + pattern_accord_res.group(2) + '条'
                accord_key = '第' + pattern_accord_res.group(5) + '条'
                violate_info = find_violate_and_accord_info(1, article_type, violate_key, accord_key, punishment_law_id)
                if violate_info is None:
                    continue
                violate_info.update({'punishment_info': [
                    punishment_chapter_id,
                    punishment_article_id,
                    punishment_sentence_id,
                    sentence]})
                violate_punishment_save(1, violate_info, punishment_law_id)
            else:
                for c in str(sentence).split("。"):
                    pattern_accord_res = re.search(PUNISHMENT_PATTERN_DETAIL,
                                                   c.strip().replace("\n", ""),
                                                   re.M | re.I)
                    if pattern_accord_res:
                        violate_key = '第' + pattern_accord_res.group(3) + '条'
                        violate_info = find_violate_and_accord_info(0, article_type, violate_key, punishment_law_id)
                        if violate_info is None:
                            continue
                        violate_info.update({'punishment_info': [
                            punishment_chapter_id,
                            punishment_article_id,
                            punishment_sentence_id,
                            c]})
                        violate_punishment_save(0, violate_info, punishment_law_id)

    elif article_type == 2:
        article_to_law_dict = get_article_2_map_dict()
        for content in contents:
            punishment_sentence_id = content[0]
            punishment_article_id = content[1]
            punishment_chapter_id = -1
            punishment_article_key, punishment_law_id = get_article_2_map_info(punishment_article_id,
                                                                               article_to_law_dict)
            sentence = content[3]
            if is_contain_accord == 1:
                pattern_accord_res = re.search(PUNISHMENT_AND_ACCORD_PATTERN,
                                               sentence.strip().replace("\n", ""),
                                               re.M | re.I)
                violate_key = '第' + pattern_accord_res.group(2) + '条'
                accord_key = '第' + pattern_accord_res.group(5) + '条'
                violate_info = find_violate_and_accord_info(1, article_type, violate_key, accord_key, punishment_law_id)
                if violate_info is None:
                    continue
                violate_info.update({'punishment_info': [
                    punishment_chapter_id,
                    punishment_article_id,
                    punishment_sentence_id,
                    sentence]})
                violate_punishment_save(1, violate_info, punishment_law_id)
            else:
                for c in str(sentence).split("。"):
                    pattern_accord_res = re.search(PUNISHMENT_PATTERN_DETAIL,
                                                   c.strip().replace("\n", ""),
                                                   re.M | re.I)
                    if pattern_accord_res:
                        violate_key = '第' + pattern_accord_res.group(3) + '条'
                        violate_info = find_violate_and_accord_info(2, article_type, violate_key, punishment_law_id)
                        if violate_info is None:
                            continue
                        violate_info.update({'punishment_info': [
                            punishment_chapter_id,
                            punishment_article_id,
                            punishment_sentence_id,
                            c]})
                        violate_punishment_save(0, violate_info, punishment_law_id)


def find_violate_and_accord_info(is_contain_accord, article_type, *kwargs):
    select_chapter_list_sql = '''select id from chapter where law_id = %s'''
    cursor = conn.cursor()
    results = None
    # 1. 如果是包含依据的违法处罚办法
    if is_contain_accord == 1:
        violate_key = kwargs[0]
        accord_key = kwargs[1]
        punishment_law_id = kwargs[2]
        # 处理article_1类型的文本
        if article_type == 1:
            cursor.execute(select_chapter_list_sql, (punishment_law_id,))
            chapter_info = cursor.fetchall()
            chapter_id_list = list(map(lambda chapter_id: chapter_id[0] + 0, chapter_info))
            select_article_1_sql = '''select * from article_1 where chapter_id in %s and a_key in %s'''
            cursor.execute(select_article_1_sql, (chapter_id_list, [violate_key, accord_key]))
            article_1_results = cursor.fetchall()
            violate_info = None
            accord_info = None
            for res in article_1_results:
                if res[1] == violate_key:
                    violate_info = res
                elif res[1] == accord_key:
                    accord_info = res
            if violate_info and accord_info:
                violate_article_id = violate_info[0]
                accord_article_id = accord_info[0]
                violate_content = violate_info[2]
                accord_content = accord_info[2]
                violate_chapter_id = violate_info[3]
                accord_chapter_id = accord_info[3]
                select_article_1_sentence_sql = '''select id from article_1_sentence where article_1_id = %s'''
                cursor.execute(select_article_1_sentence_sql, (violate_article_id,))
                violate_sentence_id = cursor.fetchone()[0]
                cursor.execute(select_article_1_sentence_sql, (accord_article_id,))
                accord_sentence_id = cursor.fetchone()[0]
                results = {'violate_info': [violate_chapter_id, violate_article_id, violate_sentence_id, violate_content],
                           'accord_info': [accord_chapter_id, accord_article_id, accord_sentence_id, accord_content]}
        # 处理article_2类型的文本
        else:
            violate_info = None
            accord_info = None
            select_article_2_sql = '''select * from article_2 where law_id = %s and a_key in %s'''
            cursor.execute(select_article_2_sql, (punishment_law_id, [violate_key, accord_key]))
            article_2_results = cursor.fetchall()
            for res in article_2_results:
                if res[1] == violate_key:
                    violate_info = res
                elif res[1] == accord_key:
                    accord_info = res
            if violate_info and accord_info:
                violate_article_id = violate_info[0]
                accord_article_id = accord_info[0]
                violate_content = violate_info[2]
                accord_content = accord_info[2]
                select_article_2_sentence_sql = '''select id from article_2_sentence where article_2_id = %s'''
                cursor.execute(select_article_2_sentence_sql, (violate_article_id,))
                violate_sentence_id = cursor.fetchone()[0]
                cursor.execute(select_article_2_sentence_sql, (accord_article_id,))
                accord_sentence_id = cursor.fetchone()[0]
                results = {'violate_info': [-1, violate_article_id, violate_sentence_id, violate_content],
                           'accord_info': [-1, accord_article_id, accord_sentence_id, accord_content]}
    # 2. 如果是不包含依据的违法处罚办法
    else:
        violate_key = kwargs[0]
        punishment_law_id = kwargs[1]
        # 处理article_1类型的文本
        if article_type == 1:
            cursor.execute(select_chapter_list_sql, (punishment_law_id,))
            chapter_info = cursor.fetchall()
            chapter_id_list = list(map(lambda chapter_id: chapter_id[0] + 0, chapter_info))
            select_article_1_sql = '''select * from article_1 where chapter_id in %s and a_key = %s'''
            cursor.execute(select_article_1_sql, (chapter_id_list, violate_key,))
            violate_info = cursor.fetchone()
            if violate_info:
                violate_article_id = violate_info[0]
                violate_content = violate_info[2]
                violate_chapter_id = violate_info[3]
                select_article_1_sentence_sql = '''select id from article_1_sentence where article_1_id = %s'''
                cursor.execute(select_article_1_sentence_sql, (violate_article_id,))
                violate_sentence_id = cursor.fetchone()[0]
                results = {
                    'violate_info': [violate_chapter_id, violate_article_id, violate_sentence_id, violate_content]}
        # 处理article_2类型的文本
        else:
            violate_info = None
            select_article_2_sql = '''select * from article_2 where law_id = %s and a_key = %s'''
            cursor.execute(select_article_2_sql, (punishment_law_id, violate_key))
            violate_info = cursor.fetchone()
            if violate_info:
                violate_article_id = violate_info[0]
                violate_content = violate_info[2]
                select_article_2_sentence_sql = '''select id from article_2_sentence where article_2_id = %s'''
                cursor.execute(select_article_2_sentence_sql, (violate_article_id,))
                violate_sentence_id = cursor.fetchone()[0]
                results = {'violate_info': [-1, violate_article_id, violate_sentence_id, violate_content]}
    return results


def violate_punishment_save(is_contain_accord, violate_punishment_accord_info, law_id):
    cursor = conn.cursor()
    if is_contain_accord == 1:
        contain_accord_insert_sql = '''insert into violate_punishment_accord 
                            (violate_law_id, violate_chapter_id, violate_article_id, violate_sentence_id, 
                             punishment_law_id, punishment_chapter_id, punishment_article_id, punishment_sentence_id,
                             accord_law_id, accord_chapter_id, accord_article_id, accord_sentence_id, 
                             violate_content, punishment_content, accord_content, is_contain_accord)
                             value (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        violate_info = violate_punishment_accord_info['violate_info']
        punishment_info = violate_punishment_accord_info['punishment_info']
        accord_info = violate_punishment_accord_info['accord_info']
        try:
            cursor.execute(contain_accord_insert_sql,
                           (law_id, violate_info[0], violate_info[1], violate_info[2],
                            law_id, punishment_info[0], punishment_info[1], punishment_info[2],
                            law_id, accord_info[0], accord_info[1], accord_info[2],
                            violate_info[3], punishment_info[3], accord_info[3], int(is_contain_accord)))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(e)
    else:
        contain_accord_insert_sql = '''insert into violate_punishment_accord 
                                    (violate_law_id, violate_chapter_id, violate_article_id, violate_sentence_id, 
                                     punishment_law_id, punishment_chapter_id, punishment_article_id, punishment_sentence_id,
                                     violate_content, punishment_content, is_contain_accord)
                                     value (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        violate_info = violate_punishment_accord_info['violate_info']
        punishment_info = violate_punishment_accord_info['punishment_info']
        try:
            cursor.execute(contain_accord_insert_sql,
                           (law_id, violate_info[0], violate_info[1], violate_info[2],
                            law_id, punishment_info[0], punishment_info[1], punishment_info[2],
                            violate_info[3], punishment_info[3], int(is_contain_accord)))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(e)


if __name__ == '__main__':
    query_sql_1 = '''select * from article_1_sentence'''
    query_sql_2 = '''select * from article_2_sentence'''
    results_detail, results_accord, article_type = query_and_match(query_sql_2, 2)
    process_and_save(results_detail, 0, article_type)