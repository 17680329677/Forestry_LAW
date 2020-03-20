#!/usr/bin/env python
# coding=utf-8
from relation_extract_based_collection.relation_extract import *
from data_resource import conn
import re


def aim_wash(aim):
    if str(aim).startswith('为了'):
        aim = aim[2:]
    elif str(aim).startswith('以'):
        aim = aim[1:]

    if str(aim).endswith('，'):
        aim = aim[:-1]
    return aim


def aim_relation_extract(accord_relation_collect, relation_type):
    cursor = conn.cursor()
    special_reg = "[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”《》〔〕：；！，。？、~@#￥%……&*（）]+"
    head_reg = "^[一二三四五六七八（１２３４５６７８９０]1234567890"
    aim_reg = "以(.*)为目标"
    collect_num = len(accord_relation_collect)
    extract_num = 0
    complex_num = 0
    output_path = "G:\\analysis\\relation\\" + relation_type + ".txt"
    with open(output_path, "w") as w:
        for res in accord_relation_collect:
            law_id = res[1]
            article_class = res[2]
            chapter_id = res[3]
            sentence_id = res[4]
            parse_sentence = res[6]
            relation_type = res[7]
            is_complex = res[8]
            # 如果是复杂句 则略过不处理
            if str(is_complex) == '1':
                continue
            # 获取语义角色标注信息
            cursor.execute(SELECT_SRL_SQL, (law_id, article_class, chapter_id, sentence_id, parse_sentence))
            srl_results = cursor.fetchall()
            srl_dict = srl_for_verb(srl_results)
            verb_srl_dict = {}
            for verb in srl_dict:
                verb_srl_dict.update({verb: {}})
                for srl in srl_dict[verb]:
                    srl_content = str(srl).split('-')
                    if srl_content[0] in verb_srl_dict[verb]:
                        verb_srl_dict[verb][srl_content[0]].append(srl_content[1])
                    else:
                        verb_srl_dict[verb].update({srl_content[0]: []})
                        verb_srl_dict[verb][srl_content[0]].append(srl_content[1])
            # 获取依存句法分析结果
            cursor.execute(SELECT_DP_SQL, (law_id, article_class, chapter_id, sentence_id, parse_sentence))
            dp_results = cursor.fetchall()

            # 目标关系抽取核心
            aim_relation_list = []
            for verb in verb_srl_dict:
                if 'PRP' in verb_srl_dict[verb] and 'A1' in verb_srl_dict[verb] :
                    subject = verb + ' ' + verb_srl_dict[verb]['A1'][0]
                    object = verb_srl_dict[verb]['PRP'][0]
                    object = aim_wash(object)
                    aim_relation_list.append(tuple((subject, 'aim', object)))

            if '为' in verb_srl_dict and 'A1' in verb_srl_dict['为']:
                if '目标' in verb_srl_dict['为']['A1']:        # 确定有关系
                    if 'A0' in verb_srl_dict['为']:
                        subject = verb_srl_dict['为']['A0'][0]
                        if 'A2' in verb_srl_dict['为']:
                            object = verb_srl_dict['为']['A2'][0]
                        elif re.search(aim_reg, parse_sentence):
                            object = re.search(aim_reg, parse_sentence).group(1)
                    else:
                        sbv, vob = find_sbv_and_vob(verb, dp_results)
                        if sbv is not None:
                            subject = subject_complete(sbv, dp_results)
                            if 'A2' in verb_srl_dict['为']:
                                object = verb_srl_dict['为']['A2'][0]
                            elif re.search(aim_reg, parse_sentence):
                                object = re.search(aim_reg, parse_sentence).group(1)
                        elif find_core_verb(dp_results) is not None:
                            subject = subject_complete(find_core_verb(dp_results), dp_results)
                            if 'A2' in verb_srl_dict['为']:
                                object = verb_srl_dict['为']['A2'][0]
                            elif re.search(aim_reg, parse_sentence):
                                object = re.search(aim_reg, parse_sentence).group(1)
                        else:
                            subject = ''
                            object = ''
                    if subject and object and len(subject) >= 2 and len(object) > 2:
                        object = aim_wash(object)
                        aim_relation_list.append(tuple((subject, 'aim', object)))
            if len(aim_relation_list) > 0:
                print(parse_sentence)
                extract_num = extract_num + 1
                for rel in aim_relation_list:
                    data = {
                        'law_id': law_id,
                        'chapter_id': chapter_id,
                        'sentence_id': sentence_id,
                        'parse_sentence': parse_sentence,
                        'subject': rel[0],
                        'relation': '目标',
                        'object': rel[2],
                    }
                    save_relation(relation_type, data)
                print('\n******************************************************************************\n')

    print("totle: %s \n extract: %s \n rate: %s" % (collect_num, extract_num, extract_num / collect_num))


if __name__ == '__main__':
    aim_relation_collect = get_relation_collect('aim')
    aim_relation_extract(aim_relation_collect, 'aim')