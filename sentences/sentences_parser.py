# -*- coding : utf-8 -*-
# coding: utf-8
import os
from data.property_collect import law_parse
import pymysql


conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='123456',
    database='forestry_law',
    charset='utf8'
)


def save_to_mysql(file_path):
    law_content = law_parse(file_path)
    text_name = file_path.split('\\')[-1].split('.')[0]
    name = law_content['name']
    status = law_content['status']
    location_dep = law_content['location_dep']
    year = law_content['year']
    pub_unit = law_content['pub_unit']
    pub_time = law_content['pub_time']
    implement_time = law_content['implement_time']
    classify = law_content['classify']
    key_word = law_content['key_word']
    content_id = law_content['content_id']
    credit_line = law_content['credit_line']
    catalogue = law_content['catalogue']

    cursor = conn.cursor()
    sql = "insert into law (text_name, name, status, location_dep, year, pub_unit, pub_time, implement_time, " \
          "classify, key_word, content_id, credit_line, catalogue) value (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    if "自然科学" in text_name or "自然科学" in name:
        return
    else:
        try:
            cursor.execute(sql, (text_name, name, status, location_dep, year, pub_unit, pub_time, implement_time, classify, key_word, content_id, credit_line, catalogue))
            conn.commit()
            print('\033[1;37;40m' + text_name + ': OK' + '\033[0m')
        except Exception as e:
            print('\033[1;32;41m' + text_name + ': ' + str(e) + '\033[0m')
            conn.rollback()


def sentences_parser(file_path):
    with open(file_path, "r", encoding='gbk', errors='ignore') as f:
        line = f.readline()
        num = 1
        while line:
            if line.startswith('【法规全文】'):
                line = line.replace('【法规全文】', '')
                print(str(num) + ': ' + line)
                num = num + 1
                line = f.readline()
                while line:
                    print(str(num) + ': ' + line)
                    num = num + 1
                    line = f.readline()
            else:
                line = f.readline()


if __name__ == '__main__':
    # save_to_mysql(dir_path + "\\" + file)
    dir_path = "C:\\Users\\dhz1216\\Desktop\\wenben"
    # for file in os.listdir(dir_path):
    #     if count < 1:
    #         law_content = law_parse(dir_path + "\\" + file)
    #         print(law_content['name'])
    #         content = law_content['content']
    #         print(content)
    #         count = count + 1
    sentences_parser(dir_path + "\\本溪市野生鸟类保护办法.txt")