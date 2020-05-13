#!/usr/bin/env python
# coding=utf-8
from flask import Blueprint, request, jsonify
import requests
question_blueprint = Blueprint('question_blueprint', __name__)

BASEURL = 'http://127.0.0.1:5051'


@question_blueprint.route('/question')
def question():
    param = request.args.get('question', '')
    url = BASEURL + '/ner?question=' + param
    r = requests.get(url)
    print(r.json())
    result = {'status': 200, 'data': param}
    return jsonify(result)