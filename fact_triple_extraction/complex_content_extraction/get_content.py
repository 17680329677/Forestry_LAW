#!/usr/bin/env python
# coding=utf-8
from pyltp import SentenceSplitter
from data_resource import conn


def get_article_1_map_dict():        # 获取article_1中sentence、chapter与law之间的对应关系
    query_article_1_sql = '''select id, chapter_id from article_1'''
    query_chapter_sql = '''select id, law_id from chapter'''
    cursor = conn.cursor()
    cursor.execute(query_article_1_sql)
    article_results = cursor.fetchall()
    article_chapter_dict = dict()
    for res in article_results:
        article_chapter_dict.update({res[0]: res[1]})

    cursor.execute(query_chapter_sql)
    chapter_results = cursor.fetchall()
    chapter_law_dict = dict()
    for res in chapter_results:
        chapter_law_dict.update({res[0]: res[1]})
    return article_chapter_dict, chapter_law_dict


# 通过对应的dict获取chapter_id，law_id
def get_article_1_mapping(article_id, article_chapter_dict, chapter_law_dict):
    chapter_id = article_chapter_dict[article_id]
    law_id = chapter_law_dict[chapter_id]
    return chapter_id, law_id


# 获取article_1 类型的复杂句，返回形式：[(law_id, chapter_id, sentence_id, temp_list)]
def get_article_1_complex_content(article_chapter_dict, chapter_law_dict):
    select_sql = '''select * from article_1_sentence where is_single = 0 and id > 36450'''
    cursor = conn.cursor()
    cursor.execute(select_sql)
    complex_contents = cursor.fetchall()
    result = []
    for c_content in complex_contents:
        sentence_id = c_content[0]      # 获取sentence_id
        article_1_id = c_content[1]     # 获取对应article_1_id
        chapter_id, law_id = get_article_1_mapping(article_1_id, article_chapter_dict, chapter_law_dict)
        content_list = SentenceSplitter.split(str(c_content[3]).strip())
        is_valid = False
        temp_list = []
        for content in content_list:
            temp_list.append(str(content.strip()))
            if '：' in content and len(content) > 6:
                is_valid = True
        if is_valid:
            result.append(tuple((law_id, 1, chapter_id, sentence_id, temp_list, 1)))
    return result


# 获取article_2 和 law_id 对应关系的字典
def get_article_2_map_dict():
    select_article_2_sql = '''select id, law_id from article_2'''
    cursor = conn.cursor()
    cursor.execute(select_article_2_sql)
    article_law_dict = dict()
    results = cursor.fetchall()
    for res in results:
        article_law_dict.update({res[0]: res[1]})
    return article_law_dict


# 根据article_2_id获取law_id
def get_article_2_mapping(article_2_id, article_law_dict):
    law_id = article_law_dict[article_2_id]
    return law_id


def get_article_2_complex_content():
    select_sql = '''select * from article_2_sentence where is_single = 0 limit 0, 1000'''
    cursor = conn.cursor()
    cursor.execute(select_sql)
    complex_contents = cursor.fetchall()
    article_law_dict = get_article_2_map_dict()
    result = []
    for c_content in complex_contents:
        sentence_id = c_content[0]
        article_2_id = c_content[1]
        law_id = get_article_2_mapping(article_2_id, article_law_dict)
        content_list = SentenceSplitter.split(str(c_content[3]).strip())
        is_valid = False
        temp_list = []
        for content in content_list:
            temp_list.append(str(content.strip()))
            if '：' in content and len(content) > 6:
                is_valid = True
        if is_valid:
            result.append(tuple((law_id, 2, -1, sentence_id, temp_list, 1)))
    return result


if __name__ == '__main__':
    # article_chapter_dict, chapter_law_dict = get_article_1_map_dict()
    # content_list = get_article_1_complex_content(article_chapter_dict, chapter_law_dict)
    # for content in content_list:
    #     print(content)
    results = get_article_2_complex_content()
    for res in results:
        print(res)