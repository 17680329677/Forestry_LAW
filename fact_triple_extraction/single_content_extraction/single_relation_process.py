#!/usr/bin/env python
# coding=utf-8
from data_resource import conn
import re


def get_law_info_dict():
    select_sql = '''select id, name from law'''
    cursor = conn.cursor()
    cursor.execute(select_sql)
    law_info_dict = dict()
    results = cursor.fetchall()
    for res in results:
        law_info_dict.update({res[0]: res[1]})
    return law_info_dict


def get_single_relation():
    select_sql = '''select * from single_extract_relation where class = 1 order by sentence_id'''
    cursor = conn.cursor()
    cursor.execute(select_sql)
    results = cursor.fetchall()
    count = 0
    for res in results:
        count = count + 1
        law_id = res[1]
        chapter_id = res[3]
        sentence_id = res[4]
        relation = res[6] + '--' + res[7] + '--' + res[8]
        print("(law_id: %s | chapter_id: %s | sentence_id: %s)：%s" % (law_id, chapter_id, sentence_id, relation))
        if count > 1000:
            break


def get_single_relation_dict():
    select_sql = '''select * from single_extract_relation order by sentence_id'''
    cursor = conn.cursor()
    cursor.execute(select_sql)
    results = cursor.fetchall()
    single_relation_dict = dict()
    for res in results:
        law_id = res[1]
        chapter_id = res[3]
        sentence_id = res[4]
        subject = res[6]
        relation = res[7]
        object = res[8]
        if subject in single_relation_dict:
            if subject is not object:
                single_relation_dict[subject].append(tuple((law_id, subject, relation, object, chapter_id, sentence_id)))
        else:
            if subject is not object:
                single_relation_dict.update({subject: []})
                single_relation_dict[subject].append(tuple((law_id, subject, relation, object, chapter_id, sentence_id)))

    # output_file = "C:\\Users\\dhz\\Desktop\\template\\single_relation.txt"
    # with open(output_file, "a") as w:
    #     for subject in single_relation_dict:
    #         for rel in single_relation_dict[subject]:
    #             w.write(rel + '\n')
    #         w.write("============================================================================\n")
    return single_relation_dict


# TODO: 将关系分类为以下几类
# 1. 定义类
# 2. 包含类
# 3. 权利义务类
# 4. 责任类
# 5. 依据类
# 6. 其他类
def single_relation_classify(single_relation_dict):
    province_pattern = "^本省(.*)"
    city_pattern = "^本市(.*)"
    other_pattern = "^本(.*)"

    classify_results = {
        'define': [],
        'contain': [],
        'right_and_obligations': [],
        'duty': [],
        'accord': [],
        'other': []
    }
    for sub in single_relation_dict:
        for relation in single_relation_dict[sub]:
            # 1. 定义类
            if relation[2] == '是' or relation[2] == '是指':
                if len(relation[1]) > 1:
                    classify_results['define'].append(relation)
            # 2. 包含类
            elif '包括' in relation[2] or '包含' in relation[2]:
                if len(relation[1]) > 1:
                    classify_results['contain'].append(relation)
            # 3. 责任类
            elif '责任' in relation[2] or '负责' in relation[2]:
                if len(relation[1]) > 1:
                    classify_results['duty'].append(relation)
            # 4. 依据类
            elif '依据' in relation[2]:
                if len(relation[1]) > 1:
                    classify_results['accord'].append(relation)
            # 5. 权利与义务类
            else:
                if len(relation[1]) > 1:
                    classify_results['right_and_obligations'].append(relation)
    return classify_results


# TODO: 添加生效流程一项
def single_relation_process(classify_results):
    output_file = "C:\\Users\\dhz\\Desktop\\template\\classify_results.txt"
    cursor = conn.cursor()
    with open(output_file, "a") as w:
        for type in classify_results:
            table_name = type + '_relation'
            insert_sql = 'insert into %s (law_id, chapter_id, sentence_id, subject, relation, object, relation_type)' \
                         % table_name + \
                         'value (%s, %s, %s, %s, %s, %s, %s)'
            print(table_name)
            for relation in classify_results[type]:
                cursor.execute(insert_sql, (relation[0], relation[4],
                                            relation[5], relation[1],
                                            relation[2], relation[3], type))
                conn.commit()


if __name__ == '__main__':
    single_relation_dict = get_single_relation_dict()
    classify_results = single_relation_classify(single_relation_dict)
    single_relation_process(classify_results)