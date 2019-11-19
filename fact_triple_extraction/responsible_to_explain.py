#!/usr/bin/env python
# coding=utf-8
from fact_triple_extraction.aim_and_accord_extraction.xf_ltp_test import *
from data_resource import conn
import re


def get_correlation_sentences():
    cursor = conn.cursor()
    select_article_1_sql = '''select * from article_1'''
    select_article_2_sql = '''select * from article_2'''
    cursor.execute(select_article_1_sql)
    results_1 = cursor.fetchall()
    pattern_1 = "^本(办法|条例|规定|法|细则)(.*?)由(.*?)"
    count = 0
    output_file = "C:\\Users\\dhz1216\\Desktop\\test\\input_test.txt"
    ltp_output_file = "C:\\Users\\dhz1216\\Desktop\\test\\ltp-xunfei.txt"
    dp_tags, sdp_tags = get_tags()
    with open(output_file, "a") as w:
        for result in results_1:
            contents = list(filter(None, str(result[2]).strip().split('\n')))
            for content in contents:
                if re.findall(pattern_1, content.strip()):
                    count = count + 1
                    print(content.strip())
                    w.write(content.strip() + '\n')
                    if len(content.strip()) > 150:
                        continue
                    content_nlp(ltp_output_file, content.strip(), dp_tags, sdp_tags)

        cursor.execute(select_article_2_sql)
        results_2 = cursor.fetchall()
        for result in results_2:
            contents = list(filter(None, str(result[2]).strip().split('\n')))
            for content in contents:
                if re.findall(pattern_1, content.strip()):
                    count = count + 1
                    print(content.strip())
                    w.write(content.strip() + '\n')
                    if len(content.strip()) > 150:
                        continue
                    content_nlp(ltp_output_file, content.strip(), dp_tags, sdp_tags)
    print(count)


if __name__ == '__main__':
    get_correlation_sentences()