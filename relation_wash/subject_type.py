# -*- coding : utf-8 -*-
# coding: utf-8
from data_resource import conn
import random
import re

def subject_type_classify():
    park_words = ['公园', '保护区', '区域', '名胜区', '风景区', '景区', '地区', '区', '湿地',
                  '范围', '基地', '山', '湖', '景观']
    org_words = ['政府', '机构', '部门', '企业', '局', '厅', '单位', '指挥部', '机关', '管委会',
                 '委员会', '公司', '站', '部', '委', '办']
    park_list = []
    org_list = []
    cursor = conn.cursor()
    select_sql = '''select * from new_forestry_subject_final'''
    update_sql = '''update new_forestry_subject_final set subject_type = %s where id = %s'''
    cursor.execute(select_sql)
    results = cursor.fetchall()
    for res in results:
        id = res[0]
        subject = res[1]
        subject_type = ''
        for p_word in park_words:
            if str(subject).endswith(p_word):
                subject_type = 'PARK'
                park_list.append(subject)

        for o_word in org_words:
            if str(subject).endswith(o_word):
                subject_type = 'ORG'
                org_list.append(subject)

        if subject_type == '':
            subject_type = 'FORESTRY'

        cursor.execute(update_sql, (subject_type, id))
        conn.commit()
        print(subject, 'update success!')


def get_subject_list(forestry_num, park_num, org_num):
    select_sql = '''select * from new_forestry_subject_final where subject_type = %s'''
    cn_reg = '^[\u4e00-\u9fa5]+$'
    cursor = conn.cursor()
    cursor.execute(select_sql, ('FORESTRY'))
    forestry_results = cursor.fetchall()
    forestry_results = forestry_results[24000:]
    cursor.execute(select_sql, ('PARK'))
    park_results = cursor.fetchall()
    park_results = park_results[1400:]
    cursor.execute(select_sql, ('ORG'))
    org_results = cursor.fetchall()
    org_results = org_results[5000:]

    forestry_count = 0
    park_count = 0
    org_count = 0
    forestry_list = []
    park_list = []
    org_list = []
    subject_dict = {}
    for forestry in forestry_results:
        subject = forestry[1]
        if str(subject).startswith('(') or str(subject).startswith('（') or str(subject).startswith('、'):
            subject = subject[1:]
        if str(subject).endswith('，') or str(subject).endswith('、') or str(subject).endswith('；'):
            subject = subject[:-1]
        if re.search(cn_reg, subject):
            forestry_count = forestry_count + 1
            if forestry_count <= forestry_num:
                forestry_list.append(subject)
                subject_dict.update({subject: 'forest'})

    for park in park_results:
        subject = park[1]
        if str(subject).startswith('(') or str(subject).startswith('（') or str(subject).startswith('、'):
            subject = subject[1:]
        if str(subject).endswith('，') or str(subject).endswith('、') or str(subject).endswith('；'):
            subject = subject[:-1]

        if re.search(cn_reg, subject):
            park_count = park_count + 1
            if park_count <= park_num:
                park_list.append(subject)
                subject_dict.update({subject: 'park'})

    for org in org_results:
        subject = org[1]
        if str(subject).startswith('(') or str(subject).startswith('（') or str(subject).startswith('、'):
            subject = subject[1:]
        if str(subject).endswith('，') or str(subject).endswith('、') or str(subject).endswith('；'):
            subject = subject[:-1]

        if re.search(cn_reg, subject):
            org_count = org_count + 1
            if org_count <= org_num:
                org_list.append(subject)
                subject_dict.update({subject: 'org'})

    print(len(forestry_list))
    print(len(park_list))
    print(len(org_list))
    subject_list = []
    for i in sorted(subject_dict):
        subject_list.append(tuple((i, subject_dict[i])))
    return forestry_list, park_list, org_list, subject_list


def tag_generate(unit_list, park_list, forestry_list, subject_list, output_file):
    unit_template_list = ['%s的职责是什么？', '%s有什么职责？', '%s有什么责任？', '%s有什么权利？', '%s有什么义务？', '%s有什么权利与义务？']
    park_template_list = ['%s有什么权利与义务？', '%s有什么禁止的行为？', '在%s有什么被禁止的行为？', '%s的定义是什么？',
                          '%s有什么权利？', '%s有什么义务？']
    normal_template_list = ['%s是什么？', '%s的职责是什么？', '%s包括什么？', '%s的依据是什么？',
                            '%s的权利与义务是什么？', '%s有什么权利？', '%s有什么义务？']

    with open(output_file, "a") as w:
        for subject in subject_list:
            if subject[1] == 'org':
                for template in unit_template_list:
                    question = template % subject[0]
                    start = question.index(subject[0])
                    end = start + len(subject[0])
                    for index in range(len(question)):
                        if index >= start and index < end:
                            if index == start:
                                w.write(question[index] + ' B-ORG\n')
                            else:
                                w.write(question[index] + ' I-ORG\n')
                        else:
                            w.write(question[index] + ' O\n')

            elif subject[1] == 'park':
                for template in park_template_list:
                    question = template % subject[0]
                    start = question.index(subject[0])
                    end = start + len(subject[0])
                    for index in range(len(question)):
                        if index >= start and index < end:
                            if index == start:
                                w.write(question[index] + ' B-PARK\n')
                            else:
                                w.write(question[index] + ' I-PARK\n')
                        else:
                            w.write(question[index] + ' O\n')

            elif subject[1] == 'forest':
                for template in normal_template_list:
                    question = template % subject[0]
                    start = question.index(subject[0])
                    end = start + len(subject[0])
                    for index in range(len(question)):
                        if index >= start and index < end:
                            if index == start:
                                w.write(question[index] + ' B-FOREST\n')
                            else:
                                w.write(question[index] + ' I-FOREST\n')
                        else:
                            w.write(question[index] + ' O\n')

    # with open(output_file, "a") as w:
    #     for unit in unit_list:
    #         for template in unit_template_list:
    #             question = template % unit
    #             start = question.index(unit)
    #             end = start + len(unit)
    #             for index in range(len(question)):
    #                 if index >= start and index < end:
    #                     if index == start:
    #                         w.write(question[index] + ' B-ORG\n')
    #                     else:
    #                         w.write(question[index] + ' I-ORG\n')
    #                 else:
    #                     w.write(question[index] + ' O\n')
    #
    #     for park in park_list:
    #         for template in park_template_list:
    #             question = template % park
    #             start = question.index(park)
    #             end = start + len(park)
    #             for index in range(len(question)):
    #                 if index >= start and index < end:
    #                     if index == start:
    #                         w.write(question[index] + ' B-PARK\n')
    #                     else:
    #                         w.write(question[index] + ' I-PARK\n')
    #                 else:
    #                     w.write(question[index] + ' O\n')
    #
    #     for forestry in forestry_list:
    #         for template in normal_template_list:
    #             question = template % forestry
    #             start = question.index(forestry)
    #             end = start + len(forestry)
    #             for index in range(len(question)):
    #                 if index >= start and index < end:
    #                     if index == start:
    #                         w.write(question[index] + ' B-FOREST\n')
    #                     else:
    #                         w.write(question[index] + ' I-FOREST\n')
    #                 else:
    #                     w.write(question[index] + ' O\n')


if __name__ == '__main__':
    forestry_list, park_list, org_list, subject_list = get_subject_list(1500, 300, 600)
    tag_generate(org_list, park_list, forestry_list, subject_list, r"C:\Users\dhz\Desktop\template\new\law_dev")