#!/usr/bin/env python
# coding=utf-8
from flask import Blueprint, request, jsonify
from template_match.tf_idf import *
from data_resource import conn
from py2neo import Graph,Node,Relationship
import requests
import re
question_blueprint = Blueprint('question_blueprint', __name__)

BASEURL = 'http://127.0.0.1:5051'
graph = Graph('http://127.0.0.1:7474', username='neo4j', password='123456')


@question_blueprint.route('/question')
def question():
    question = request.args.get('question', '')
    url = BASEURL + '/ner?question=' + question
    r = requests.get(url)
    result_json = r.json()
    if len(result_json['data']['entities']) > 0:
        entity_type = result_json['data']['entities'][0]['type']
        entity = result_json['data']['entities'][0]['word']
        valid_entity_list = re.findall(r'[\u4e00-\u9fa5]', entity)
        entity = ''.join(valid_entity_list)
        user_question = str(question).replace(entity, ' $' + entity_type)

        # 实体链接
        # query_subject = "match p=(a:forestry_subject) return a.name"
        # entity_list = graph.run(query_subject).data()
        # sim_dict = {}
        # for e in entity_list:
        #     sim_tmp = model.similarity(e['a.name'], entity)
        #     sim_dict.update({e['a.name']: sim_tmp})
        # sim_res = sorted(sim_dict.items(), key=lambda x: x[1], reverse=True)
        # for s in sim_res:
        #     print(s)

        # 问句模板匹配及关系识别
        segment_results, template_results = get_template_and_segment(user_question)
        word, weight = calculate_tf_idf(segment_results)
        vec_dict = calculate_question_vec(segment_results, word, weight)
        match_template, relation_type = calculate_sim(vec_dict, template_results)
        print(entity, relation_type)
        query_cql = "match p=(e:forestry_subject)-[r:%s]->(obj) where e.name='%s' return obj" % (str(relation_type).upper(), entity)
        query_res = graph.run(query_cql).data()

        relation_object_list = []
        origin_dict = {}
        if len(query_res) > 0:
            for res in query_res:
                relation_object_list.append(res['obj']['name'])
                law_id = res['obj']['law_id']
                chapter_id = res['obj']['chapter_id']
                sentence_id = res['obj']['sentence_id']
                origin_dict.update({law_id: [chapter_id, sentence_id]})

            origin_info = origin_info_pack(origin_dict)

            data = {
                'entity_type': entity_type,
                'entity': entity,
                'relation_type': relation_type,
                'relation_object': relation_object_list,
                'origin_info': origin_info
            }
            result = {'status': 200, 'data': data}
            return jsonify(result)

        else:
            result = {'status': 0, 'message': '暂时无法回答该问题！'}
            return jsonify(result)
    else:
        result = {'status': 0, 'message': '提问中未包含实体！'}
        return jsonify(result)


def origin_info_pack(origin_dict):
    cursor = conn.cursor()
    select_law = "select name from law where id = %s"
    select_chapter = "select * from chapter where id = %s"
    select_article_1 = "select * from article_1 where id = %s"
    select_article_2 = "select * from article_2 where id = %s"
    select_sentence_1 = "select * from article_1_sentence where id = %s"
    select_sentence_2 = "select * from article_2_sentence where id = %s"

    origin_info = []

    for law_id in origin_dict:
        print(origin_dict[law_id])
        cursor.execute(select_law, (law_id, ))
        law_name = cursor.fetchone()[0]

        chapter_id = origin_dict[law_id][0]
        sentence_id = origin_dict[law_id][1]

        if int(chapter_id) > 0:
            # 获取章信息
            cursor.execute(select_chapter, (chapter_id, ))
            chapter_res = cursor.fetchone()
            chapter_key = chapter_res[1]
            chapter_name = chapter_res[2]
            chap_data = {'chapter_key': chapter_key, 'chapter_name': chapter_name}

            # 获取条款信息
            cursor.execute(select_sentence_1, (sentence_id, ))
            sentence_res = cursor.fetchone()
            article1_id = sentence_res[1]
            is_single = sentence_res[2]
            origin_content = sentence_res[3]

            cursor.execute(select_article_1, (article1_id, ))
            article_res = cursor.fetchone()
            article_key = article_res[1]
            article_content = article_res[2]
            article_data = {'article_key': article_key,
                            'article_content': article_content,
                            'origin_content': origin_content}

            dict_temp = {
                'law_id': law_id,
                'law_name': law_name,
                'chap_data': chap_data,
                'article_data': article_data
            }
            origin_info.append(dict_temp)

        else:
            chap_data = {'chapter_key': '-', 'chapter_name': '-'}

            # 获取条款信息
            cursor.execute(select_sentence_2, (sentence_id,))
            sentence_res = cursor.fetchone()
            article2_id = sentence_res[1]
            is_single = sentence_res[2]
            origin_content = sentence_res[3]

            cursor.execute(select_article_2, (article2_id,))
            article_res = cursor.fetchone()
            article_key = article_res[1]
            article_content = article_res[2]
            article_data = {'article_key': article_key,
                            'article_content': article_content,
                            'origin_content': origin_content}

            dict_temp = {
                'law_id': law_id,
                'law_name': law_name,
                'chap_data': chap_data,
                'article_data': article_data
            }
            origin_info.append(dict_temp)

    return origin_info
