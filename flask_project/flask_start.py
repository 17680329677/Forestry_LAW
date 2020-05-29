#!/usr/bin/env python
# coding=utf-8

from flask import Flask
from flask_project.questionAnswer import question_blueprint
from flask_project.search import search_blueprint
from flask_project.drawInfo import draw_blueprint

app = Flask(__name__)
app.register_blueprint(question_blueprint, url_prefix='/forestry_law_qa')
app.register_blueprint(search_blueprint, url_prefix='/forestry_law_search')
app.register_blueprint(draw_blueprint, url_prefix='/forestry_law_draw')


if __name__ == '__main__':
    app.run()