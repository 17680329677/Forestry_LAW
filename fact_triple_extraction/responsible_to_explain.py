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
    count = 0
    for index in range(len(sentences_list)):
        if count < 10:
            content = str(sentences_list[index][1]).strip()
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
            print(sentence_parse_info)
        count = count + 1


if __name__ == '__main__':
    sentences_list = get_correlation_sentences()
    # srl_parser(sentences_list)
    responsible_to_explain_extracte_core(sentences_list)
