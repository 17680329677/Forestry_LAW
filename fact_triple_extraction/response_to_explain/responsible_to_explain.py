#!/usr/bin/env python
# coding=utf-8
from fact_triple_extraction.xunfei_graphviz import *
from fact_triple_extraction.scope_of_application_extraction.scope_of_application_extraction import get_chapter_law_mapping
from data_resource import conn
import re


def get_correlation_sentences():
    cursor = conn.cursor()
    select_article_1_sql = '''select * from article_1'''
    select_article_2_sql = '''select * from article_2'''
    cursor.execute(select_article_1_sql)
    results_1 = cursor.fetchall()
    pattern_1 = "^本(办法|条例|规定|法|细则)(.*?)由(.*?)"
    chapter_to_law_dict = get_chapter_law_mapping()
    count = 0
    sentences_list = list()
    for result in results_1:
        law_id = chapter_to_law_dict[result[3]]
        contents = list(filter(None, str(result[2]).strip().split('\n')))
        for content in contents:
            if re.findall(pattern_1, content.strip()):
                count = count + 1
                if len(content.strip()) > 150:
                    continue
                sentences_list.append(tuple((law_id, content.strip())))

    cursor.execute(select_article_2_sql)
    results_2 = cursor.fetchall()
    for result in results_2:
        law_id = result[3]
        contents = list(filter(None, str(result[2]).strip().split('\n')))
        for content in contents:
            if re.findall(pattern_1, content.strip()):
                count = count + 1
                if len(content.strip()) > 150:
                    continue
                sentences_list.append(tuple((law_id, content.strip())))
    print(count)
    return sentences_list


def srl_parser(sentences_list):
    for sentence in sentences_list:
        xunfei_nlp_srl_parser(str(sentence[1]).strip())
        print(sentence)


def responsible_to_explain_extracte_core(sentences_list):
    for index in range(len(sentences_list)):
        content = str(sentences_list[index][1]).strip()
        law_id = sentences_list[index][0]
        words_list = func_cas(word_segment(content), word_segment, content, 'word')  # 分词结果
        srl_dict_by_verb = xunfei_nlp_srl_parser(content)
        verb_index_list = list(srl_dict_by_verb.keys())
        sentence_parse_info = dict()
        for verb_index in verb_index_list:
            verv_word = words_list[verb_index]
            sentence_parse_info.update({verv_word: []})
            for srl in srl_dict_by_verb[verb_index]:
                sentence_parse_info[verv_word].append(
                    tuple((srl['type'], "".join(words_list[srl['beg']: srl['end'] + 1]))))
        # print(sentence_parse_info)
        # TODO: 抽取负责解释和执行对应法律法规的机构,并存入数据库
        explain_relation_process(law_id, sentence_parse_info, content)


def explain_relation_process(law_id, sentence_parse_info, content):
    cursor = conn.cursor()
    insert_sql = '''insert into response_to_explain (law_id, responsibility, relation, from_sentence) value (%s, %s, %s, %s)'''
    for verb in dict(sentence_parse_info).keys():
        # [('A1', '本办法'), ('A0', '由省财政厅'), ('C-A1', '解释')]
        verb_role_list = sentence_parse_info[verb]
        verb_role_dict = dict()
        for role in verb_role_list:
            if role[0] in verb_role_dict:
                verb_role_dict[role[0]].append(role[1])
            else:
                verb_role_dict.update({role[0]: []})
                verb_role_dict[role[0]].append(role[1])
        # print(verb_role_dict)
        role_list = list(verb_role_dict.keys())
        if 'A1' not in role_list and 'C-A1' not in role_list:
            continue
        elif 'A0' not in role_list or len(verb_role_dict['A0']) > 1:
            continue
        else:
            law_name = ''
            relation_name = verb
            orgnization = verb_role_dict['A0'][0]
            if 'A1' in role_list and len(verb_role_dict['A1']) == 2:
                law_name = verb_role_dict['A1'][0]
                relation_name = relation_name + verb_role_dict['A1'][1]
            elif 'A1' in role_list and len(verb_role_dict['A1']) == 1 and 'C-A1' in role_list:
                law_name = verb_role_dict['A1'][0]
                relation_name = relation_name + verb_role_dict['C-A1'][0]
            elif 'A1' in role_list and len(verb_role_dict['A1']) == 1 and 'C-A1' not in role_list:
                law_name = '本条例 | 本办法'
                relation_name = relation_name + verb_role_dict['A1'][0]
            elif 'A1' not in role_list and 'C-A1' in role_list:
                law_name = '本条例 | 本办法'
                relation_name = relation_name + verb_role_dict['C-A1'][0]
        print("【%s】(%s  ---%s-->  %s)" % (str(law_id), law_name, relation_name, orgnization))
        orgnization = str(orgnization).replace('由', '')
        try:
            cursor.execute(insert_sql, (law_id, orgnization, relation_name, content))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print('\033[1;32;41m' + law_id + ': ------------PARSE FAILED---------' + '\033[0m')


if __name__ == '__main__':
    sentences_list = get_correlation_sentences()
    responsible_to_explain_extracte_core(sentences_list)
