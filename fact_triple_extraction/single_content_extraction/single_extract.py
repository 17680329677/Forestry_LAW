#!/usr/bin/env python
# coding=utf-8
# TODO: 简单句关系抽取（利用多线程）
from data_resource import conn
import time, threading


# 获取多线程处理关系的分组信息---将要提取关系的待分析句子分为4组
def get_thread_extract_info(from_sentence_id, thread_num):
    query_for_parse_sentence = '''select complete_sentence, parse_sentence, class, sentence_id 
                                  from dependency_parsing_result 
                                  where is_complex = 0 and sentence_id > %s group by parse_sentence order by id'''
    cursor = conn.cursor()
    cursor.execute(query_for_parse_sentence, (from_sentence_id,))
    parsing_sentences = cursor.fetchall()
    extract_count = len(parsing_sentences)      # 获取总数
    print(extract_count)
    group_num = extract_count // thread_num     # 获取每个线程要处理的信息数
    extract_group = []
    for index in range(thread_num):
        extract_group.append([])
        if index == thread_num - 1:
            extract_group[index] = parsing_sentences[index * group_num:]
        else:
            extract_group[index] = parsing_sentences[index * group_num: (index + 1) * group_num]
    return extract_group


# 关系抽取任务
def extract_task(extract_sentences):
    for sentence in extract_sentences:
        print(threading.get_ident(), '--', sentence[1])
        # TODO：查询并分析DP、SDP、SRL分析结果
        single_extract_core()


# 分析关系的核心方法
def single_extract_core(dp_info, sdp_info, srl_info):
    # TODO： 制定不同规则分析并抽取关系

    # TODO: 存储关系
    save_relation_to_db()
    pass


def save_relation_to_db():
    pass


# 将抽取任务的不同组开启不同的线程
def start_multiple_thread_to_extract(func_name, thread_num, extract_group):
    thread_pool = []
    for index in range(thread_num):
        thread_pool.append(threading.Thread(target=func_name, args=(extract_group[index],)))
    for i in range(len(thread_pool)):
        thread_pool[i].start()


if __name__ == '__main__':
    extract_group = get_thread_extract_info(0, 4)
    start_multiple_thread_to_extract(extract_task, 4, extract_group)
