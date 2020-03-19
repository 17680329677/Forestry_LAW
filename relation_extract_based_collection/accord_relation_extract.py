#!/usr/bin/env python
# coding=utf-8
from relation_extract_based_collection.relation_extract import *
from data_resource import conn
import re


def accord_relation_extract(accord_relation_collect, relation_type):
    cursor = conn.cursor()
    special_reg = "[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”《》〔〕：；！，。？、~@#￥%……&*（）]+"
    head_reg = "^[一二三四五六七八（１２３４５６７８９０]1234567890"
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

            # 依据关系抽取核心
            accord_relation_list = []
            core_verb = find_core_verb(dp_results)
            print(parse_sentence)
            for verb in verb_srl_dict:
                sub = None
                obj = None
                if 'MNR' in verb_srl_dict[verb]:
                    if 'ADV' in verb_srl_dict[verb] and ('未' in verb_srl_dict[verb]['ADV'] or
                                                         '不得' in verb_srl_dict[verb]['ADV'] or
                                                         '不' in verb_srl_dict[verb]['ADV']):
                        continue
                    sbv, vob = find_sbv_and_vob(verb, dp_results)
                    if sbv is not None:
                        sub = subject_complete(sbv, dp_results)
                    if vob is not None:
                        obj = object_complete(vob, dp_results)

                    if 'A0' in verb_srl_dict[verb] and 'A1' in verb_srl_dict[verb] and len(verb_srl_dict[verb]['MNR'][0]) > 2:
                        for a1 in verb_srl_dict[verb]['A1']:
                            subject = verb_srl_dict[verb]['A0'][0] + ' ' + verb + ' ' + a1
                            object =  verb_srl_dict[verb]['MNR'][0]
                            accord_relation_list.append(tuple((subject, 'accord', object)))
                    elif 'A0' not in verb_srl_dict[verb] and 'A1' in verb_srl_dict[verb] and sub is not None and len(verb_srl_dict[verb]['MNR'][0]) > 2:
                        for a1 in verb_srl_dict[verb]['A1']:
                            subject = sub + ' ' + verb + ' ' + a1
                            object =  verb_srl_dict[verb]['MNR'][0]
                            accord_relation_list.append(tuple((subject, 'accord', object)))
                    elif 'A0' not in verb_srl_dict[verb] and 'A1' in verb_srl_dict[verb] and sub is None and len(verb_srl_dict[verb]['MNR'][0]) > 2:
                        for a1 in verb_srl_dict[verb]['A1']:
                            subject = verb + ' ' + a1
                            object = verb_srl_dict[verb]['MNR'][0]
                            accord_relation_list.append(tuple((subject, 'accord', object)))
                    elif 'A0' not in verb_srl_dict[verb] and 'A1' not in verb_srl_dict[verb] and sub is not None and obj is not None and len(verb_srl_dict[verb]['MNR'][0]) > 2:
                        subject = sub + ' ' + verb + ' ' + obj
                        object = verb_srl_dict[verb]['MNR'][0]
                        accord_relation_list.append(tuple((subject, 'accord', object)))
                    elif 'A0' not in verb_srl_dict[verb] and 'A1' not in verb_srl_dict[verb] and sub is None and obj is not None and len(verb_srl_dict[verb]['MNR'][0]) > 2:
                        subject = verb + ' ' + obj
                        object = verb_srl_dict[verb]['MNR'][0]
                        accord_relation_list.append(tuple((subject, 'accord', object)))
                else:
                    continue
            if len(accord_relation_list) > 0:
                extract_num = extract_num + 1
                print(parse_sentence)
                for rel in accord_relation_list:
                    print(rel)
                print('\n*************************************************************************************\n')
    print("totle: %s \n extract: %s \n rate: %s" % (collect_num, extract_num, extract_num / collect_num))


if __name__ == '__main__':
    accord_relation_collect = get_relation_collect('accord')
    accord_relation_extract(accord_relation_collect, 'accord')