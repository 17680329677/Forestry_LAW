#!/usr/bin/env python
# coding=utf-8
from fact_triple_extraction.complex_content_extraction.get_content import *
from fact_triple_extraction.complex_content_extraction.complex_analysis import *


# 获取article_1中的单句
def get_article_1_single_content():
    select_sql = '''select * from article_1_sentence where is_single = 1'''
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


# 获取article_2中的单句
def get_article_2_single_content():
    pass


if __name__ == '__main__':
    pass