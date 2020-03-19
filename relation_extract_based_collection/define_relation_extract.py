#!/usr/bin/env python
# coding=utf-8
from relation_extract_based_collection.relation_extract import *
from data_resource import conn
import re


def define_relation_extract(define_relation_collect, relation_type):
    cursor = conn.cursor()
    special_reg = "[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”《》〔〕：；！，。？、~@#￥%……&*（）]+"
    head_reg = "^[一二三四五六七八（１２３４５６７８９０]1234567890"
    collect_num = len(define_relation_collect)
    extract_num = 0
    output_path = "G:\\analysis\\relation\\" + relation_type + ".txt"
    with open(output_path, "a") as w:
        for res in define_relation_collect:
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
            verb_srl_dict = {'是': {}, '指': {}}
            if '是' in srl_dict:
                for srl in srl_dict['是']:
                    srl_content = str(srl).split('-')
                    if srl_content[0] in verb_srl_dict['是']:
                        verb_srl_dict['是'][srl_content[0]].append(srl_content[1])
                    else:
                        verb_srl_dict['是'].update({srl_content[0]: []})
                        verb_srl_dict['是'][srl_content[0]].append(srl_content[1])
            if '指' in srl_dict:
                for srl in srl_dict['指']:
                    srl_content = str(srl).split('-')
                    if srl_content[0] in verb_srl_dict['指']:
                        verb_srl_dict['指'][srl_content[0]].append(srl_content[1])
                    else:
                        verb_srl_dict['指'].update({srl_content[0]: []})
                        verb_srl_dict['指'][srl_content[0]].append(srl_content[1])
            subject1 = ''
            subject2 = ''
            subject = ''
            object = ''
            # 1. 需要根据条款补充
            if is_complex == 1:
                if 'A0' in verb_srl_dict['是'] and 'A1' in verb_srl_dict['是']:
                    subject = verb_srl_dict['是']['A0'][0]
                    object = verb_srl_dict['是']['A1'][0]
                else:
                    if 'A0' in verb_srl_dict['是']:
                        subject1 = verb_srl_dict['是']['A0'][0]
                    if 'A1' in verb_srl_dict['指']:
                        subject2 = verb_srl_dict['指']['A1'][0]
                    if subject1 != '' and subject2 != '' and subject1 == subject2:
                        subject = subject1
                        object = '待补充'
                    elif subject1 != '' and subject2 == '':
                        subject = subject1
                        object = '待补充'
                    elif subject1 == '' and subject2 != '':
                        subject = subject2
                        object = '待补充'
                    else:
                        continue
                if subject != '' and object == '待补充':
                    object = clause_supplement(article_class, sentence_id)
            # 2. 不需要补充直接抽取
            else:
                if 'A0' in verb_srl_dict['是'] and 'A1' in verb_srl_dict['是']:
                    subject = verb_srl_dict['是']['A0'][0]
                    object = verb_srl_dict['是']['A1'][0]
                elif 'A1' in verb_srl_dict['指'] and 'A2' in verb_srl_dict['指']:
                    subject = verb_srl_dict['指']['A1'][0]
                    object = verb_srl_dict['指']['A2'][0]
                else:
                    continue
            if subject != '' and object != '':
                subject = re.sub(special_reg, "", subject)
                if len(subject) >= 2 and len(object) >= 2:
                    data = {
                        'law_id': law_id,
                        'chapter_id': chapter_id,
                        'sentence_id': sentence_id,
                        'parse_sentence': parse_sentence,
                        'subject': subject,
                        'relation': '是/指',
                        'object': object,
                    }
                    extract_num = extract_num + 1
                    # print('<%s， %s， %s>' % (subject, 'define', object))
                    w.write(parse_sentence + '\n')
                    w.write('<%s， %s， %s>\n' % (subject, 'define', object))
                    w.write('\n*********************************************************************************\n')
                    save_relation(relation_type, data)
        print("totle: %s \n extract: %s \n rate: %s" % (collect_num, extract_num, extract_num / collect_num))
        w.write("totle: %s \n extract: %s \n rate: %s" % (collect_num, extract_num, extract_num / collect_num))


if __name__ == '__main__':
    define_relation_collect = get_relation_collect('define')
    define_relation_extract(define_relation_collect, 'define')