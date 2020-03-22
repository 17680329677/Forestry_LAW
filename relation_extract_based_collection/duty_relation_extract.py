#!/usr/bin/env python
# coding=utf-8
from relation_extract_based_collection.relation_extract import *
from data_resource import conn
import re


def duty_subject_wash(subject):
    subject = str(subject).strip()
    if subject.startswith('由'):
        subject = subject[1:]
    return subject


def duty_relation_extract(duty_relation_collect, relation_type):
    cursor = conn.cursor()
    special_reg = "[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”《》〔〕：；！，。？、~@#￥%……&*（）]+"
    head_reg = "^[一二三四五六七八（１２３４５６７８９０]1234567890"
    collect_num = len(duty_relation_collect)
    extract_num = 0
    output_path = "G:\\analysis\\relation\\" + relation_type + ".txt"
    with open(output_path, "a") as w:
        for res in duty_relation_collect:
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

            duty_relation_list = []
            core_verb = find_core_verb(dp_results)
            core_sbv, core_vob = find_sbv_and_vob(core_verb, dp_results)
            if core_sbv is not None:
                core_subject = subject_complete(core_sbv, dp_results)
            else:
                core_subject = ''

            for verb in verb_srl_dict:
                if 'A0' in verb_srl_dict[verb] and 'A1' in verb_srl_dict[verb]:
                    subject = verb_srl_dict[verb]['A0'][-1]
                    for a0 in verb_srl_dict[verb]['A0'][:-1]:
                        object = object + ' ' + a0
                    object = object + ' ' + verb + ' ' + verb_srl_dict[verb]['A1'][0]
                    if len(subject) >= 2 and len(object) >= 2:
                        subject = duty_subject_wash(subject)
                        duty_relation_list.append(tuple((subject, 'duty', object)))

                elif 'A0' in verb_srl_dict[verb] and 'A1' not in verb_srl_dict[verb]:
                    subject = verb_srl_dict[verb]['A0'][-1]
                    sbv, vob = find_sbv_and_vob(verb, dp_results)
                    if vob is not None:
                        object = object_complete(vob, dp_results)
                    else:
                        object = ''
                    if len(subject) >= 2 and len(object) >= 2:
                        subject = duty_subject_wash(subject)
                        duty_relation_list.append(tuple((subject, 'duty', object)))
                elif 'A0' not in verb_srl_dict[verb] and 'A1' in verb_srl_dict[verb]:
                    sbv, vob = find_sbv_and_vob(verb, dp_results)
                    if sbv is not None:
                        subject = subject_complete(sbv, dp_results)
                    elif core_subject is not None and core_subject != '':
                        subject = core_subject
                    else:
                        subject = ''
                    object = verb + ' ' + verb_srl_dict[verb]['A1'][0]
                    if len(subject) >= 2 and len(object) >= 4:
                        subject = duty_subject_wash(subject)
                        duty_relation_list.append(tuple((subject, 'duty', object)))

            if len(duty_relation_list) > 0:
                extract_num = extract_num + 1
                for rel in duty_relation_list:
                    data = {
                        'law_id': law_id,
                        'chapter_id': chapter_id,
                        'sentence_id': sentence_id,
                        'parse_sentence': parse_sentence,
                        'subject': rel[0],
                        'relation': '责任/要求/规定',
                        'object': rel[2],
                    }
                    save_relation(relation_type, data)

    print("totle: %s \n extract: %s \n rate: %s" % (collect_num, extract_num, extract_num / collect_num))


if __name__ == '__main__':
    duty_relation_collect = get_relation_collect('duty')
    duty_relation_extract(duty_relation_collect, 'duty')