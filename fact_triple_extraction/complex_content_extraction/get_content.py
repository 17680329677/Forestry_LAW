#!/usr/bin/env python
# coding=utf-8
from pyltp import SentenceSplitter
from fact_triple_extraction.xf_ltp_api import *


def get_article_1_complex_content():
    select_sql = '''select * from article_1_sentence where is_single = 0 limit 20'''
    cursor = conn.cursor()
    cursor.execute(select_sql)
    complex_contents = cursor.fetchall()
    result = []
    for c_content in complex_contents:
        long_content = str(c_content[3]).strip()
        content_list = SentenceSplitter.split(str(c_content[3]).strip())
        for content in content_list:
            if '：' in content and len(content) > 6:
                result.append(content.strip())
    return result


def get_article_2_complex_content():
    pass


def xunfei_complex_analysis(content_list):
    dp_tags, sdp_tags = get_tags()
    output_file = "F:\\dhz\\test\\complex_content\\test.txt"
    for content in content_list:
        words_list = func_cas(word_segment(content), word_segment, content, 'word')  # 分词结果
        # postags_list = func_cas(word_postag(content), word_postag, content, 'pos')  # 词性标注结果
        # dp_info = func_cas(dependency_parse(content), dependency_parse, content, 'dp')  # 依存句法分析
        # # [{'beg': 0, 'end': 1, 'id': 3, 'type': 'A0'}, {'beg': 4, 'end': 5, 'id': 3, 'type': 'A1'}]
        srl_info = func_cas(semantic_role_labeller(content), semantic_role_labeller, content, 'srl')  # 语义角色标注分析
        # sdgp_info = func_cas(semantic_dependency_parse(content), semantic_dependency_parse, content, 'sdgp')  # 语义依存分析

        with open(output_file, "a") as w:
            w.write(content + '\n')
            # print('-------------------------句法依存分析结果打印----------------------------')
            # w.write('-------------------------句法依存分析结果打印----------------------------' + '\n')
            # for index in range(len(dp_info)):
            #     parent_index = dp_info[index]['parent']
            #     if parent_index == -1:
            #         parent_word = 'Root'
            #     else:
            #         parent_word = words_list[parent_index]
            #     child_index = index
            #     child_word = words_list[child_index]
            #     reletion_name = dp_tags[dp_info[index]['relate']]
            #     print("%s -----(%s)---- %s" % (parent_word, reletion_name, child_word))
            #     w.write("%s -----(%s)---- %s\n" % (parent_word, reletion_name, child_word))
            #
            # print('-------------------------语义依存分析结果打印----------------------------')
            # w.write('-------------------------语义依存分析结果打印----------------------------' + '\n')
            # for sdp_index in range(len(sdgp_info)):
            #     sdp_parent_index = sdgp_info[sdp_index]['parent']
            #     if sdp_parent_index == -1:
            #         sdp_parent_word = 'Root'
            #     else:
            #         sdp_parent_word = words_list[sdp_parent_index]
            #     sdp_child_index = sdgp_info[sdp_index]['id']
            #     sdp_child_word = words_list[sdp_child_index]
            #     if sdgp_info[sdp_index]['relate'] in sdp_tags:
            #         semantic_dp_name = sdp_tags[sdgp_info[sdp_index]['relate']]
            #     elif str(sdgp_info[sdp_index]['relate']).startswith('r'):
            #         main_relate = '' + str(sdgp_info[sdp_index]['relate'])[1:]
            #         semantic_dp_name = sdp_tags[main_relate] + '--反角色'
            #     elif str(sdgp_info[sdp_index]['relate']).startswith('d'):
            #         main_relate = '' + str(sdgp_info[sdp_index]['relate'])[1:]
            #         semantic_dp_name = sdp_tags[main_relate] + '--嵌套角色'
            #     else:
            #         semantic_dp_name = sdgp_info[sdp_index]['relate']
            #     print("%s(%s)-----%s-----%s(%s)" % (
            #         sdp_parent_word, postags_list[sdp_parent_index], semantic_dp_name, sdp_child_word,
            #         postags_list[sdp_child_index]))
            #     w.write("%s(%s)-----%s-----%s(%s)\n" % (
            #         sdp_parent_word, postags_list[sdp_parent_index], semantic_dp_name, sdp_child_word,
            #         postags_list[sdp_child_index]))

            print('-------------------------语义角色分析结果打印----------------------------')
            w.write('-------------------------语义角色分析结果打印----------------------------' + '\n')
            role_lable_dict = dict()
            for role_label in srl_info:
                verb = words_list[role_label['id']]
                begin = role_label['beg']
                end = role_label['end']
                if verb in role_lable_dict:
                    role_lable_dict[verb].append(
                        tuple((role_label['type'], "".join(words_list[begin: end+1]))))
                else:
                    role_lable_dict.update({verb: []})
                    role_lable_dict[verb].append(
                        tuple((role_label['type'], "".join(words_list[begin: end + 1]))))
            print(role_lable_dict)

            print('===============================================================================================')
            w.write(
                '================================================================================================='
                '=================================================================================================' + '\n\n\n')


if __name__ == '__main__':
    content_list = get_article_1_complex_content()
    xunfei_complex_analysis(content_list)
