#!/usr/bin/env python
# coding=utf-8
from data_resource import conn
import re

FILE_PATH = "C:\\Users\\dhz\\Desktop\\template\\basic_template.txt"


# 基础模板生成
def basic_info_template_generate():
    cursor = conn.cursor()
    select_sql = '''select * from law'''
    cursor.execute(select_sql)
    law_info = cursor.fetchall()
    with open(FILE_PATH, "a") as w:
        for law in law_info:
            law_name = law[1]
            w.write(law_name + "的颁布年份？\n")
            w.write(law_name + "是什么时间颁布的？\n")
            w.write(law_name + "的发布时间？\n")
            w.write("什么时间颁布了" + law_name + "?\n")
            w.write(law_name + "是哪个机构颁布的？\n")
            w.write(law_name + "的颁布单位？\n")
            w.write(law_name + "的发布单位？\n")
            w.write(law_name + "的具体内容是什么？\n")
            w.write(law_name + "的第一条规定了什么？\n")


def bio_tag_generate(contents, tag_file_path):
    pattern_list = []
    pattern_list.append("(.*?)的颁布年份？")
    pattern_list.append("(.*?)是什么时间颁布的？")
    pattern_list.append("(.*?)的发布时间？")
    pattern_list.append("什么时间颁布了(.*?)")
    pattern_list.append("(.*?)是哪个机构颁布的？")
    pattern_list.append("(.*?)的颁布单位？")
    pattern_list.append("(.*?)的发布单位？")
    pattern_list.append("(.*?)的具体内容是什么？")
    pattern_list.append("(.*?)的第一条规定了什么？")
    for line in contents:
        with open(tag_file_path, "a") as w:
            line = line.replace("\n", "").strip()
            print(line)
            for pattern in pattern_list:
                match = re.findall(pattern, line)
                if len(match) > 0:
                    bio_content = match[0]
                    index = line.index(bio_content)
                    for i in range(len(line)):
                        if i >= index and i < index + len(bio_content):
                            if i == index:
                                w.write(line[i] + ' B-LAW\n')
                            else:
                                w.write(line[i] + ' I-LAW\n')
                        else:
                            w.write(line[i] + ' O\n')
                    break


def generate_data_set():
    contents = []
    with open(FILE_PATH, "r", encoding='gbk', errors='ignore') as f:
        line = f.readline()
        while line:
            line = line.replace("\n", "").strip()
            contents.append(line)
            line = f.readline()
    return contents


if __name__ == '__main__':
    # basic_info_template_generate()
    contents = generate_data_set()
    train_file = "C:\\Users\\dhz\\Desktop\\template\\law_train"
    test_file = "C:\\Users\\dhz\\Desktop\\template\\law_test"
    dev_file = "C:\\Users\\dhz\\Desktop\\template\\law_dev"
    bio_tag_generate(contents[0: 12000], train_file)
    bio_tag_generate(contents[12000: 16000], test_file)
    bio_tag_generate(contents[16000: 20000], dev_file)