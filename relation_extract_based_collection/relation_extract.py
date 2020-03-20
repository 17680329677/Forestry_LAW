#!/usr/bin/env python
# coding=utf-8
from data_resource import conn
import re

SELECT_DP_SQL = '''select * 
                       from dependency_parsing_result 
                       where law_id = %s and class = %s and chapter_id = %s 
                       and sentence_id = %s 
                       and parse_sentence = %s'''
SELECT_SRL_SQL = '''select * 
                       from semantic_role_label_result 
                       where law_id = %s and class = %s and chapter_id = %s 
                       and sentence_id = %s 
                       and parse_sentence = %s'''


# 获取指定关系类型的句子集合
def get_relation_collect(relation_type):
    cursor = conn.cursor()
    select_sql = '''select * from relation_classify where relation_type = %s'''
    cursor.execute(select_sql, (relation_type,))
    relation_collect = cursor.fetchall()
    return relation_collect


def srl_for_verb(srl_results):
    srl_dict = {}
    for res in srl_results:
        verb = res[7]
        role_label = res[8]
        content = res[9]
        if verb in srl_dict:
            srl_dict[verb].append(role_label + '-' + content)
        else:
            srl_dict.update({verb: []})
            srl_dict[verb].append(role_label + '-' + content)
    return srl_dict


def parsing_and_semantic_analysis(relation_type, relation_collect):
    cursor = conn.cursor()

    output_path = "G:\\analysis\\" + relation_type + ".txt"
    with open(output_path, "a") as w:
        for res in relation_collect:
            law_id = res[1]
            article_class = res[2]
            chapter_id = res[3]
            sentence_id = res[4]
            parse_sentence = res[6]
            relation_type = res[7]
            w.write(parse_sentence + '\n')

            cursor.execute(SELECT_SRL_SQL, (law_id, article_class, chapter_id, sentence_id, parse_sentence))
            srl_results = cursor.fetchall()
            srl_dict = srl_for_verb(srl_results)
            for verb in srl_dict:
                w.write(verb + '：')
                for role_label in srl_dict[verb]:
                    w.write(role_label + '\t')
                w.write('\n')
            w.write('\n================================================================================\n')
            cursor.execute(SELECT_DP_SQL, (law_id, article_class, chapter_id, sentence_id, parse_sentence))
            dp_results = cursor.fetchall()
            for dp in dp_results:
                w.write(dp[7] + '  --------  ' + dp[8] + '  -------  ' + dp[9] + '\n')
            w.write('\n********************************************************************************\n')


def clause_supplement(article_class, sentence_id):
    if str(article_class) == '1':
        clause_table = 'article_1_clause'
        colum_name = 'article_1_sentence_id'
    else:
        clause_table = 'article_2_clause'
        colum_name = 'article_2_sentence_id'

    clause_content = ''
    cursor = conn.cursor()
    select_clause_sql = "select * from %s " % clause_table + "where %s" % colum_name + " = %s"
    cursor.execute(select_clause_sql, (sentence_id,))
    clause_results = cursor.fetchall()
    for clause in clause_results:
        clause = str(clause[3]).replace('\n', '').strip()
        clause_content = clause_content + clause + '\n'
    return clause_content


def subject_complete(subject, dp_results):          # 利用定中关系，使用递归调用将主语补全
    last_word = subject
    index = len(dp_results) - 1
    while index >= 0:
        if dp_results[index][8] == '定中关系-ATT' and last_word == dp_results[index][7]:
            subject = dp_results[index][9] + subject
            # 右附加关系主语补全代码更新
            if index - 2 >= 0 and (dp_results[index - 1] == '右附加关系-RAD'
                                   or dp_results[index - 1] == '左附加关系-LAD'
                                   or dp_results[index - 1] == '并列关系-COO') \
                              and dp_results[index - 2] == '定中关系-ATT':
                subject = dp_results[index - 2][9] + dp_results[index - 1][9] + subject
                last_word = dp_results[index - 2][9]
                index = index - 2
                continue
            if index - 1 >= 0 and dp_results[index - 1][8] == '定中关系-ATT' and dp_results[index][9] == dp_results[index - 1][7]:
                last_word = dp_results[index][9]
        elif dp_results[index][7] == last_word and dp_results[index][8] == '主谓关系-SBV':
            subject = dp_results[index][9] + subject
        index = index - 1
    return subject


def find_core_verb(dp_results):
    core_verb = None
    for dp_res in dp_results:
        if dp_res[7] == 'Root':
            core_verb = dp_res[9]
            break
    return core_verb


def find_sbv_and_vob(verb, dp_results):
    sbv = None
    vob = None
    for dp_res in dp_results:
        if dp_res[8] == '主谓关系-SBV' and dp_res[7] == verb:
            sbv = dp_res[9]
    for dp_res in dp_results:
        if dp_res[8] == '动宾关系-VOB' and dp_res[7] == verb:
            vob = dp_res[9]
    return sbv, vob


def object_complete(object, dp_results):          # 利用定中关系，使用递归调用将主语补全
    last_word = object
    index = len(dp_results) - 1
    while index >= 0:
        if dp_results[index][8] == '定中关系-ATT' and last_word == dp_results[index][7]:
            object = dp_results[index][9] + object
            # 左右附加关系及并列附加关系主语补全代码更新
            if index - 2 >= 0 and (dp_results[index - 1] == '右附加关系-RAD'
                                   or dp_results[index - 1] == '左附加关系-LAD'
                                   or dp_results[index - 1] == '并列关系-COO') \
                              and dp_results[index - 2] == '定中关系-ATT':
                object = dp_results[index - 2][9] + dp_results[index - 1][9] + object
                last_word = dp_results[index - 2][9]
                index = index - 2
                continue
            if index - 1 >= 0 and dp_results[index - 1][8] == '定中关系-ATT' and dp_results[index][9] == dp_results[index - 1][7]:
                last_word = dp_results[index][9]
        elif dp_results[index][7] == last_word and dp_results[index][8] == '动宾关系-VOB':
            object = dp_results[index][9] + object
        index = index - 1
    return object


def save_relation(relation_type, data):
    cursor = conn.cursor()
    insert_sql = '''insert into new_relation 
                    (law_id, chapter_id, sentence_id, parse_sentence, subject, relation, object, relation_type)
                    value (%s, %s, %s, %s, %s, %s, %s, %s)'''
    cursor.execute(insert_sql, (data['law_id'], data['chapter_id'], data['sentence_id'], data['parse_sentence'],
                                data['subject'], data['relation'], data['object'], relation_type, ))
    conn.commit()
    print(relation_type, 'insert success!')


if __name__ == '__main__':
    # relation_type_list = ['define', 'aim', 'application_scope', 'contain',
    #                       'duty', 'right', 'accord', 'forbid', 'punishment']
    # for relation_type in relation_type_list:
    #     relation_collect = get_relation_collect(relation_type)
    #     parsing_and_semantic_analysis(relation_type, relation_collect)
    #     print(relation_type, 'finish')
    relation_collect = get_relation_collect('forbid')
    parsing_and_semantic_analysis('forbid', relation_collect)
    print('forbid', 'finish')