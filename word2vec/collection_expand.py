# -*- coding : utf-8 -*-
# coding: utf-8
from gensim.models import Word2Vec
from data_resource import conn
import re

SELECT_DP_SQL = '''select * 
                       from dependency_parsing_result 
                       where law_id = %s and class = %s and chapter_id = %s 
                       and sentence_id = %s 
                       and parse_sentence = %s'''


def get_relation_collection():
    cursor = conn.cursor()
    query_for_relation_classify = '''select * from relation_classify'''
    cursor.execute(query_for_relation_classify)
    relation_classify_results = cursor.fetchall()
    relation_classify_dict = {'define': [], 'aim': [], 'application_scope': [],
                              'contain': [], 'duty': [], 'right': [],
                              'accord': [], 'forbid': [], 'punishment': []}
    for res in relation_classify_results:
        law_id = res[1]
        article_class = res[2]
        chapter_id = res[3]
        sentence_id = res[4]
        parse_sentence = res[6]
        relation_type = res[7]
        relation_classify_dict[relation_type].append(tuple((law_id, article_class, chapter_id,
                                                            sentence_id, parse_sentence, relation_type)))
    return relation_classify_dict


relation_classify_dict = get_relation_collection()
print('--开始加载模型--')
# model = Word2Vec.load('../model/forestry_law.model')
model = ''
print('--模型加载完毕--')


def get_parse_sentences():
    query_for_parse_sentence = '''select * 
                                  from dependency_parsing_result 
                                  group by parse_sentence order by id'''

    cn_reg = '^[\u4e00-\u9fa5]+$'
    cursor = conn.cursor()
    print('**开始获取数据集**')
    cursor.execute(query_for_parse_sentence)
    sentences = cursor.fetchall()
    print('**数据集获取完毕**')
    for sentence in sentences:
        law_id = sentence[1]
        article_class = sentence[2]
        chapter_id = sentence[3]
        sentence_id = sentence[4]
        complete_sentence = sentence[5]
        parse_sentence = sentence[6]
        is_comlex = sentence[10]
        cursor.execute(SELECT_DP_SQL, (law_id, article_class, chapter_id, sentence_id, parse_sentence))
        res1 = cursor.fetchall()
        group1 = []
        for res in res1:
            front_word = res[7]
            relation = res[8]
            tail_word = res[9]
            if re.search(cn_reg, front_word) and re.search(cn_reg, tail_word):
                group1.append(tuple((front_word, relation, tail_word)))
            else:
                continue
        print('开始计算：', parse_sentence)
        relation_type, sim_sentence = sim_calculate(model, relation_classify_dict, group1, parse_sentence)
        print(parse_sentence, '--------', relation_type, sim_sentence)


def get_group2(sentence2):
    cursor = conn.cursor()
    cn_reg = '^[\u4e00-\u9fa5]+$'

    law_id = sentence2[0]
    article_class = sentence2[1]
    chapter_id = sentence2[2]
    sentence_id = sentence2[3]
    parse_sentence = sentence2[4]
    cursor.execute(SELECT_DP_SQL, (law_id, article_class, chapter_id, sentence_id, parse_sentence))
    res2 = cursor.fetchall()
    group2 = []
    for res in res2:
        front_word = res[7]
        relation = res[8]
        tail_word = res[9]
        if re.search(cn_reg, front_word) and re.search(cn_reg, tail_word):
            group2.append(tuple((front_word, relation, tail_word)))
        else:
            continue
    return group2


def sim_calculate(model, relation_classify_dict, group1, sentence1):
    sim_dict = {}
    for relation_type in relation_classify_dict:
        num_account = 0
        sim_sentence = 0
        for sentence2 in relation_classify_dict[relation_type]:
            parse_sentence = sentence2[4]
            group2 = get_group2(sentence2)
            max_len = max(len(group1), len(group2))

            sim_score = 0
            for pair1 in group1:
                for pair2 in group2:
                    if pair1[1] == pair2[1]:
                        if pair1[0] in model and pair1[2] in model and pair2[0] in model and pair2[2] in model:
                            sim1 = model.similarity(pair1[0], pair2[0])
                            sim2 = model.similarity(pair1[2], pair2[2])
                            if sim1 > 0.35 and sim2 > 0.35:
                                sim_score = sim_score + 0.7 * ((sim1 + sim2) / 2) / max_len
            if sim_score < 0.2:
                num_account = num_account + 1
            sim_sentence = sim_sentence + sim_score
        if num_account >= 10:
            sim_dict.update({relation_type: 0})
            continue
        sim_dict.update({relation_type: sim_sentence / len(relation_classify_dict[relation_type])})
        # if sim_sentence / len(relation_classify_dict[relation_type]) > 0.6:
        #     return relation_type, (sim_sentence / len(relation_classify_dict[relation_type]))
    d_order = sorted(sim_dict.items(), key=lambda x: x[1], reverse=True)
    print(d_order)
    return 'miss', 0


def relation_collection_expand(filter_colum, key, relation_type):
    cursor = conn.cursor()
    key_word = '%' + key + '%'
    select_srl_results = "select * from semantic_role_label_result where %s" % filter_colum \
                         + " like %s and parse_sentence not like %s group by parse_sentence"

    insert_relation_classify = '''insert into relation_classify 
    (law_id, class, chapter_id, sentence_id, complete_sentence, parse_sentence, relation_type, is_complex)
    value (%s, %s, %s, %s, %s, %s, %s, %s)'''

    num_reg = '[0-9]+'
    head_reg = '^[一二三四五六七八（１２３４５６７８９０]'
    count = 0
    cursor.execute(select_srl_results, ('%' + key + '%', '%所有权%'))
    define_resutlts = cursor.fetchall()
    for res in define_resutlts:
        parse_sentence = str(res[6]).strip()
        count = count + 1

        law_id = res[1]
        article_class = res[2]
        chapter_id = res[3]
        sentence_id = res[4]
        complete_sentence = res[5]
        is_comlex = res[10]
        cursor.execute(insert_relation_classify, (law_id, article_class, chapter_id, sentence_id,
                                                  complete_sentence, parse_sentence, relation_type, is_comlex))
        conn.commit()
        print(relation_type, ' insert success')
        # print(parse_sentence)
    print(relation_type, count)
    return count


if __name__ == '__main__':
    # get_parse_sentences()
    count = 0
    # 1.定义、解释
    # count = count + relation_collection_expand('verb', '是', 'define')
    # count = count + relation_collection_expand('verb', '指', 'define')

    # 2.目标、目的
    # count = count + relation_collection_expand('parse_sentence', '为了', 'aim')
    # count = count + relation_collection_expand('parse_sentence', '为目标', 'aim')
    # count = count + relation_collection_expand('parse_sentence', '目标为', 'aim')
    # count = count + relation_collection_expand('parse_sentence', '目标是', 'aim')

    # 3.适用范围
    # count = count + relation_collection_expand('parse_sentence', '适用', 'application_scope')

    # 4.包含
    # count = count + relation_collection_expand('parse_sentence', '分为', 'contain')
    # count = count + relation_collection_expand('parse_sentence', '包括', 'contain')

    # 5.责任
    # count = count + relation_collection_expand('parse_sentence', '应当', 'duty')
    # count = count + relation_collection_expand('parse_sentence', '负责', 'duty')

    # 6.权利与义务 TODO：**************************************************
    # count = count + relation_collection_expand('parse_sentence', '有权', 'right')
    # count = count + relation_collection_expand('parse_sentence', '有义务', 'right')

    # 7.依据
    # count = count + relation_collection_expand('parse_sentence', '按照', 'accord')
    # count = count + relation_collection_expand('parse_sentence', '根据', 'accord')
    # count = count + relation_collection_expand('parse_sentence', '依据', 'accord')

    # 8.令行禁止
    count = count + relation_collection_expand('parse_sentence', '禁止', 'forbid')
    count = count + relation_collection_expand('parse_sentence', '严禁', 'forbid')
    count = count + relation_collection_expand('parse_sentence', '不得', 'forbid')
    count = count + relation_collection_expand('parse_sentence', '不允许', 'forbid')

    # 9.违反与处罚
    # count = count + relation_collection_expand('verb', '处', 'punishment')
    # count = count + relation_collection_expand('verb', '违反', 'punishment')
    # print(count)