#!/usr/bin/env python
# coding=utf-8
from fact_triple_extraction.complex_content_extraction.get_content import *
from fact_triple_extraction.complex_content_extraction.complex_analysis import *


# 获取article_1中的单句
def get_article_1_single_content():
    select_sql = '''select * from article_1_sentence where is_single = 1 and id > 41816 and id < 50649'''
    cursor = conn.cursor()
    cursor.execute(select_sql)
    single_contents = cursor.fetchall()
    article_chapter_dict, chapter_law_dict = get_article_1_map_dict()
    result = []
    for s_content in single_contents:
        sentence_id = s_content[0]      # 获取sentence_id
        article_1_id = s_content[1]     # 获取article_1_id
        # 获取chapter_id, law_id
        chapter_id, law_id = get_article_1_mapping(article_1_id, article_chapter_dict, chapter_law_dict)
        temp_list = []
        is_complex = 0
        for content in list(SentenceSplitter.split(str(s_content[3]).strip())):
            if content is not None and content != '' and len(content.strip()) > 6 and len(content) < 120:
                temp_list.append(str(content).strip())
        if temp_list is not None and len(temp_list) > 0:
            result.append(tuple((law_id, 1, chapter_id, sentence_id, temp_list, is_complex)))
    return result


def get_article_2_map_dict():
    select_sql = '''select id, law_id from article_2'''
    cursor = conn.cursor()
    cursor.execute(select_sql)
    results = cursor.fetchall()
    article_2_map_dict = dict()
    for res in results:
        article_2_map_dict.update({res[0]: res[1]})
    return article_2_map_dict


# 获取article_2中的单句
def get_article_2_single_content(from_index, to_index):
    select_sql = '''select * from article_2_sentence where is_single = 1 and id > %s and id < %s'''
    cursor = conn.cursor()
    cursor.execute(select_sql, (from_index, to_index))
    single_contents = cursor.fetchall()
    article_2_map_dict = get_article_2_map_dict()
    result = []
    for s_content in single_contents:
        sentence_id = s_content[0]  # 获取sentence_id
        article_2_id = s_content[1]  # 获取article_2_id
        law_id = article_2_map_dict[article_2_id]
        temp_list = []
        is_complex = 0
        for content in list(SentenceSplitter.split(str(s_content[3]).strip())):
            if content is not None and content != '' and len(content.strip()) > 6 and len(content) < 120:
                temp_list.append(str(content).strip())
        if temp_list is not None and len(temp_list) > 0:
            result.append(tuple((law_id, 2, -1, sentence_id, temp_list, is_complex)))
    return result


# 将获取到的数据按照指定线程数分组
def single_content_group(single_contents, thread_num):
    content_group = []
    group_num = len(single_contents) // thread_num
    for index in range(thread_num):
        content_group.append([])
        if index == thread_num - 1:
            content_group[index] = single_contents[index * group_num:]
        else:
            content_group[index] = single_contents[index * group_num: (index + 1) * group_num]
    return content_group


if __name__ == '__main__':
    # single_contents = get_article_1_single_content()
    # single_content_group(single_contents, 3)
    result = get_article_2_single_content(0, 20000)
    single_content_group(result, 4)