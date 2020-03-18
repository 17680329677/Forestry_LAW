# -*- coding : utf-8 -*-
# coding: utf-8
from data_resource import conn
import re


def init_relation_collection(filter_colum, key, relation_type, num):
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
        if re.search(num_reg, parse_sentence) or re.search(head_reg, parse_sentence):
            continue
        else:
            count = count + 1
            if count % num == 0:
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
    print(count)


if __name__ == '__main__':
    # 1.定义、解释
    # init_relation_collection('verb', '是', 'define')

    # 2.目标、目的
    # init_relation_collection('parse_sentence', '为了', 'aim', 32)
    # init_relation_collection('parse_sentence', '为目标', 'aim', 32)

    # 3.适用范围
    # init_relation_collection('verb', '适用', 'application_scope', 32)

    # 4.包含
    # init_relation_collection('verb', '分为', 'contain', 32)
    # init_relation_collection('verb', '包含', 'contain', 32)
    # init_relation_collection('verb', '包括', 'contain', 32)

    # 5.责任
    # init_relation_collection('parse_sentence', '应当', 'duty', 128)
    # init_relation_collection('parse_sentence', '负责', 'duty', 64)

    # 6.权利与义务 TODO：**************************************************
    init_relation_collection('parse_sentence', '有权', '', 34)
    init_relation_collection('parse_sentence', '有义务', 'right', 4)

    # 7.依据
    # init_relation_collection('verb', '按照', 'accord', 16)
    # init_relation_collection('verb', '根据', 'accord', 16)
    # init_relation_collection('verb', '依据', 'accord', 16)

    # 8.令行禁止
    # init_relation_collection('verb', '禁止', 'fobid', 64)
    # init_relation_collection('verb', '严禁', 'fobid', 16)
    # init_relation_collection('verb', '严禁', 'fobid', 16)
    # init_relation_collection('parse_sentence', '不允许', 'fobid', 16)

    # 9.违反与处罚
    # init_relation_collection('verb', '处', 'punishment', 64)
    # init_relation_collection('verb', '违反', 'punishment', 64)