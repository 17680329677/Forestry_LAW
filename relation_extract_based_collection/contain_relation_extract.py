#!/usr/bin/env python
# coding=utf-8
from relation_extract_based_collection.relation_extract import *
from data_resource import conn
import re


def contain_content_split(is_complex, object):
    object = str(object).strip()
    if len(object) < 2:
        return ''

    if is_complex == 1:
        obj_list = object.split('\n')
        object = "-".join(obj_list)
    else:
        # 1. 顿号
        dun_list = object.split('、')
        # 1.2 逗号
        dou_list = []
        for dun in dun_list:
            tmp_list = dun.split('，')
            for tmp in tmp_list:
                dou_list.append(tmp)
        # 2. '和'
        and_list = []
        for dou in dou_list:
            tmp_list = dou.split('和')
            for tmp in tmp_list:
                and_list.append(tmp)
        # 3. '以及'
        yiji_list = []
        for a in and_list:
            tmp_list = a.split('以及')
            for tmp in tmp_list:
                yiji_list.append(tmp)
        # 4. '及'
        ji_list = []
        for yiji in yiji_list:
            tmp_list = yiji.split('以及')
            for tmp in tmp_list:
                ji_list.append(tmp)
        # 5. '与'
        final_list = []
        for ji in ji_list:
            tmp_list = ji.split('与')
            for tmp in tmp_list:
                final_list.append(tmp)

        if final_list[-1].endswith('等'):
            final_list[-1] = final_list[-1].replace('等', '')

        object = "-".join(final_list)
    return object


def contain_relation_extract(contain_relation_collect, relation_type):
    cursor = conn.cursor()
    special_reg = "[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”《》〔〕：；！，。？、~@#￥%……&*（）]+"
    head_reg = "^[一二三四五六七八（１２３４５６７８９０]1234567890"
    contain_reg1 = "(.*)分为(.*?)[，；。]"
    contain_reg2 = "(.*)包括(.*?)[，；。]"
    collect_num = len(contain_relation_collect)
    extract_num = 0
    output_path = "G:\\analysis\\relation\\" + relation_type + ".txt"
    with open(output_path, "a") as w:
        for res in contain_relation_collect:
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

            contain_relation_list = []
            subject = ''
            object = ''
            # 1. 需要根据条款补充
            if is_complex == 1:
                if '分为' in verb_srl_dict and 'A1' in verb_srl_dict['分为']:
                    subject = verb_srl_dict['分为']['A1'][0]
                    object = '待补充'
                elif '分为' in verb_srl_dict and 'LOC' in verb_srl_dict['分为']:
                    subject = verb_srl_dict['分为']['LOC'][0]
                    object = '待补充'
                elif '划分' in verb_srl_dict and 'A1' in verb_srl_dict['划分']:
                    subject = verb_srl_dict['划分']['A1'][0]
                    object = '待补充'
                elif '划分' in verb_srl_dict and 'LOC' in verb_srl_dict['划分']:
                    subject = verb_srl_dict['划分']['LOC'][0]
                    object = '待补充'
                elif '包括' in verb_srl_dict and 'A0' in verb_srl_dict['包括']:
                    subject = verb_srl_dict['包括']['A0'][0]
                    object = '待补充'
                elif '包括' in verb_srl_dict and 'LOC' in verb_srl_dict['包括']:
                    subject = verb_srl_dict['包括']['LOC'][0]
                    object = '待补充'

                if subject != '' and object == '待补充':
                    object = clause_supplement(article_class, sentence_id)
                    object = contain_content_split(1, object)
                    if len(object) >= 2:
                        contain_relation_list.append(tuple((subject, 'contain', object)))
            # 2. 不需要补充
            else:
                if '分为' in verb_srl_dict or '划分' in verb_srl_dict:
                    if '分为' in verb_srl_dict:
                        v = '分为'
                    else:
                        v = '划分'

                    if 'A1' in verb_srl_dict[v] and 'A2' in verb_srl_dict[v]:
                        subject = verb_srl_dict[v]['A1'][0]
                        object = verb_srl_dict[v]['A2'][0]
                    elif 'A1' in verb_srl_dict[v] and 'A2' not in verb_srl_dict[v]:
                        if len(verb_srl_dict[v]['A1']) > 1:
                            subject = verb_srl_dict[v]['A1'][0]
                            object = verb_srl_dict[v]['A1'][1]
                        else:
                            subject = verb_srl_dict[v]['A1'][0]
                            contain_pattern = re.search(contain_reg1, parse_sentence)
                            if contain_pattern:
                                object = contain_pattern.group(2)
                            else:
                                object = ''
                    elif 'A1' not in verb_srl_dict[v] and 'A2' in verb_srl_dict[v]:
                        sbv, vob = find_sbv_and_vob(v, dp_results)
                        core_verb = find_core_verb(dp_results)
                        core_sbv, core_vob = find_sbv_and_vob(core_verb, dp_results)
                        if sbv is not None:
                            subject = subject_complete(sbv, dp_results)
                            object = verb_srl_dict[v]['A2'][0]
                        elif core_sbv is not None:
                            subject = subject_complete(core_sbv, dp_results)
                            object = verb_srl_dict[v]['A2'][0]
                    else:
                        subject = ''
                        object = ''
                elif '包括' in verb_srl_dict:
                    if 'A0' in verb_srl_dict['包括'] and 'A1' in verb_srl_dict['包括']:
                        subject = verb_srl_dict['包括']['A0'][0]
                        for a1 in verb_srl_dict['包括']['A1']:
                            object = object + ' ' + a1
                    elif 'LOC' in verb_srl_dict['包括'] and 'A1' in verb_srl_dict['包括']:
                        subject = verb_srl_dict['包括']['LOC'][0]
                        for a1 in verb_srl_dict['包括']['A1']:
                            object = object + ' ' + a1
                    elif'A0' not in verb_srl_dict['包括'] and 'LOC' not in verb_srl_dict['包括'] and 'A1' in verb_srl_dict['包括']:
                        sbv, vob = find_sbv_and_vob('包括', dp_results)
                        core_verb = find_core_verb(dp_results)
                        core_sbv, core_vob = find_sbv_and_vob(core_verb, dp_results)
                        if sbv is not None:
                            subject = subject_complete(sbv, dp_results)
                            object = verb_srl_dict['包括']['A1'][0]
                        elif core_sbv is not None:
                            subject = subject_complete(core_sbv, dp_results)
                            object = verb_srl_dict['包括']['A1'][0]
                    elif 'A0' in verb_srl_dict['包括'] and 'LOC' in verb_srl_dict['包括'] and 'A1' not in verb_srl_dict['包括']:
                        subject = verb_srl_dict['包括']['LOC'][0]
                        object = verb_srl_dict['包括']['A0'][0]
                    else:
                        subject = ''
                        object = ''
                # 对object做补充
                if subject != '' and object != '':
                    if len(object) < 5:
                        contain_pattern1 = re.search(contain_reg1, parse_sentence)
                        contain_pattern2 = re.search(contain_reg2, parse_sentence)
                        if contain_pattern1:
                            new_object = contain_pattern1.group(2)
                            if len(object) < len(new_object):
                                object = new_object
                        elif contain_pattern2:
                            new_object = contain_pattern2.group(2)
                            if len(object) < len(new_object):
                                object = new_object
                    object = contain_content_split(0, object)
                    if len(object) >= 2:
                        contain_relation_list.append(tuple((subject, 'contain', object)))

            if len(contain_relation_list) > 0:
                extract_num = extract_num + 1
                for rel in contain_relation_list:
                    data = {
                        'law_id': law_id,
                        'chapter_id': chapter_id,
                        'sentence_id': sentence_id,
                        'parse_sentence': parse_sentence,
                        'subject': rel[0],
                        'relation': '包括',
                        'object': rel[2],
                    }
                    save_relation(relation_type, data)

    print("totle: %s \n extract: %s \n rate: %s" % (collect_num, extract_num, extract_num / collect_num))


if __name__ == '__main__':
    contain_relation_collect = get_relation_collect('contain')
    contain_relation_extract(contain_relation_collect, 'contain')