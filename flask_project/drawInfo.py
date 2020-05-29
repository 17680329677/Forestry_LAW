#!/usr/bin/env python
# coding=utf-8
from flask import Blueprint, request, jsonify
from py2neo import Graph,Node,Relationship
import requests
import re

draw_blueprint = Blueprint('draw_blueprint', __name__)

graph = Graph('http://127.0.0.1:7474', username='neo4j', password='123456')


@draw_blueprint.route('/draw_info')
def get_draw_info():
    entity = request.args.get('entity', '')
    query_cql = "match (e:forestry_subject)-[r]->(obj) where e.name='%s' return r,obj" % (entity, )
    query_res = graph.run(query_cql).data()
    rel_pattern = ":(.*) {}"
    draw_info_dict = {}
    if len(query_res) > 0:
        for res in query_res:
            rel_res = re.search(rel_pattern, str(res['r']), re.M | re.I)
            if rel_res:
                rel = rel_res.groups(1)[0]
                obj_tmp = res['obj']['name']
                if rel not in draw_info_dict:
                    draw_info_dict.update({rel: []})
                    draw_info_dict[rel].append(obj_tmp)
                else:
                    draw_info_dict[rel].append(obj_tmp)
    if len(draw_info_dict) > 0:
        result = {'status': 200, 'data': draw_info_dict}
    else:
        result = {'status': 0, 'message': '未找到相关实体信息！'}
    return jsonify(result)