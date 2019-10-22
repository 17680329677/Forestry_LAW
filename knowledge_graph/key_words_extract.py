# -*- coding : utf-8 -*-
# coding: utf-8
# 抽取法律法规文本的关键词
import os
from jieba import analyse
from data.property_collect import law_parse
from data_resource import conn


def key_words_extract():        # 利用jieba的两种方式提取关键词，并做交集，更新到 law 表的 key_words 字段
    dir_path = "C:\\Users\\dhz1216\\Desktop\\wenben\\"
    cursor = conn.cursor()
    select_sql = "select id from law where text_name = %s"
    update_sql = "update law set key_words = %s where id = %s"
    for file in os.listdir(dir_path):
        with open(dir_path + file, "r", encoding='gbk', errors='ignore') as f:
            text = f.read()
            text_name = file.split('.')[0]
            cursor.execute(select_sql, (text_name))
            law = cursor.fetchone()
            if not law:
                continue
            law_id = law[0]
            textrank = analyse.textrank
            key_words_textrank = textrank(text, topK=3, withWeight=False, allowPOS=('n', 'ns', 'vn', 'v', 'nz'))
            key_words_tfidf = analyse.extract_tags(text, topK=5, withWeight=False, allowPOS=('n', 'ns', 'vn', 'v', 'nz'))
            intersection_list = list(set(key_words_textrank).intersection(set(key_words_tfidf)))
            if intersection_list:
                key_words_list = intersection_list
            else:
                key_words_list = list(set(key_words_textrank).union(set(key_words_tfidf)))
            key_words = str()
            for i in range(len(key_words_list)):
                if i == len(key_words_list) - 1:
                    key_words = key_words + key_words_list[i]
                else:
                    key_words = key_words + key_words_list[i] + ','

            try:
                cursor.execute(update_sql, (key_words, law_id))
                conn.commit()
                print(text_name + '--------UPDATE SUCCESS')
            except Exception as e:
                conn.rollback()
                print('\033[1;32;41m' + text_name + ': PARSE FAILED---------' + e + '\033[0m')


def statistic_keywords_num():       # 统计关键词的词频，为分类提供思路
    key_words_dict = dict()
    select_sql = "select key_words from law"
    cursor = conn.cursor()
    cursor.execute(select_sql)
    results = cursor.fetchall()

    for res in results:
        key_words = str(res[0]).split(',')
        for word in key_words:
            if word not in key_words_dict:
                key_words_dict.update({word: 1})
            else:
                key_words_dict.update({word: key_words_dict[word] + 1})
    key_words_dict = sorted(key_words_dict.items(), key=lambda item:item[1], reverse=True)
    for key in key_words_dict:
        print(key)


def law_classify():         # 法律法规文本归类
    dir_path = "C:\\Users\\dhz1216\\Desktop\\wenben"
    class_select_sql = "select * from law_class"        # 查找法律分类表law_class
    law_select_sql = "select id from law where text_name = %s"        # 根据文本名称查找law ID
    update_sql = "update law set type = %s where id = %s"       # 根据ID更新law表中的type信息
    insert_sql = "insert into law_to_class (law_id, class_id) value (%s, %s)"       # 插入法律和分类对照表

    cursor = conn.cursor()
    cursor.execute(class_select_sql)
    results= cursor.fetchall()
    class_id_dict = dict()          # 记录类别和id的对应关系
    class_keyword_dict = dict()          # 记录类别和关键词的对应关系
    for res in results:
        class_id_dict.update({res[1]: res[0]})
        class_keyword_dict.update({res[1]: str(res[2]).split(',')})

    for file in os.listdir(dir_path):
        text_name = file.split('.')[0]
        cursor.execute(law_select_sql, (text_name))
        law = cursor.fetchone()
        if law is None:
            continue
        law_id = law[0]
        class_type = str()
        for c in class_id_dict:
            for word in class_keyword_dict[c]:
                if word in text_name:
                    class_type = c
                    break
            if class_type is not None and class_type != '':
                break

        if class_type is None or class_type == '':
            class_type = '其他'
        class_id = class_id_dict[class_type]        # 获取所属类别的id

        try:
            cursor.execute(update_sql, (class_type, law_id))
            conn.commit()
            try:
                cursor.execute(insert_sql, (law_id, class_id))
                conn.commit()
            except Exception as e:
                conn.rollback()
                print('\033[1;32;41m' + text_name + e + ': INSERT FAILED---------' + '\033[0m')
            print(text_name + '--------success--------' + class_type)
        except Exception as e:
            conn.rollback()
            print('\033[1;32;41m' + text_name + e + ': UPDATE FAILED---------' + '\033[0m')
        print(text_name + '------------------' + class_type + str(class_id))


if __name__ == '__main__':
    # key_words_extract()       # 关键词提取
    # statistic_keywords_num()      # 统计关键词出现的次数
    law_classify()      # 类别归属
