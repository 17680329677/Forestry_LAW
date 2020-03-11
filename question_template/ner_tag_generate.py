#!/usr/bin/env python
# coding=utf-8
from data_resource import conn
import re

Cursor = conn.cursor()


# 1. 部门单位等
# 2. 保护区、风景区
# 3. 林业名词
def forestry_entity_classify():
    unit_words = ['部门', '单位', '企业', '组织', '委', '局', '政府', '机构',  '委员会']
    park_words = ['保护区', '景区', '旅游区', '园']
    all_subject = []
    unit_list = []
    park_list = []
    select_sql = '''select subject from forestry_subject'''
    Cursor.execute(select_sql)
    results = Cursor.fetchall()
    for res in results:
        all_subject.append(res[0])
        for word in unit_words:
            if str(res[0]).endswith(word):
                unit_list.append(res[0])
        for word in park_words:
            if str(res[0]).endswith(word):
                park_list.append(res[0])
    forestry_list = list(set(all_subject) - set(unit_list) - set(park_list))
    return unit_list, park_list, forestry_list


def entity_list_wash(unit_list, park_list, forestry_list):
    new_unit_list = []
    new_park_list = []
    new_forestry_list = []
    for index in range(len(unit_list)):
        unit = str(unit_list[index])
        if unit.startswith('、'):
            unit = unit[1:]
        if '、' in unit or '（' in unit or '，' in unit or '。' in unit or '《' in unit or '(' in unit:
            continue
        else:
            new_unit_list.append(unit)
    for park in park_list:
        for word in str(park).split('、'):
            if word.endswith('区') or word.endswith('公园'):
                new_park_list.append(word)
    new_new_park_list = []
    for park in new_park_list:
        if '、' in park or '（' in park or '，' in park or '。' in park or '《' in park or '(' in park:
            continue
        else:
            new_new_park_list.append(park)
    chinese_seg_pattern = "[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b]+"
    chinese_pattern = "[\\u4e00-\\u9fa5]+"
    num_pattern = "[0-9].*"
    article_pattern = "第(.*?)"
    invalid_word = ['１', '２', '３', '４', '５', '６', '７', '８', '９', '０']
    for entity in forestry_list:
        if re.search(chinese_seg_pattern, entity, re.M | re.I):
            continue
        elif '(' in entity or ':' in entity:
            continue
        elif re.search(num_pattern, entity, re.M | re.I):
            continue
        elif re.search(article_pattern, entity, re.M | re.I):
            continue
        elif not re.search(chinese_pattern, entity, re.M | re.I):
            continue
        elif str(entity).startswith('在'):
            continue
        else:
            n = 0
            while n < len(invalid_word):
                if invalid_word[n] in entity:
                    break
                n = n + 1
            if n == len(invalid_word):
                new_forestry_list.append(entity)
    return new_unit_list, new_new_park_list, new_forestry_list


def tag_generate(unit_list, park_list, forestry_list, output_file):
    unit_template_list = ['%s的职责是什么？', '%s有什么职责？', '%s有什么责任？', '%s有什么权利？', '%s有什么义务？', '%s有什么权利与义务？']
    park_template_list = ['%s有什么权利与义务？', '%s有什么禁止的行为？', '在%s有什么被禁止的行为？', '%s的定义是什么？',
                          '%s有什么权利？', '%s有什么义务？']
    normal_template_list = ['%s是什么？', '%s的职责是什么？', '%s包括什么？', '%s的流程是怎么样的？', '%s的依据是什么？',
                            '%s的权利与义务是什么？', '%s有什么权利？', '%s有什么义务？']
    with open(output_file, "a") as w:
        for unit in unit_list:
            for template in unit_template_list:
                question = template % unit
                start = question.index(unit)
                end = start + len(unit)
                for index in range(len(question)):
                    if index >= start and index < end:
                        if index == start:
                            w.write(question[index] + ' B-UNIT\n')
                        else:
                            w.write(question[index] + ' I-UNIT\n')
                    else:
                        w.write(question[index] + ' O\n')

        for park in park_list:
            for template in park_template_list:
                question = template % park
                start = question.index(park)
                end = start + len(park)
                for index in range(len(question)):
                    if index >= start and index < end:
                        if index == start:
                            w.write(question[index] + ' B-PARK\n')
                        else:
                            w.write(question[index] + ' I-PARK\n')
                    else:
                        w.write(question[index] + ' O\n')

        for forestry in forestry_list:
            for template in normal_template_list:
                question = template % forestry
                start = question.index(forestry)
                end = start + len(forestry)
                for index in range(len(question)):
                    if index >= start and index < end:
                        if index == start:
                            w.write(question[index] + ' B-FOREST\n')
                        else:
                            w.write(question[index] + ' I-FOREST\n')
                    else:
                        w.write(question[index] + ' O\n')


def tag_generate1(unit_list, park_list, forestry_list, output_file):
    unit_template_list = ['%s的职责是什么？']
    park_template_list = ['%s有什么禁止的行为？', '在%s有什么被禁止的行为？']
    normal_template_list = ['%s是什么？',  '%s包括什么？']
    with open(output_file, "a") as w:
        for unit in unit_list:
            for template in unit_template_list:
                question = template % unit
                start = question.index(unit)
                end = start + len(unit)
                for index in range(len(question)):
                    if index >= start and index < end:
                        if index == start:
                            w.write(question[index] + ' B-UNIT\n')
                        else:
                            w.write(question[index] + ' I-UNIT\n')
                    else:
                        w.write(question[index] + ' O\n')

        for park in park_list:
            for template in park_template_list:
                question = template % park
                start = question.index(park)
                end = start + len(park)
                for index in range(len(question)):
                    if index >= start and index < end:
                        if index == start:
                            w.write(question[index] + ' B-PARK\n')
                        else:
                            w.write(question[index] + ' I-PARK\n')
                    else:
                        w.write(question[index] + ' O\n')

        for forestry in forestry_list:
            for template in normal_template_list:
                question = template % forestry
                start = question.index(forestry)
                end = start + len(forestry)
                for index in range(len(question)):
                    if index >= start and index < end:
                        if index == start:
                            w.write(question[index] + ' B-FOREST\n')
                        else:
                            w.write(question[index] + ' I-FOREST\n')
                    else:
                        w.write(question[index] + ' O\n')


def tag_generate2(forestry_list, output_file):
    # unit_template_list = ['%s的职责是什么？']
    # park_template_list = ['%s有什么禁止的行为？', '在%s有什么被禁止的行为？']
    normal_template_list = ['%s的定义是什么？',  '%s包括什么？', '%s的职责是什么？',
                            '%s有什么权利和义务？', '在%s有什么被禁止的行为？']
    with open(output_file, "a") as w:
        for forestry in forestry_list:
            B_name = ' B-FOREST'
            I_name = ' I-FOREST'
            for template in normal_template_list:
                question = template % forestry
                start = question.index(forestry)
                end = start + len(forestry)
                for index in range(len(question)):
                    if index >= start and index < end:
                        if index == start:
                            w.write(question[index] + B_name + '\n')
                        else:
                            w.write(question[index] + I_name + '\n')
                    else:
                        w.write(question[index] + ' O\n')


if __name__ == '__main__':
    unit_list, park_list, forestry_list = forestry_entity_classify()
    unit_list, park_list, forestry_list = entity_list_wash(unit_list, park_list, forestry_list)
    # print(len(unit_list))   # 3000 1800 600 600
    # print(len(park_list))   # 250  150 50 50
    # print(len(forestry_list))   # 12000 7200 2400 2400
    # tag_generate(unit_list[2400:3000],
    #              park_list[200:250],
    #              forestry_list[15000:15600],
    #              r"C:\Users\dhz\Desktop\template\law_test")

    # tag_generate1(unit_list[2400:3000],
    #               park_list[200:250],
    #               forestry_list[9600:12000],
    #               r"C:\Users\dhz\Desktop\template\law_test1")

    # forestry_list = list(set(forestry_list).union(set(park_list)).union(set(unit_list)))
    # print(len(forestry_list))
    tag_generate2(forestry_list[9600:11600], r"C:\Users\dhz\Desktop\template\law_test2")