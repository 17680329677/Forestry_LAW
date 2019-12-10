#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 讯飞LTP接口结合graphviz实现可视化
from graphviz import Digraph
from fact_triple_extraction.xf_ltp_api import *


dp_tags, sdp_tags = get_tags()


def xunfei_nlp_dp_parser(content):

    words_list = func_cas(word_segment(content), word_segment, content, 'word')  # 分词结果
    postags_list = func_cas(word_postag(content), word_postag, content, 'pos')  # 词性标注结果
    dp_info = func_cas(dependency_parse(content), dependency_parse, content, 'dp')  # 依存句法分析

    dot = Digraph(comment='The Round Table')
    tree_node = ['ROOT'] + words_list
    postags_list = ['none'] + postags_list
    for i in range(len(tree_node)):
        if postags_list[i] == 'v':
            dot.node('N' + str(i), tree_node[i] + '(' + postags_list[i] + ')', fontname="Microsoft YaHei", color='red')
        elif postags_list[i] == 'n':
            dot.node('N' + str(i), tree_node[i] + '(' + postags_list[i] + ')', fontname="Microsoft YaHei", color='blue')
        elif postags_list == 'ni':
            dot.node('N' + str(i), tree_node[i] + '(' + postags_list[i] + ')', fontname="Microsoft YaHei", color='yellow')
        else:
            dot.node('N' + str(i), tree_node[i] + '(' + postags_list[i] + ')', fontname="Microsoft YaHei")

    for i in range(len(dp_info)):
        parent_index = dp_info[i]['parent'] + 1
        child_index = i + 1
        dot.edge('N' + str(parent_index), 'N' + str(child_index),
                 label=dp_tags[dp_info[i]['relate']], fontname="Microsoft YaHei")
    dot.view()


def xunfei_nlp_sdp_parser(content):

    words_list = func_cas(word_segment(content), word_segment, content, 'word')  # 分词结果
    postags_list = func_cas(word_postag(content), word_postag, content, 'pos')  # 词性标注结果
    sdgp_info = func_cas(semantic_dependency_parse(content), semantic_dependency_parse, content, 'sdgp')  # 语义依存分析

    dot = Digraph(comment='The Round Table')
    tree_node = ['ROOT'] + words_list
    postags_list = ['none'] + postags_list
    for i in range(len(tree_node)):
        if postags_list[i] == 'v':
            dot.node('N' + str(i), tree_node[i] + '(' + postags_list[i] + ')', fontname="Microsoft YaHei", color='red')
        elif postags_list[i] == 'n':
            dot.node('N' + str(i), tree_node[i] + '(' + postags_list[i] + ')', fontname="Microsoft YaHei", color='blue')
        elif postags_list == 'ni':
            dot.node('N' + str(i), tree_node[i] + '(' + postags_list[i] + ')', fontname="Microsoft YaHei", color='yellow')
        else:
            dot.node('N' + str(i), tree_node[i] + '(' + postags_list[i] + ')', fontname="Microsoft YaHei")
    for i in range(len(sdgp_info)):
        child_index = sdgp_info[i]['id'] + 1
        parent_index = sdgp_info[i]['parent'] + 1
        if sdgp_info[i]['relate'] in sdp_tags:
            label = sdp_tags[sdgp_info[i]['relate']]
        else:
            label = sdgp_info[i]['relate']
        dot.edge('N' + str(parent_index), 'N' + str(child_index),
                 label=label, fontname="Microsoft YaHei")
    dot.view()


def xunfei_nlp_srl_parser(content):
    print(content)
    words_list = func_cas(word_segment(content), word_segment, content, 'word')  # 分词结果
    # postags_list = func_cas(word_postag(content), word_postag, content, 'pos')  # 词性标注结果
    srl_info = func_cas(semantic_role_labeller(content), semantic_role_labeller, content, 'srl')  # 语义角色标注分析
    srl_dict_by_verb = dict()
    for srl in srl_info:
        if srl['id'] in srl_dict_by_verb:
            srl_dict_by_verb[srl['id']].append(srl)
        else:
            srl_dict_by_verb.update({srl['id']: []})
            srl_dict_by_verb[srl['id']].append(srl)
    # {7: [{'beg': 0, 'end': 1, 'id': 7, 'type': 'A1'}, {'beg': 2, 'end': 6, 'id': 7, 'type': 'TMP'}],
    # 11: [{'beg': 9, 'end': 10, 'id': 11, 'type': 'A0'}, {'beg': 12, 'end': 12, 'id': 11, 'type': 'A1'}]}
    # for key in list(srl_dict_by_verb.keys()):
    #     core_verb = words_list[key]
    #     print(core_verb + "：", end="")
    #     for srl in srl_dict_by_verb[key]:
    #         print("".join(words_list[srl['beg']: srl['end'] + 1]), srl['type'], '\t', end="")
    #     print()
    # print(content, '--------------------PARSE SUCCESS')
    return words_list, srl_dict_by_verb


if __name__ == '__main__':
    content = "本办法自发布之日起执行，由水利部负责解释。"
    # content = "本办法由省财政厅负责解释。"
    xunfei_nlp_srl_parser(content)
    # xunfei_nlp_dp_parser(content)
    # xunfei_nlp_sdp_parser(content)