#!/usr/bin/env python
# coding=utf-8

from flask import Flask
from flask_project.questionAnswer import question_blueprint

app = Flask(__name__)
app.register_blueprint(question_blueprint, url_prefix='/forestry_law_qa')


if __name__ == '__main__':
    app.run()