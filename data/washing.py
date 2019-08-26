# -*- coding : utf-8 -*-
# coding: utf-8
import os


# 将文本中的每个法律文本全部按照标题提取到不同的txt中待下一步处理，key_words用于过滤和林业领域无关的法律
def parse_content(file):
    dir_path = "C:\\Users\\dhz1216\\Desktop\\wenben\\"
    content = []

    with open(file, "r", encoding='gbk', errors='ignore') as f:
        line = f.readline()
        law_name = 'null'
        while line:
            if line.startswith('【法规全文】'):
                content.append(line)
                line = f.readline()
                while line:
                    if line.startswith("【"):
                        if not forestry_law_filter(law_name):
                            content = []
                            break
                        law_name = invalid_char_filter(law_name)
                        path_name = dir_path + law_name + ".txt"
                        with open(path_name, "a") as w:
                            for c in content:
                                w.write(c)
                        content = []
                        break
                    content.append(line)
                    line = f.readline()
            line = line
            if line.startswith("【法规名称】"):
                law_name = line.split('】')[-1].strip()
            content.append(line)
            line = f.readline()

    path_name = dir_path + law_name + ".txt"
    with open(path_name, "a") as w:
        for c in content:
            w.write(c)


# 判断法律是否和林业领域相关
def forestry_law_filter(law_name):
    law_name = str(law_name)
    key_words = ['木', '林', '森', '草', '苗', '绿', '生态', '资源', '自然', '环境', '流域', '湖泊',
                 '水土', '湿地', '风景', '野生', '动物', '种子', '保护区', '多样性']
    for word in key_words:
        if word in law_name:
            return True
    return False


# 过滤名称中的非法字符
def invalid_char_filter(law_name):
    res = law_name.translate({ord(c): None for c in '/:：*?？"<>'})
    return res


if __name__ == '__main__':
    dir_path = "C:\\Users\\dhz1216\\Desktop\\原始数据"
    for file in os.listdir(dir_path):
        parse_content(dir_path + "\\" + file)
