#!/usr/bin/env python
# coding=utf-8
from data_resource import conn
from pyltp import SentenceSplitter
# from  fact_triple_extraction.fact_triple_extraction import extraction_start


def create_test_txt():
    cursor = conn.cursor()
    select_sql = '''select * from article_1_sentence where is_single = 0 limit 0, 500'''
    cursor.execute(select_sql)
    sentences = cursor.fetchall()
    with open(r"C:\Users\dhz1216\Desktop\test\law_input.txt", "a") as w:
        for sentence in sentences:
            contents = SentenceSplitter.split(sentence[3])
            for content in contents:
                if content is not None and content != '' and '：' in content:
                    w.write(str(content).strip() + '\n')


if __name__ == '__main__':
    create_test_txt()
