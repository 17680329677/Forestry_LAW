#!/usr/bin/env python
# coding=utf-8
from pyltp import SentenceSplitter
from data_resource import conn


def get_article_1_complex_content():
    select_sql = '''select * from article_1_sentence where is_single = 0 limit 50'''
    cursor = conn.cursor()
    cursor.execute(select_sql)
    complex_contents = cursor.fetchall()
    result = []
    for c_content in complex_contents:
        content_list = SentenceSplitter.split(str(c_content[3]).strip())
        is_valid = False
        temp_list = []
        for content in content_list:
            temp_list.append(str(content.strip()))
            if '：' in content and len(content) > 6:
                is_valid = True
        if is_valid:
            result.append(temp_list)
    return result


def get_article_2_complex_content():
    pass


if __name__ == '__main__':
    content_list = get_article_1_complex_content()
