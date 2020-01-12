#!/usr/bin/env python
# coding=utf-8
from data_resource import conn
import re, string


def query_and_match():
    select_1_sql = '''select * from article_1_sentence'''
    select_2_sql = '''select * from article_2_sentence'''
    punishment_pattern = "(.*)违反(.*)[处|处以](.*)"
    punishment_pattern_1 = r"(.*)违反(.*)第(.*)条第(.*)款规定(.*)[处|处以](.*)"
    punishment_pattern_2 = r"违反(.*)第(.*)条(.*)依照本(.*)第(.*)条"
    cursor = conn.cursor()
    cursor.execute(select_1_sql)
    results_1 = cursor.fetchall()
    # cursor.execute(select_2_sql)
    # results_2 = cursor.fetchall()
    results = []
    count = 0
    output_file = "C:\\Users\\dhz\\Desktop\\template\\punishment_content.txt"
    with open(output_file, "a") as w:
        for res in results_1:
            content = res[3]
            pattern_res = re.search(punishment_pattern_2, content, re.M | re.I)
            if pattern_res:
                count = count + 1
                results.append(res)
    return punishment_pattern_2, 1, results


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


def process_and_save(pattern, article_type, contents):
    article_to_chapter_dict, chapter_to_law_dict = get_article_1_map_dict()
    if article_type == 1:
        for content in contents:
            sentence_id = content[0]
            article_id = content[1]
            chapter_id, article_key, law_id = get_article_1_map_info(article_id,
                                                                     article_to_chapter_dict,
                                                                     chapter_to_law_dict)
            sentences = content[3].strip().split('。')
            for sentence in sentences:
                sentence = str(sentence).strip().replace("\n", "")
                pattern_res = re.search(pattern, sentence,  re.M | re.I)
                if pattern_res:
                    print(sentence)
                    for res in pattern_res.groups():
                        print(res)
        print(len(contents))
    elif article_type == 2:
        pass


if __name__ == '__main__':
    pattern, article_type, contents = query_and_match()
    process_and_save(pattern, article_type, contents)