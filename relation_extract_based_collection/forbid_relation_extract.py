#!/usr/bin/env python
# coding=utf-8
from relation_extract_based_collection.relation_extract import *
from data_resource import conn
import re


def forbid_relation_extract(forbid_relation_collect, relation_type):
    cursor = conn.cursor()
    special_reg = "[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”《》〔〕：；！，。？、~@#￥%……&*（）]+"
    head_reg = "^[一二三四五六七八（１２３４５６７８９０]1234567890"
    forbid_reg1 = "[在 ](.*)[内 ]禁止(.*?)[，；。]"
    forbid_reg2 = "(.*)严禁(.*?)[，；。]"
    forbid_reg3 = "(.*)不得(.*?)[，；。]"
    forbid_reg4 = "(.*)不允许(.*?)[，；。]"
    collect_num = len(forbid_relation_collect)
    extract_num = 0
    output_path = "G:\\analysis\\relation\\" + relation_type + ".txt"
    with open(output_path, "a") as w:
        for res in forbid_relation_collect:
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
            role_content_list = []
            for verb in srl_dict:
                verb_srl_dict.update({verb: {}})
                for srl in srl_dict[verb]:
                    if 'C-A1' in srl:
                        verb_srl_dict[verb].update({'C-A1': [str(srl).replace('C-A1-', '')]})
                    srl_content = str(srl).split('-')
                    role_content_list.append(srl_content[1])
                    if srl_content[0] in verb_srl_dict[verb]:
                        verb_srl_dict[verb][srl_content[0]].append(srl_content[1])
                    else:
                        verb_srl_dict[verb].update({srl_content[0]: []})
                        verb_srl_dict[verb][srl_content[0]].append(srl_content[1])

            # 获取依存句法分析结果
            cursor.execute(SELECT_DP_SQL, (law_id, article_class, chapter_id, sentence_id, parse_sentence))
            dp_results = cursor.fetchall()

            forbid_relation_list = []
            subject = ''
            object = ''
            core_verb = find_core_verb(dp_results)
            core_sbv, core_vob = find_sbv_and_vob(core_verb, dp_results)
            if core_sbv is not None:
                core_subject = subject_complete(core_sbv, dp_results)
            else:
                core_subject = ''

            if '禁止' in verb_srl_dict:
                if 'A0' in verb_srl_dict['禁止'] and 'A1' in verb_srl_dict['禁止']:
                    subject = verb_srl_dict['禁止']['A0'][0]
                    for a1 in verb_srl_dict['禁止']['A1']:
                        object = a1
                        if len(subject) >= 2 and len(object) >= 2:
                            forbid_relation_list.append(tuple((subject, 'forbid', object)))
                elif 'LOC' in verb_srl_dict['禁止'] and 'A1' in verb_srl_dict['禁止']:
                    subject = verb_srl_dict['禁止']['LOC'][0]
                    for a1 in verb_srl_dict['禁止']['A1']:
                        object = a1
                        if len(subject) >= 2 and len(object) >= 2:
                            forbid_relation_list.append(tuple((subject, 'forbid', object)))
                elif 'A0' not in verb_srl_dict['禁止'] and 'LOC' not in verb_srl_dict['禁止'] and 'A1' in verb_srl_dict['禁止']:
                    sbv, vob = find_sbv_and_vob(verb, dp_results)
                    if sbv is not None:
                        subject = subject_complete(sbv, dp_results)
                    elif core_subject is not None and core_subject != '':
                        subject = core_subject
                    elif re.search(forbid_reg1, parse_sentence):
                        subject = re.search(forbid_reg1, parse_sentence).group(1)
                    else:
                        subject = 'law' + '-' + str(law_id)
                    if len(subject) >= 2:
                        for a1 in verb_srl_dict['禁止']['A1']:
                            object = a1
                            if len(object) >= 2:
                                forbid_relation_list.append(tuple((subject, 'forbid', object)))

            elif '严禁' in verb_srl_dict:
                if 'A0' in verb_srl_dict['严禁'] and 'A1' in verb_srl_dict['严禁']:
                    subject = verb_srl_dict['严禁']['A0'][0]
                    for a1 in verb_srl_dict['严禁']['A1']:
                        object = a1
                        if len(subject) >= 2 and len(object) >= 2:
                            forbid_relation_list.append(tuple((subject, 'forbid', object)))
                elif 'LOC' in verb_srl_dict['严禁'] and 'A1' in verb_srl_dict['严禁']:
                    subject = verb_srl_dict['严禁']['LOC'][0]
                    for a1 in verb_srl_dict['严禁']['A1']:
                        object = a1
                        if len(subject) >= 2 and len(object) >= 2:
                            forbid_relation_list.append(tuple((subject, 'forbid', object)))
                elif 'LOC' in verb_srl_dict['严禁'] and 'C-A1' in verb_srl_dict['严禁']:
                    subject = verb_srl_dict['严禁']['LOC'][0]
                    for c_a1 in verb_srl_dict['严禁']['C-A1']:
                        object = c_a1
                        if len(subject) >= 2 and len(object) >= 2:
                            forbid_relation_list.append(tuple((subject, 'forbid', object)))

                elif 'A0' not in verb_srl_dict['严禁'] and 'LOC' not in verb_srl_dict['严禁'] and 'A1' in verb_srl_dict['严禁']:
                    sbv, vob = find_sbv_and_vob(verb, dp_results)
                    if sbv is not None:
                        subject = subject_complete(sbv, dp_results)
                    elif core_subject is not None and core_subject != '':
                        subject = core_subject
                    elif re.search(forbid_reg1, parse_sentence):
                        subject = re.search(forbid_reg1, parse_sentence).group(1)
                    else:
                        subject = 'law' + '-' + str(law_id)
                    if len(subject) >= 2:
                        for a1 in verb_srl_dict['严禁']['A1']:
                            object = a1
                            if len(object) >= 2:
                                forbid_relation_list.append(tuple((subject, 'forbid', object)))
                elif 'A0' not in verb_srl_dict['严禁'] and 'LOC' not in verb_srl_dict['严禁'] and 'C-A1' in verb_srl_dict['严禁']:
                    sbv, vob = find_sbv_and_vob(verb, dp_results)
                    if sbv is not None:
                        subject = subject_complete(sbv, dp_results)
                    elif core_subject is not None and core_subject != '':
                        subject = core_subject
                    elif re.search(forbid_reg1, parse_sentence):
                        subject = re.search(forbid_reg1, parse_sentence).group(1)
                    else:
                        subject = 'law' + '-' + str(law_id)
                    if len(subject) >= 2:
                        for a1 in verb_srl_dict['严禁']['C-A1']:
                            object = a1
                            if len(object) >= 2:
                                forbid_relation_list.append(tuple((subject, 'forbid', object)))

            elif '严禁' not in verb_srl_dict and '严禁' in parse_sentence:
                forbid_pattern2 = re.search(forbid_reg2, parse_sentence)
                if core_subject is not None and core_subject != '' and forbid_pattern2:
                    subject = core_subject
                    object = forbid_pattern2.group(2)
                elif (core_subject is None or core_subject == '') and forbid_pattern2:
                    subject = forbid_pattern2.group(1)
                    object = forbid_pattern2.group(2)
                else:
                    subject = ''
                    object = ''
                if len(subject) >= 2 and len(object) >= 2:
                    forbid_relation_list.append(tuple((subject, 'forbid', object)))

            elif '不得' in parse_sentence:
                forbid_pattern3 = re.search(forbid_reg3, parse_sentence)
                if core_subject is not None and core_subject != '' and forbid_pattern3:
                    subject = core_subject
                    object = forbid_pattern3.group(2)
                elif (core_subject is None or core_subject == '') and forbid_pattern3:
                    subject = forbid_pattern3.group(1)
                    object = forbid_pattern3.group(2)
                else:
                    subject = ''
                    object = ''
                if len(subject) >= 2 and len(object) >= 2:
                    forbid_relation_list.append(tuple((subject, 'forbid', object)))

            elif '不允许' in parse_sentence:
                forbid_pattern4 = re.search(forbid_reg4, parse_sentence)
                if core_subject is not None and core_subject != '' and forbid_pattern4:
                    subject = core_subject
                    object = forbid_pattern4.group(2)
                elif (core_subject is None or core_subject == '') and forbid_pattern4:
                    subject = forbid_pattern4.group(1)
                    object = forbid_pattern4.group(2)
                else:
                    subject = ''
                    object = ''
                if len(subject) >= 2 and len(object) >= 2:
                    forbid_relation_list.append(tuple((subject, 'forbid', object)))

            if len(forbid_relation_list) > 0:
                extract_num = extract_num + 1
                for rel in forbid_relation_list:
                    data = {
                        'law_id': law_id,
                        'chapter_id': chapter_id,
                        'sentence_id': sentence_id,
                        'parse_sentence': parse_sentence,
                        'subject': rel[0],
                        'relation': '令行禁止',
                        'object': rel[2],
                    }
                    save_relation(relation_type, data)
                print('\n****************************************************************************\n')

    print("totle: %s \n extract: %s \n rate: %s" % (collect_num, extract_num, extract_num / collect_num))


if __name__ == '__main__':
    forbid_relation_collect = get_relation_collect('forbid')
    forbid_relation_extract(forbid_relation_collect, 'forbid')