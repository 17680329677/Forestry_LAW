#!/usr/bin/env python
# coding=utf-8
# TODO: 简单句关系抽取（利用多线程）
from data_resource import conn, pool
import time, threading


SELECT_DP_SQL = '''select * from dependency_parsing_result 
                   where parse_sentence = %s and class = %s and sentence_id = %s and is_complex = 0'''
SELECT_SDP_SQL = '''select * from semantic_dependency_result 
                    where parse_sentence = %s and class = %s and sentence_id = %s and is_complex = 0'''
SELECT_SRL_SQL = '''select * from semantic_role_label_result 
                    where parse_sentence = %s and class = %s and sentence_id = %s and is_complex = 0'''


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


def decode_srl_results(srl_results):
    srl_dict = dict()
    for srl in srl_results:
        verb = srl[7]
        if verb in srl_dict:
            srl_dict[verb].append(tuple((srl[8], srl[9])))
        else:
            srl_dict.update({verb: []})
            srl_dict[verb].append(tuple((srl[8], srl[9])))
    return srl_dict


def subject_complete(subject, dp_results):          # 利用定中关系，使用递归调用将主语补全
    last_word = subject
    index = len(dp_results) - 1
    while index >= 0:
        if dp_results[index][8] == '定中关系-ATT' and last_word == dp_results[index][7]:
            subject = dp_results[index][9] + subject
            if index - 1 >= 0 and dp_results[index - 1][8] == '定中关系-ATT' and dp_results[index][9] == dp_results[index - 1][7]:
                last_word = dp_results[index][9]
        elif dp_results[index][7] == last_word and dp_results[index][8] == '主谓关系-SBV':
            subject = dp_results[index][9] + subject
        index = index - 1
    return subject


def srl_info_extract(srl_info_list):        # 整理语义角色标注结果，将某动词的语义结果整理为字典，key为语义角色
    srl_info_dict = dict()
    for srl_info in srl_info_list:
        role_label = srl_info[0]
        role_content = srl_info[1]
        if role_label in srl_info_dict:
            srl_info_dict[role_label].append(role_content)
        else:
            srl_info_dict.update({role_label: []})
            srl_info_dict[role_label].append(role_content)
    return srl_info_dict


# 关系抽取任务
def extract_task(extract_sentences):
    pool_conn = pool.connection()
    cursor = pool_conn.cursor()
    for extract_sentence in extract_sentences:
        cursor.execute(SELECT_DP_SQL, (extract_sentence[1], extract_sentence[2], extract_sentence[3]))
        dp_results = cursor.fetchall()
        cursor.execute(SELECT_SDP_SQL, (extract_sentence[1], extract_sentence[2], extract_sentence[3]))
        sdp_results = cursor.fetchall()
        cursor.execute(SELECT_SRL_SQL, (extract_sentence[1], extract_sentence[2], extract_sentence[3]))
        srl_results = decode_srl_results(cursor.fetchall())
        # TODO：查询并分析DP、SDP、SRL分析结果
        single_extract_core(dp_results, sdp_results, srl_results)


# 分析关系的核心方法
def single_extract_core(dp_results, sdp_results, srl_results):
    # 1. 找到核心动词 以及 与 核心动词并列的动词
    core_verb = None
    coo_verb_list = []
    for dp_res in dp_results:
        if dp_res[7] == 'Root':
            core_verb = dp_res[9]
            break
    for dp_res in dp_results:
        if dp_res[8] == '并列关系-COO' and (core_verb == dp_res[7] or core_verb == dp_res[9]):
            if core_verb == dp_res[7]:
                coo_verb_list.append(dp_res[9])
            else:
                coo_verb_list.append(dp_res[7])

    # 2. 判断与核心动词之间是否存在主谓关系, 若存在，通过定中关系-ATT将主语做补全修饰
    core_subject = None  # 核心动词对应的主语，此处命名为核心主语core_subject
    for dp_res in dp_results:
        if dp_res[8] == '主谓关系-SBV' and dp_res[7] == core_verb:
            core_subject = dp_res[9]
    core_subject = subject_complete(core_subject, dp_results)  # 调用递归方式，将核心主语补全

    # 3. 结合dp 和 srl结果进行关系抽取
    relation_list = []
    if core_subject is None and len(coo_verb_list) > 0:
        # TODO: 找不到主谓关系，也就是没有核心主语，此时去寻找核心动词对应的角色标注中是否有可以充当主语的角色
        for coo_verb in coo_verb_list:
            if coo_verb in srl_results:
                coo_srl_list = srl_results[coo_verb]
                coo_srl_dict = srl_info_extract(coo_srl_list)
                if 'A0' in coo_srl_dict and 'A1' in coo_srl_dict:
                    relation_list.append(tuple((coo_srl_dict['A0'][0], coo_verb, coo_srl_dict['A1'][0])))
                elif 'TMP' in coo_srl_dict and 'A1' in coo_srl_dict:
                    relation_list.append(tuple((coo_srl_dict['TMP'][0], coo_verb, coo_srl_dict['A1'][0])))
                elif 'LOC' in coo_srl_dict and 'A1'in coo_srl_dict:
                    relation_list.append(tuple((coo_srl_dict['LOC'][0], coo_verb, coo_srl_dict['A1'][0])))
    else:
        # TODO: 找到了核心主语，从核心主语出发制定规则抽取关系
        if core_verb in srl_results:
            core_srl_list = srl_results[core_verb]
            core_srl_dict = srl_info_extract(core_srl_list)
            complete_sentence = dp_results[0][5]
            parsing_sentence = dp_results[0][6]
            # 调用核心动词及主语的关系抽取方法
            relation_list = core_single_relation_analysis(core_verb,            # 核心动词
                                                          core_srl_dict,        # 核心动词的语义角色标注信息
                                                          core_subject,         # 核心主语
                                                          parsing_sentence,     # 解析句
                                                          relation_list)        # 现有关系list
        if len(coo_verb_list) > 0:      # 分析与核心动词并列动词的语义角色包含的关系
            pass
    # TODO: 存储关系
    if relation_list is not None and len(relation_list) > 0:
        print(relation_list)
    save_relation_to_db()
    pass


def core_single_relation_analysis(core_verb, core_srl_dict, core_subject, parsing_sentence, relation_list):
    print(parsing_sentence)
    print('verb:', core_verb)
    print('subject:', core_subject)
    print('srl_info:', core_srl_dict)
    print("============================================================================================")
    return relation_list


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
