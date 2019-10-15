# -*- coding : utf-8 -*-
# coding: utf-8
# 按照不同的层次划分类别进行文本分割和解析
import os
import re
from data_resource import conn


def invalid_filter(file_name):     # 过滤修订法律法规
    invalid_words = ['修改', '修正', '修订']
    for word in invalid_words:
        if word in file_name:
            return False
    return True


def is_chapter_article(file_path):      # 判断法规正文是否是按照--“第xx条”进行分段的
    with open(file_path, "r", encoding='gbk', errors='ignore') as f:
        line = f.readline()
        count_level = 0
        while line:
            if line.startswith('【法规全文】'):
                line = line.replace('【法规全文】', '')
                while line:
                    if '第一条' in line or '第二条' in line:      # 至少拥有两个条款才算作此类
                        count_level = count_level + 1
                        if count_level > 1:
                            return True
                        else:
                            line = f.readline()
                    else:
                        line = f.readline()
            else:
                line = f.readline()
    return False


def is_one_two_article(file_path):      # 判断法规正文是否是按照--“一、二、...”进行分段的
    with open(file_path, "r", encoding='gbk', errors='ignore') as f:
        line = f.readline()
        count_invalid = 0   # 记录包含非此类目录关键词的数量，超过1则返回False
        count_level = 0     # 记录包含此类目录关键词的数量，超过1则返回True
        while line:
            if line.startswith('【法规全文】'):
                line = line.replace('【法规全文】', '')
                while line:
                    if '第一条' in line or '第二条' in line:
                        count_invalid = count_invalid + 1
                        if count_invalid > 1:
                            return False
                        else:
                            line = f.readline()
                    elif '一、' in line or '二、' in line:
                        count_level = count_level + 1
                        if count_level > 1:
                            return True
                        else:
                            line = f.readline()
                    else:
                        line = f.readline()
            else:
                line = f.readline()
    return False


def chapter_article_parser(file_path):      # "第xx条"类文本解析与格式化
    file_name = file_path.split('\\')[-1]
    write_path = "C:\\Users\\dhz1216\\Desktop\\washing\\第一类\\" + file_name
    # 查询法规基本数据库中该文本的id和对应的法规名称
    law_name = file_name.split('.')[0]
    try:
        cursor = conn.cursor()
        select_sql = "select id from law where text_name = %s"
        cursor.execute(select_sql, (file_name.split('.')[0]))
        law_id = cursor.fetchone()[0]
    except Exception as e:
        print(e)
        return

    with open(file_path, "r", encoding='gbk', errors='ignore') as f:
        line = f.readline()
        pattern = re.compile("第(.*?)(?:章|条)")
        while line:
            if line.startswith('【法规全文】'):
                line = line.replace('【法规全文】', '')
                with open(write_path, "a") as w:
                    while line:
                        match = pattern.match(line.lstrip())
                        if match:
                            p_key = match.group()
                            p_content = line.replace(match.group(), '').lstrip()
                            line = f.readline()
                            while line:
                                match = pattern.match(line.lstrip())
                                if not match:
                                    p_content = p_content + line
                                    line = f.readline()
                                else:
                                    break
                            w.write(p_key + ':  ' + p_content + '\n')
                            insert_sql = "insert into law_content_parse (law_id, p_key, p_content, law_name) " \
                                         "value (%s, %s, %s, %s)"
                            try:
                                cursor.execute(insert_sql, (law_id, p_key, p_content, law_name))
                                conn.commit()
                                print(file_name + ': PARSE SUCCESS')
                            except Exception as e:
                                print(e)
                                conn.rollback()
                                print('\033[1;32;41m' + file_name + ': PARSE FAILED---------' + '\033[0m')
                        else:
                            line = f.readline()
            else:
                line = f.readline()


def is_cotain_one_two_title(line):
    title_words = ['一、', '二、', '三、', '四、', '五、', '六、', '七、', '八、', '九、', '十、', '十一、',
                   '十二、', '十三、', '十四、', '十五、', '十六、', '十七', '十八、', '十九、', '二十、']
    line = line.lstrip()
    for word in title_words:
        if word in line and line.index(word) == 0:
            return word
        else:
            continue
    return None


def one_two_article_parser(file_path):
    file_name = file_path.split('\\')[-1]
    write_path = "C:\\Users\\dhz1216\\Desktop\\washing\\第二类\\" + file_name

    # 查询法规基本数据库中该文本的id和对应的法规名称
    law_name = file_name.split('.')[0]
    try:
        cursor = conn.cursor()
        select_sql = "select id from law where text_name = %s"
        cursor.execute(select_sql, (file_name.split('.')[0]))
        law_id = cursor.fetchone()[0]
    except Exception as e:
        print(e)
        return

    with open(file_path, "r", encoding='gbk', errors='ignore') as f:
        line = f.readline()
        while line:
            if line.startswith('【法规全文】'):
                line = line.replace('【法规全文】', '')
                with open(write_path, "a") as w:
                    while line:
                        if is_cotain_one_two_title(line) is not None:
                            p_key = is_cotain_one_two_title(line)
                            p_content = line.lstrip().replace(p_key, '')
                            line = f.readline()
                            while line:
                                if is_cotain_one_two_title(line) is None:
                                    p_content = p_content + line
                                    line = f.readline()
                                else:
                                    break
                            w.write(p_key + ': ' + p_content + '\n')
                            insert_sql = "insert into law_content_parse (law_id, p_key, p_content, law_name) " \
                                         "value (%s, %s, %s, %s)"
                            try:
                                cursor.execute(insert_sql, (law_id, p_key, p_content, law_name))
                                conn.commit()
                                print(file_name + ': PARSE SUCCESS')
                            except Exception as e:
                                print(e)
                                conn.rollback()
                                print('\033[1;32;41m' + file_name + ': PARSE FAILED---------' + '\033[0m')
                        else:
                            line = f.readline()
            else:
                line = f.readline()
    pass


def is_other_class(file_path):      # 判断是否是除上述两类文本以为的文本
    if not is_chapter_article(file_path) and not is_one_two_article(file_path):
        return True
    else:
        return False


# if __name__ == '__main__':      # 两类主要文本解析
#     dir_path = "C:\\Users\\dhz1216\\Desktop\\wenben"
#     count = 0
#     for file in os.listdir(dir_path):
#         file_path = dir_path + "\\" + file
#         if is_one_two_article(file_path) and invalid_filter(file_path.split('.')[0]):
#             count = count + 1
#             # chapter_article_parser(file_path)     # 第一类文本解析
#             one_two_article_parser(file_path)       # 第二类文本解析
#     print(count)


if __name__ == '__main__':      # 统计两类之外类别的文本
    dir_path = "C:\\Users\\dhz1216\\Desktop\\wenben"
    count = 0
    for file in os.listdir(dir_path):
        file_path = dir_path + "\\" + file
        if is_other_class(file_path) and invalid_filter(file_path.split('.')[0]):
            count = count + 1
            print(file)
    print(count)