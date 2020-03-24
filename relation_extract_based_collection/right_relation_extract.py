#!/usr/bin/env python
# coding=utf-8
from relation_extract_based_collection.relation_extract import *
from data_resource import conn
import re


def right_relation_extract(right_relation_collect, relation_type):
    cursor = conn.cursor()
    special_reg = "[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”《》〔〕：；！，。？、~@#￥%……&*（）]+"
    head_reg = "^[一二三四五六七八（１２３４５６７８９０]1234567890"
    right_reg1 = "(.*)履行(.*?)义务[，；。]"
    right_reg2 = "(.*)有(.*?)的义务[，；。]"
    right_reg3 = "(.*)有权(.*?)[，；。]"
    right_reg4 = "(.*)有义务(.*?)[，；。]"
    collect_num = len(right_relation_collect)
    extract_num = 0
    output_path = "G:\\analysis\\relation\\" + relation_type + ".txt"
    with open(output_path, "a") as w:
        for res in right_relation_collect:
            law_id = res[1]
            article_class = res[2]
            chapter_id = res[3]
            sentence_id = res[4]
            parse_sentence = res[6]
            relation_type = res[7]
            is_complex = res[8]

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

            right_relation_list = []
            subject = ''
            object = ''
            core_verb = find_core_verb(dp_results)
            core_sbv, core_vob = find_sbv_and_vob(core_verb, dp_results)
            if core_sbv is not None:
                core_subject = subject_complete(core_sbv, dp_results)
            else:
                core_subject = ''

            # 权利与义务关系抽取核心
            right_pattern1 = re.search(right_reg1, parse_sentence)
            right_pattern2 = re.search(right_reg2, parse_sentence)
            if right_pattern1:
                subject_tmp = right_pattern1.group(1)
                object = right_pattern1.group(2)
            elif right_pattern2:
                subject_tmp = right_pattern2.group(1)
                object = right_pattern2.group(2)
            else:
                subject_tmp = ''
                object = ''
            if object is not None and object != '':
                if core_subject is not None and core_subject != '':
                    subject = core_subject
                else:
                    subject = subject_tmp
            if len(subject) >= 2 and len(object) >= 2:
                right_relation_list.append(tuple((subject, 'right', object)))

            subject = ''
            object = ''
            if '有' in verb_srl_dict and 'A1' in verb_srl_dict['有']:
                if '权' in verb_srl_dict['有']['A1']:
                    right_pattern3 = re.search(right_reg3, parse_sentence)
                    if right_pattern3 and 'A0' in verb_srl_dict['有']:
                        subject = verb_srl_dict['有']['A0'][-1]
                        object = right_pattern3.group(2)
                    elif right_pattern3 and 'A0' not in verb_srl_dict['有']:
                        if core_subject is not None and core_subject != '':
                            subject = core_subject
                            object = right_pattern3.group(2)
                        else:
                            subject = right_pattern3.group(1)
                            object = right_pattern3.group(2)

                elif '义务' in verb_srl_dict['有']['A1']:
                    right_pattern4 = re.search(right_reg4, parse_sentence)
                    if right_pattern4 and 'A0' in verb_srl_dict['有']:
                        subject = verb_srl_dict['有']['A0'][-1]
                        object = right_pattern4.group(2)
                    elif right_pattern4 and 'A0' not in verb_srl_dict['有']:
                        if core_subject is not None and core_subject != '':
                            subject = core_subject
                            object = right_pattern4.group(2)
                        else:
                            subject = right_pattern4.group(1)
                            object = right_pattern4.group(2)
                if len(subject) >= 2 and len(object) >= 2:
                    right_relation_list.append(tuple((subject, 'right', object)))

            if len(right_relation_list) > 0:
                extract_num = extract_num + 1
                for rel in right_relation_list:
                    data = {
                        'law_id': law_id,
                        'chapter_id': chapter_id,
                        'sentence_id': sentence_id,
                        'parse_sentence': parse_sentence,
                        'subject': rel[0],
                        'relation': '权利/义务',
                        'object': rel[2]
                    }
                    save_relation(relation_type, data)

    print("totle: %s \n extract: %s \n rate: %s" % (collect_num, extract_num, extract_num / collect_num))


if __name__ == '__main__':
    right_relation_collect = get_relation_collect('right')
    right_relation_extract(right_relation_collect, 'right')