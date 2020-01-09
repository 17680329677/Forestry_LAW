#!/usr/bin/env python
# coding=utf-8
from data_resource import conn
import re


def query_and_match():
    select_1_sql = '''select * from article_1_sentence'''
    select_2_sql = '''select * from article_2_sentence'''
    punishment_pattern = "(.*)违反(.*)[处|处以](.*)"
    punishment_pattern_1 = "(.*)违反本(.*)第(.*)规定(.*)[处|处以](.*)"
    cursor = conn.cursor()
    cursor.execute(select_1_sql)
    results_1 = cursor.fetchall()
    cursor.execute(select_2_sql)
    results_2 = cursor.fetchall()
    results = results_1 + results_2
    count = 0
    output_file = "C:\\Users\\dhz\\Desktop\\template\\punishment_content.txt"
    with open(output_file, "a") as w:
        for res in results:
            content = res[3]
            pattern_res = re.findall(punishment_pattern_1, content)
            if len(pattern_res) > 0:
                count = count + 1
                content = str(content).strip().replace("\n", "")
                print(content, res[0])
                print(pattern_res)
                print("==================================================================")
                # w.write(content + '\n\n')
    print(count)


if __name__ == '__main__':
    query_and_match()