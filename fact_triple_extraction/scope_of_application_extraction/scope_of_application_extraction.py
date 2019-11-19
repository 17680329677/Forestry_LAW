#!/usr/bin/env python
# coding=utf-8
# 抽取法律法规的适用范围
from data_resource import conn
import re
from fact_triple_extraction.aim_and_accord_extraction.xf_ltp_test import *


def get_chapter_law_mapping():      # 获取chapter和law的ID对应字典
    cursor = conn.cursor()
    select_sql = '''select id, law_id from chapter'''
    cursor.execute(select_sql)
    resutlts = cursor.fetchall()
    chapter_to_law = dict()
    for res in resutlts:
        chapter_to_law.update({res[0]: res[1]})
    return chapter_to_law


def is_cope_of_application(content):        # 判断句子内容是否是适用范围相关
    pattern_1 = "本(办法|条例|规定|法|细则)适用于(.*?)"
    pattern_2 = "(.*?)(须遵守|遵守本)(.*?)"
    pattern_3 = "本(办法|条例|规定|法|细则)的适用范围(.*?)"
    pattern_4 = "(.*?)适用本(办法|条例|规定|法|细则)"
    if re.findall(pattern_1, content):
        return True
    elif re.findall(pattern_2, content):
        return True
    elif re.findall(pattern_3, content):
        return True
    elif re.findall(pattern_4, content):
        return True
    else:
        return False


def get_article_1_sentence():           # 获取article_1 的句子
    select_sql = '''select * from article_1'''
    cursor = conn.cursor()
    cursor.execute(select_sql)
    results = cursor.fetchall()
    count = 0
    chapter_law_dict = get_chapter_law_mapping()
    article_1_list = list()
    for result in results:
        chapter_id = result[3]
        law_id = chapter_law_dict[chapter_id]
        contents = list(filter(None, str(result[2]).strip().split('\n')))
        for content in contents:
            if "：" in content:
                continue
            if is_cope_of_application(content.strip()):
                article_1_list.append(tuple((law_id, content.strip())))
                count = count + 1
    return article_1_list


def get_article_2_sentence():           # 获取article_2 中符合要求的句子
    select_sql = '''select * from article_2'''
    cursor = conn.cursor()
    cursor.execute(select_sql)
    results = cursor.fetchall()
    count = 0
    article_2_list = list()
    for result in results:
        law_id = result[3]
        contents = list(filter(None, str(result[2]).strip().split('\n')))
        for content in contents:
            if "：" in content:
                continue
            if is_cope_of_application(content.strip()):
                article_2_list.append(tuple((law_id, content.strip())))
                count = count + 1
    return article_2_list


def pattern_2_filter_process(text):     # 过滤掉按照pattern_2分割后没用部分
    invalid_words = ['必须严格', '必须自觉', '并愿意', '并严格', '都应当', '应当', '都应', '都有', '都必', '均需', '均应', '应', '均', '必']
    for word in invalid_words:
        if word in text[-4:]:
            text = str(text).replace(word, '')
        text = text[0:len(text) - 1] + re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+", "", text[-1])
        text = text.strip().replace('\n', '')
    return text


def scope_of_application_extrate(contents):
    pattern_1 = "本(办法|条例|规定|法|细则)适用于(.*?)"
    pattern_2 = "(.*?)(须遵守|遵守本)(.*?)"
    pattern_3 = "本(办法|条例|规定|法|细则)的适用范围(.*?)"
    pattern_4 = "(.*?)适用本(办法|条例|规定|法|细则)"
    output_file = "C:\\Users\\dhz1216\\Desktop\\test\\test.txt"
    cursor = conn.cursor()
    insert_sql = '''insert into scope_of_application (law_id, scope_of_application) value (%s, %s)'''
    with open(output_file, "a") as w:
        for content in contents:
            law_id = content[0]
            if re.findall(pattern_1, content[1]):
                result = re.split(pattern_1, content[1])
                if len(result[-1]) < 5:
                    continue
                main_sentence = result[-1]
            elif re.findall(pattern_2, content[1]):
                result = re.split(pattern_2, content[1])
                if len(result[1]) < 5:
                    continue
                main_sentence = pattern_2_filter_process(result[1])
            elif re.findall(pattern_3, content[1]):
                result = re.split(pattern_3, content[1])
                if len(result[-1]) < 5:
                    continue
                main_sentence = result[-1]
            elif re.findall(pattern_4, content[1]):
                result = re.split(pattern_4, content[1])
                if len(result[1]) < 5:
                    continue
                main_sentence = result[1]
            w.write(str(law_id) + '---' + main_sentence + '\n')
            try:
                cursor.execute(insert_sql, (law_id, main_sentence))
                conn.commit()
                print(law_id, '---', main_sentence, '---SUCCESS')
            except Exception as e:
                conn.rollback()
                print('\033[1;32;41m' + str(law_id) + main_sentence + e + ': ARTICLE FAILED---------' + '\033[0m')


if __name__ == '__main__':
    a1 = get_article_1_sentence()
    a2 = get_article_2_sentence()
    scope_of_application_extrate(a1)
    print('\n=======================================================================================================\n')
    scope_of_application_extrate(a2)