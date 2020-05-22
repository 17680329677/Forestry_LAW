#!/usr/bin/env python
# coding=utf-8
from flask import Blueprint, request, jsonify
from pyltp import Segmentor
from data_resource import conn

MODEL_DIR_PATH = "F:\\ltp_data_v3.4.0\\"
SEGMENTOR_MODEL = MODEL_DIR_PATH + "cws.model"  # LTP分词模型库

segmentor = Segmentor()  # 初始化分词实例
segmentor.load(SEGMENTOR_MODEL)     # 加载分词模型库

search_blueprint = Blueprint('search_blueprint', __name__)


@search_blueprint.route('/search')
def search():
    content = request.args.get('content', '')
    search_words = list(segmentor.segment(content))
    cursor = conn.cursor()
    select_sql = '''select name, type from law'''
    cursor.execute(select_sql)
    law_info_dict = {}
    law_results = cursor.fetchall()
    for law in law_results:
        law_name = law[0]
        law_name_words = list(segmentor.segment(law_name))
        match_count = 0
        for w in law_name_words:
            if w in search_words:
                match_count = match_count + 1
        if (len(search_words) <= 3 and match_count >= 1) or match_count >= 3:
            law_info_dict.update({law[0]: match_count})

    if len(law_info_dict) > 0:
        match_res = sorted(law_info_dict.items(), key=lambda x: x[1], reverse=True)
        result = {'status': 200, 'data': match_res}
    else:
        result = {'status': 0, 'message': '未找到相关法律法规！'}
    return result