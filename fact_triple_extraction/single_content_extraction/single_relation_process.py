#!/usr/bin/env python
# coding=utf-8
from data_resource import conn
from pyltp import Parser, SentenceSplitter, Segmentor, Postagger
import re

SINGLE_RELATION_CLASS = ['define', 'contain', 'duty', 'accord', 'right_and_obligations']

MODEL_DIR_PATH = "F:\\ltp_data_v3.4.0\\"
SEGMENTOR_MODEL = MODEL_DIR_PATH + "cws.model"  # LTP分词模型库
POSTAGGER_MODEL = MODEL_DIR_PATH + "pos.model"  # LTP词性标注模型库

segmentor = Segmentor()  # 初始化分词实例
postagger = Postagger()  # 初始化词性标注实例

segmentor.load(SEGMENTOR_MODEL)     # 加载分词模型库
postagger.load(POSTAGGER_MODEL)     # 加载词性标注模型库


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
            elif '责任' in relation[2] or '负责' in relation[2] or '负' in relation[2]:
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
def single_relation_save(classify_results):
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


# 实体对齐和清洗
def entity_aligament_and_wash():
    province_pattern = "^本省(.*)"
    city_pattern = "^本市(.*)"
    other_pattern = "^本[办法|条例|法|规划|规定|补充规定|规则](.*)"
    cursor = conn.cursor()
    wash_set = {
        'province': [],
        'city': [],
        'other': []
    }
    for type in SINGLE_RELATION_CLASS:
        select_sql = 'select * from %s' % type + '_relation'
        cursor.execute(select_sql)
        results = cursor.fetchall()
        for res in results:
            subject = res[4]
            province_res = re.search(province_pattern, subject, re.M | re.I)
            city_res = re.search(city_pattern, subject, re.M | re.I)
            other_res = re.search(other_pattern, subject, re.M | re.I)
            if province_res and not city_res and not other_res:
                wash_set['province'].append(res)
            elif city_res and not province_res and not other_res:
                wash_set['city'].append(res)
            elif other_res and not province_res and not city_res:
                wash_set['other'].append(res)
    return wash_set


def entity_aligament_and_wash_core(data_set):
    query_for_law_sql = '''select id, name, location, location_code, location_level, province_code from law where id = %s'''
    cursor = conn.cursor()
    # 1. 处理省份
    for relation in data_set['province']:
        id = relation[0]
        law_id = relation[1]
        class_type = relation[7]
        table_name = class_type + '_relation'
        update_sql = 'update %s ' % table_name + \
                     'set subject = %s, province_code = %s, province_name = %s, state = %s where id = %s'
        subject = str(relation[4]).replace('本省', '')
        cursor.execute(query_for_law_sql, (law_id,))
        law_info = cursor.fetchone()
        if subject == '' or subject is None:
            subject = law_info[2]
        province_name = law_info[2]
        province_code = law_info[5]
        state = 'province'
        cursor.execute(update_sql, (subject, province_code, province_name, state, id))
        conn.commit()
        print(id)

    # 2. 处理城市
    for relation in data_set['city']:
        id = relation[0]
        law_id = relation[1]
        class_type = relation[7]
        table_name = class_type + '_relation'
        update_sql = 'update %s ' % table_name + \
                     'set subject = %s, city_code = %s, city_name = %s, state = %s where id = %s'
        subject = str(relation[4]).replace('本市', '')
        cursor.execute(query_for_law_sql, (law_id,))
        law_info = cursor.fetchone()
        if subject == '' or subject is None:
            subject = law_info[2]
        city_name = law_info[2]
        city_code = law_info[3]
        state = 'city'
        cursor.execute(update_sql, (subject, city_code, city_name, state, id))
        conn.commit()
        print(class_type, id)

    # 3. 处理其他
    validate_words = ['本办法', '本条例', '本法', '本规划', '本规定', '本补充规定', '本规则']
    for relation in data_set['other']:
        id = relation[0]
        law_id = relation[1]
        class_type = relation[7]
        table_name = class_type + '_relation'
        update_sql = 'update %s ' % table_name + \
                     'set subject = %s, province_code = %s, province_name = %s,' \
                     ' city_code = %s, city_name = %s, state = %s where id = %s'
        for word in validate_words:
            if word in relation[4]:
                subject = str(relation[4]).replace(word, '')
                cursor.execute(query_for_law_sql, (law_id,))
                law_info = cursor.fetchone()
                if subject == '' or subject is None:
                    subject = law_info[1]

                location_level = law_info[4]
                if location_level == '1':
                    state = 'country'
                    province_code = 000000
                    city_code = 000000
                    province_name = '中华人民共和国'
                    city_name = '中华人民共和国'
                elif location_level == '2':
                    state = 'province'
                    province_code = law_info[5]
                    city_code = law_info[5]
                    province_name = law_info[2]
                    city_name = law_info[2]
                elif location_level == '3':
                    state = 'city'
                    province_code = law_info[5]
                    city_code = law_info[3]
                    province_name = law_info[2]
                    city_name = law_info[2]
                else:
                    province_code = ''
                    city_code = ''
                    province_name = ''
                    city_name = ''
                    state = ''
                cursor.execute(update_sql, (subject, province_code, province_name, city_code, city_name, state, id))
                conn.commit()
                print(class_type, id)


def update_all_location_info():
    cursor = conn.cursor()
    query_for_law_sql = '''select id, name, location, location_code, location_level, province_code 
                           from law where id = %s'''
    for class_type in SINGLE_RELATION_CLASS:
        table_name = class_type + '_relation'
        select_sql = 'select * from %s ' % table_name + 'where ISNULL(state)=1'
        cursor.execute(select_sql)
        results = cursor.fetchall()
        for relation in results:
            id = relation[0]
            law_id = relation[1]
            class_type = relation[7]
            table_name = class_type + '_relation'
            update_sql = 'update %s ' % table_name + \
                         'set subject = %s, province_code = %s, province_name = %s,' \
                         ' city_code = %s, city_name = %s, state = %s where id = %s'
            subject = relation[4]
            cursor.execute(query_for_law_sql, (law_id,))
            law_info = cursor.fetchone()

            location_level = law_info[4]
            if location_level == '1':
                state = 'country'
                province_code = 000000
                city_code = 000000
                province_name = '中华人民共和国'
                city_name = '中华人民共和国'
            elif location_level == '2':
                state = 'province'
                province_code = law_info[5]
                city_code = law_info[5]
                province_name = law_info[2]
                city_name = law_info[2]
            elif location_level == '3':
                state = 'city'
                province_code = law_info[5]
                city_code = law_info[3]
                province_name = law_info[2]
                city_name = law_info[2]
            else:
                province_code = ''
                city_code = ''
                province_name = ''
                city_name = ''
                state = ''
            cursor.execute(update_sql, (subject, province_code, province_name, city_code, city_name, state, id))
            conn.commit()
            print(class_type, id)


def subject_wash():
    cursor = conn.cursor()
    for class_type in SINGLE_RELATION_CLASS:
        table_name = class_type + '_relation'
        select_sql = 'select * from %s' % table_name
        cursor.execute(select_sql)
        results = cursor.fetchall()
        update_sql = 'update %s ' % table_name + 'set subject = %s where id = %s'
        for relation in results:
            id = relation[0]
            subject = relation[4]
            if str(subject).startswith('由'):
                subject = str(subject).replace('由', '')
                print(class_type, id, subject)
            elif len(subject) > 2 and subject[0] == subject[1] and subject[0] != '1' and subject[0] != 1:
                subject = str(subject)[1:]
                print(class_type, id, subject)
            # cursor.execute(update_sql, (subject, id))
            # conn.commit()


if __name__ == '__main__':
    # single_relation_dict = get_single_relation_dict()
    # classify_results = single_relation_classify(single_relation_dict)
    # single_relation_save(classify_results)
    # data_set = entity_aligament_and_wash()
    # entity_aligament_and_wash_core(data_set)
    # update_all_location_info()
    subject_wash()