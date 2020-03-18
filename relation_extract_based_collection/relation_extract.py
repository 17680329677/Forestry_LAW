#!/usr/bin/env python
# coding=utf-8
from data_resource import conn

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


if __name__ == '__main__':
    relation_type_list = ['define', 'aim', 'application_scope', 'contain',
                          'duty', 'right', 'accord', 'forbid', 'punishment']
    for relation_type in relation_type_list:
        relation_collect = get_relation_collect(relation_type)
        parsing_and_semantic_analysis(relation_type, relation_collect)
        print(relation_type, 'finish')