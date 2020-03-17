# -*- coding : utf-8 -*-
# coding: utf-8
from data_resource import conn


def get_parse_sentences():
    query_for_parse_sentence = '''select * 
                                  from dependency_parsing_result 
                                  group by parse_sentence order by id'''
    SELECT_DP_SQL = '''select * 
                       from dependency_parsing_result 
                       where law_id = %s and class = %s and chapter_id = %s 
                       and sentence_id = %s 
                       and parse_sentence = %s'''
    cursor = conn.cursor()
    cursor.execute(query_for_parse_sentence)
    sentences = cursor.fetchall()
    for sentence in sentences:
        law_id = sentence[1]
        article_class = sentence[2]
        chapter_id = sentence[3]
        sentence_id = sentence[4]
        complete_sentence = sentence[5]
        parse_sentence = sentence[6]
        is_comlex = sentence[10]



if __name__ == '__main__':
    get_parse_sentences()