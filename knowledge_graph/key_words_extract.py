# -*- coding : utf-8 -*-
# coding: utf-8
# 抽取法律法规文本的关键词
from jieba import analyse
from data.property_collect import law_parse
from data_resource import conn


def key_words_extract():
    file_path = "C:\\Users\\dhz1216\\Desktop\\wenben\\安徽省湿地保护条例.txt"
    law = law_parse(file_path)
    text = law['content']
    textrank = analyse.textrank
    key_words_textrank = textrank(text, topK=5, withWeight=False, allowPOS=('n', 'ns', 'vn', 'v', 'nz'))
    for word in key_words_textrank:
        print(word + '\n')


if __name__ == '__main__':
    key_words_extract()