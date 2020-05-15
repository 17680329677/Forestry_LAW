#!/usr/bin/env python
# coding=utf-8
from flask import Blueprint, request, jsonify
from template_match.tf_idf import *
from py2neo import Graph,Node,Relationship
import requests
import re
question_blueprint = Blueprint('question_blueprint', __name__)

BASEURL = 'http://127.0.0.1:5051'
graph = Graph('http://localhost:7474', username='neo4j', password='123456')


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

        # 问句模板匹配及关系识别
        segment_results, template_results = get_template_and_segment(user_question)
        word, weight = calculate_tf_idf(segment_results)
        vec_dict = calculate_question_vec(segment_results, word, weight)
        match_template, relation_type = calculate_sim(vec_dict, template_results)
        print(entity, relation_type)
        query_cql = "match p=(e:forestry_subject)-[r:%s]->(obj) where e.name='%s' return obj" % (str(relation_type).upper(), entity)
        g = graph.run(query_cql).data()
        for res in g:
            print(res)
            print(res['obj'])
            print(res['obj']['name'])

        result = {'status': 200, 'data': {'entity_type': entity_type, 'entity': entity}}
        return jsonify(result)
    else:
        result = {'status': 0, 'message': '提问中未包含实体！'}
        return jsonify(result)