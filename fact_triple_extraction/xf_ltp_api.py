#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 讯飞自然语言处理接口调用
import time
import urllib.request
import urllib.parse
import json
import hashlib
import base64
import ast
from data_resource import conn

# 中文分词接口地址-cws
url_cws = "http://ltpapi.xfyun.cn/v1/cws"
# 词性标注接口地址-pos
url_pos = "http://ltpapi.xfyun.cn/v1/pos"
# 命名实体识别接口地址-ner
url_ner = "http://ltpapi.xfyun.cn/v1/ner"
# 依存句法分析接口地址-dp
url_dp = "http://ltpapi.xfyun.cn/v1/dp"
# 语义角色标注接口地址-srl
url_srl = "http://ltpapi.xfyun.cn/v1/srl"
# 语义依存分析接口地址-sdgp
url_sdgp = "http://ltpapi.xfyun.cn/v1/sdgp"
# 开放平台应用ID
x_appid = "5dcb67fc"
# 开放平台应用接口秘钥
api_key = "ae692f6e6934e1cdeb788e7854181443"
# 语言文本
TEXT = "为了促进绿化事业的发展，改善城市生态环境，根据国务院《城市绿化条例》以及有关法律、行政法规，结合本市实际，制定本条例。"


def word_segment(content):      # 分词
    body = urllib.parse.urlencode({'text': content}).encode('utf-8')
    param = {"type": "dependent"}
    x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode('utf-8'))
    x_time = str(int(time.time()))
    x_checksum = hashlib.md5(api_key.encode('utf-8') + str(x_time).encode('utf-8') + x_param).hexdigest()
    x_header = {'X-Appid': x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum}
    req = urllib.request.Request(url_cws, body, x_header)
    result = urllib.request.urlopen(req)
    result = result.read()
    if ast.literal_eval(result.decode('utf-8'))['code'] != '0' and \
            ast.literal_eval(result.decode('utf-8'))['code'] != '10700':
        print(result)
    # 返回分词结果list: ['项目', '开工', '须', '具备', '下列', '条件', '：']
    # return ast.literal_eval(result.decode('utf-8'))['data']['word']
    return ast.literal_eval(result.decode('utf-8'))


def word_postag(content):   # 词性标记
    body = urllib.parse.urlencode({'text': content}).encode('utf-8')
    param = {"type": "dependent"}
    x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode('utf-8'))
    x_time = str(int(time.time()))
    x_checksum = hashlib.md5(api_key.encode('utf-8') + str(x_time).encode('utf-8') + x_param).hexdigest()
    x_header = {'X-Appid': x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum}
    req = urllib.request.Request(url_pos, body, x_header)
    result = urllib.request.urlopen(req)
    result = result.read()
    if ast.literal_eval(result.decode('utf-8'))['code'] != '0' and \
            ast.literal_eval(result.decode('utf-8'))['code'] != '10700':
        print(result)
    # 返回词性标记结果list: ['n', 'v', 'd', 'v', 'b', 'n', 'wp']
    # return ast.literal_eval(result.decode('utf-8'))['data']['pos']
    return ast.literal_eval(result.decode('utf-8'))


def chinese_ner(content):       # 中文命名实体识别
    body = urllib.parse.urlencode({'text': content}).encode('utf-8')
    param = {"type": "dependent"}
    x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode('utf-8'))
    x_time = str(int(time.time()))
    x_checksum = hashlib.md5(api_key.encode('utf-8') + str(x_time).encode('utf-8') + x_param).hexdigest()
    x_header = {'X-Appid': x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum}
    req = urllib.request.Request(url_ner, body, x_header)
    result = urllib.request.urlopen(req)
    result = result.read()
    if ast.literal_eval(result.decode('utf-8'))['code'] != '0' and \
            ast.literal_eval(result.decode('utf-8'))['code'] != '10700':
        print(result)
    # 返回NER结果list: ['O', 'O', 'O', 'O', 'O', 'S-Ni', 'O', 'O']
    # return ast.literal_eval(result.decode('utf-8'))['data']['ner']
    return ast.literal_eval(result.decode('utf-8'))


def dependency_parse(content):       # 依存句法分析
    body = urllib.parse.urlencode({'text': content}).encode('utf-8')
    param = {"type": "dependent"}
    x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode('utf-8'))
    x_time = str(int(time.time()))
    x_checksum = hashlib.md5(api_key.encode('utf-8') + str(x_time).encode('utf-8') + x_param).hexdigest()
    x_header = {'X-Appid': x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum}
    req = urllib.request.Request(url_dp, body, x_header)
    result = urllib.request.urlopen(req)
    result = result.read()
    if ast.literal_eval(result.decode('utf-8'))['code'] != '0' and \
            ast.literal_eval(result.decode('utf-8'))['code'] != '10700':
        print(result)
    # 返回依存句法分析结果list:
    # [{'parent': 1, 'relate': 'SBV'}, {'parent': 3, 'relate': 'SBV'}, {'parent': 3, 'relate': 'ADV'},
    # {'parent': -1, 'relate': 'HED'}, {'parent': 5, 'relate': 'ATT'}, {'parent': 3, 'relate': 'VOB'},
    # {'parent': 3, 'relate': 'WP'}]
    # return ast.literal_eval(result.decode('utf-8'))['data']['dp']
    return ast.literal_eval(result.decode('utf-8'))


def semantic_role_labeller(content):       # 语义角色标注
    body = urllib.parse.urlencode({'text': content}).encode('utf-8')
    param = {"type": "dependent"}
    x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode('utf-8'))
    x_time = str(int(time.time()))
    x_checksum = hashlib.md5(api_key.encode('utf-8') + str(x_time).encode('utf-8') + x_param).hexdigest()
    x_header = {'X-Appid': x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum}
    req = urllib.request.Request(url_srl, body, x_header)
    result = urllib.request.urlopen(req)
    result = result.read()
    if ast.literal_eval(result.decode('utf-8'))['code'] != '0' and \
            ast.literal_eval(result.decode('utf-8'))['code'] != '10700':
        print(result)
    # 返回语义角色标注结果list: [{'beg': 0, 'end': 1, 'id': 3, 'type': 'A0'}, {'beg': 4, 'end': 5, 'id': 3, 'type': 'A1'}]
    # return ast.literal_eval(result.decode('utf-8'))['data']['srl']
    return ast.literal_eval(result.decode('utf-8'))


def semantic_dependency_parse(content):       # 语义依存分析
    body = urllib.parse.urlencode({'text': content}).encode('utf-8')
    param = {"type": "dependent"}
    x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode('utf-8'))
    x_time = str(int(time.time()))
    x_checksum = hashlib.md5(api_key.encode('utf-8') + str(x_time).encode('utf-8') + x_param).hexdigest()
    x_header = {'X-Appid': x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum}
    req = urllib.request.Request(url_sdgp, body, x_header)
    result = urllib.request.urlopen(req)
    result = result.read()
    if ast.literal_eval(result.decode('utf-8'))['code'] != '0' and \
            ast.literal_eval(result.decode('utf-8'))['code'] != '10700':
        print(result)
    # 返回语义依存分析结果list:
    # [{'id': 0, 'parent': 1, 'relate': 'Prod'}, {'id': 1, 'parent': 3, 'relate': 'dPoss'},
    # {'id': 2, 'parent': 3, 'relate': 'mMod'}, {'id': 3, 'parent': -1, 'relate': 'Root'},
    # {'id': 4, 'parent': 5, 'relate': 'Desc'}, {'id': 5, 'parent': 3, 'relate': 'Belg'},
    # {'id': 6, 'parent': 3, 'relate': 'mPunc'}]
    # return ast.literal_eval(result.decode('utf-8'))['data']['sdgp']
    return ast.literal_eval(result.decode('utf-8'))


def func_cas(res, func, content, data_param):
    count = 1
    while res['code'] == "10700":
        res = func(content)
        count = count + 1
        if count > 30:
            print('retry too many times--', str(func))
            return None
    # print(count, '---', res['data'][data_param])
    return res['data'][data_param]


def content_nlp(output_file, content, dp_tags, sdp_tags):
    print(content)
    words_list = func_cas(word_segment(content), word_segment, content, 'word')      # 分词结果

    postags_list = func_cas(word_postag(content), word_postag, content, 'pos')     # 词性标注结果

    dp_info = func_cas(dependency_parse(content), dependency_parse, content, 'dp')     # 依存句法分析

    srl_info = func_cas(semantic_role_labeller(content), semantic_role_labeller, content, 'srl')      # 语义角色标注分析

    sdgp_info = func_cas(semantic_dependency_parse(content), semantic_dependency_parse, content, 'sdgp')      # 语义依存分析

    with open(output_file, "a") as w:
        w.write(content + '\n')
        print('-------------------------句法依存分析结果打印----------------------------')
        w.write('-------------------------句法依存分析结果打印----------------------------' + '\n')
        for index in range(len(dp_info)):
            parent_index = dp_info[index]['parent']
            if parent_index == -1:
                parent_word = 'Root'
            else:
                parent_word = words_list[parent_index]
            child_index = index
            child_word = words_list[child_index]
            reletion_name = dp_tags[dp_info[index]['relate']]
            print("%s -----(%s)---- %s" % (parent_word, reletion_name, child_word))
            w.write("%s -----(%s)---- %s\n" % (parent_word, reletion_name, child_word))

        print('-------------------------语义依存分析结果打印----------------------------')
        w.write('-------------------------语义依存分析结果打印----------------------------' + '\n')
        for sdp_index in range(len(sdgp_info)):
            sdp_parent_index = sdgp_info[sdp_index]['parent']
            if sdp_parent_index == -1:
                sdp_parent_word = 'Root'
            else:
                sdp_parent_word = words_list[sdp_parent_index]
            sdp_child_index = sdgp_info[sdp_index]['id']
            sdp_child_word = words_list[sdp_child_index]
            if sdgp_info[sdp_index]['relate'] in sdp_tags:
                semantic_dp_name = sdp_tags[sdgp_info[sdp_index]['relate']]
            elif str(sdgp_info[sdp_index]['relate']).startswith('r'):
                main_relate = '' + str(sdgp_info[sdp_index]['relate'])[1:]
                semantic_dp_name = sdp_tags[main_relate] + '--反角色'
            elif str(sdgp_info[sdp_index]['relate']).startswith('d'):
                main_relate = '' + str(sdgp_info[sdp_index]['relate'])[1:]
                semantic_dp_name = sdp_tags[main_relate] + '--嵌套角色'
            else:
                semantic_dp_name = sdgp_info[sdp_index]['relate']
            print("%s(%s)-----%s-----%s(%s)" % (sdp_parent_word, postags_list[sdp_parent_index], semantic_dp_name, sdp_child_word,postags_list[sdp_child_index]))
            w.write("%s(%s)-----%s-----%s(%s)\n" % (sdp_parent_word, postags_list[sdp_parent_index], semantic_dp_name, sdp_child_word,postags_list[sdp_child_index]))
        print('===============================================================================================')
        w.write('==========================================================================================' + '\n\n\n')


def get_tags():
    cursor = conn.cursor()
    select_dp_tag = '''select tag, name from dependency_parse'''    # 依存句法分析
    select_sdp_tag = '''select tag, name from semantic_dependency_parse'''    # 语义依存分析分析
    cursor.execute(select_dp_tag)
    dp_results = cursor.fetchall()
    dp_tags = dict()
    for dp in dp_results:
        dp_tags.update({dp[0]: dp[1]})

    sdp_tags = dict()
    cursor.execute(select_sdp_tag)
    sdp_results = cursor.fetchall()
    for sdp in sdp_results:
        sdp_tags.update({sdp[0]: sdp[1]})
    return dp_tags, sdp_tags


if __name__ == '__main__':
    dp_tags, sdp_tags = get_tags()
    content_nlp("C:\\Users\\dhz1216\\Desktop\\test\\ltp-xunfei.txt", TEXT, dp_tags, sdp_tags)
