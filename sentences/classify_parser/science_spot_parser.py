# -*- coding : utf-8 -*-
# coding: utf-8
# 风景名胜管理条例相关法律法规的解析---并存入mysql数据库中做初步的格式化
import os
from data.property_collect import law_parse
from data_resource import conn


def science_spot_parser(file_path):
    dir_path = "C:\\Users\\dhz1216\\Desktop\\washing\\风景名胜"
    file_name = file_path.split("\\")[-1]
    cursor = conn.cursor()
    select_sql = "select id, name from law where text_name = %s"
    cursor.execute(select_sql, (file_name.split('.')[0]))
    law_id = cursor.fetchone()[0]
    count = 0
    with open(file_path, "r", encoding='gbk', errors='ignore') as f:
        line = f.readline()
        while line:
            if line.startswith('【法规全文】'):
                with open(dir_path + "\\" + file_name, "a") as w:
                    line = line.replace('【法规全文】', '')
                    # line = f.readline()
                    while line:
                        if len(line.lstrip().split('　')) > 1:
                            key_title = line.lstrip().split('　')[0]
                            value_content = line.lstrip().split('　')[1]
                            line = f.readline()
                            while line:
                                if len(line.lstrip().split('　')) <= 1:
                                    value_content = value_content + line.lstrip().split('　')[0]
                                    line = f.readline()
                                else:
                                    break
                            w.write(key_title + ':' + value_content + '\n')
                            insert_sql = "insert into law_content (law_id, p_key, p_content, law_class) " \
                                         "value (%s, %s, %s, %s)"
                            try:
                                cursor.execute(insert_sql, (law_id, key_title, value_content, '风景名胜'))
                                conn.commit()
                                count = count + 1
                                print('\033[1;37;40m' + file_name + ': PARSE SUCCESS' + '\033[0m')
                            except Exception as e:
                                print(e)
                                conn.rollback()
                                print('\033[1;32;41m' + file_name + ': PARSE FAILED---------' + '\033[0m')

                        else:
                            line = f.readline()
            else:
                line = f.readline()
    print('共插入：' + str(count) + '条')


def science_spot_filter(file_name):
    invalid_words = ['修订', '修正', '修改']
    if '风景名胜' not in file_name:
        return False
    for word in invalid_words:
        if word in file_name:
            return False
    return True


if __name__ == '__main__':
    dir_path = "C:\\Users\\dhz1216\\Desktop\\wenben"
    for file in os.listdir(dir_path):
        if science_spot_filter(file):
            file_path = dir_path + "\\" + file
            science_spot_parser(file_path)