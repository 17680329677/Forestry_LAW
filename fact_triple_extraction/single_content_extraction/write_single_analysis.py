#!/usr/bin/env python
# coding=utf-8
from fact_triple_extraction.complex_content_extraction.complex_extrate import *

OUTPUT_FILE = "F:\\forestry_law_test\\article_1_single\\single.txt"
SELECT_DP_SQL = '''select * from dependency_parsing_result 
                   where parse_sentence = %s and class = %s and sentence_id = %s'''
SELECT_SDP_SQL = '''select * from semantic_dependency_result 
                    where parse_sentence = %s and class = %s and sentence_id = %s'''
SELECT_SRL_SQL = '''select * from semantic_role_label_result 
                    where parse_sentence = %s and class = %s and sentence_id = %s'''


def write_single_analysis_to_file():
    query_for_parse_sentence = '''select complete_sentence, parse_sentence, class, sentence_id 
                                  from dependency_parsing_result where is_complex = 0
                                  group by parse_sentence order by id'''
    cursor = conn.cursor()
    cursor.execute(query_for_parse_sentence)
    parse_sentences = cursor.fetchall()

    with open(OUTPUT_FILE, "a") as w:
        for parse_sentence in parse_sentences:
            w.write("原句：" + parse_sentence[0] + '\n')
            w.write("解析：" + parse_sentence[1] + '\n')
            cursor.execute(SELECT_DP_SQL, (parse_sentence[1], parse_sentence[2], parse_sentence[3]))
            dp_results = cursor.fetchall()
            cursor.execute(SELECT_SDP_SQL, (parse_sentence[1], parse_sentence[2], parse_sentence[3]))
            sdp_results = cursor.fetchall()
            cursor.execute(SELECT_SRL_SQL, (parse_sentence[1], parse_sentence[2], parse_sentence[3]))
            srl_results = decode_srl_results(cursor.fetchall())
            w.write("-----------------------------依存句法分析结果---------------------------\n")
            for dp in dp_results:
                front_word = dp[7]
                relation_name = dp[8]
                tail_word = dp[9]
                w.write("%s -----(%s)---- %s\n" % (front_word, relation_name, tail_word))
            w.write("-----------------------------语义角色标注结果---------------------------\n")
            for verb in srl_results:
                w.write(verb + "：\t")
                for role_info in srl_results[verb]:
                    w.write(role_info[0] + '-' + role_info[1] + '\t')
                w.write('\n')
            w.write("-----------------------------语义依存分析结果---------------------------\n")
            for sdp in sdp_results:
                front_word = sdp[7]
                relation_name = sdp[8]
                tail_word = sdp[9]
                w.write("%s -----(%s)---- %s\n" % (front_word, relation_name, tail_word))
            w.write("\n********************************************************************************************\n")


if __name__ == '__main__':
    write_single_analysis_to_file()