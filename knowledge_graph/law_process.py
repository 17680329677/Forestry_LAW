# -*- coding : utf-8 -*-
# coding: utf-8
# 再次处理基础法律数据，为构建一个小的知识图谱做准备
from pyltp import Parser, SentenceSplitter, Segmentor, Postagger
from data_resource import conn

MODEL_DIR_PATH = "E:\\ltp_data_v3.4.0\\"
SEGMENTOR_MODEL = MODEL_DIR_PATH + "cws.model"  # LTP分词模型库
POSTAGGER_MODEL = MODEL_DIR_PATH + "pos.model"  # LTP词性标注模型库

segmentor = Segmentor()  # 初始化分词实例
postagger = Postagger()  # 初始化词性标注实例

segmentor.load(SEGMENTOR_MODEL)     # 加载分词模型库
postagger.load(POSTAGGER_MODEL)     # 加载词性标注模型库


def location_extract():     # 运用pyltp的分词和词性标注，识别法律法规所属地区（省市）
    select_sql = "select id, name from law"
    update_sql = "update law set location = %s where id = %s"
    cursor = conn.cursor()
    select_special_city_sql = "select name from city where name not like '%市'"
    cursor.execute(select_sql)
    results = cursor.fetchall()
    cursor.execute(select_special_city_sql)
    select_special_city = cursor.fetchall()
    special_city_list = list()
    for c in select_special_city:
        special_city_list.append(c[0])

    for result in results:
        title = result[1]
        location = ''
        for city in special_city_list:
            if city in title:
                location = city
                break
        if location is None or location == '':
            words = list(segmentor.segment(title))
            postag = list(postagger.postag(words))
            for index in range(len(words)):
                if postag[index] == 'ns':
                    location = location + words[index]
                    if postag[index + 1] == 'ns':
                        location = location + words[index + 1]
                        if postag[index + 2] == 'ns':
                            location = location + words[index + 2]
                    break

        if location is None or location == '' or len(location) <= 1:
            location='中华人民共和国'
        try:
            cursor.execute(update_sql, (location, result[0]))
            conn.commit()
            print(str(result[0]) + result[1] + '-----------SUCCESS')
        except Exception as e:
            conn.rollback()
            print('\033[1;32;41m' + str(result[0]) + result[1] + e + '\033[0m')


def province_index(word):       # 省份索引对应
    cursor = conn.cursor()
    province_select_sql = 'select * from province'  # 查询标准省份
    cursor.execute(province_select_sql)
    provinces = cursor.fetchall()
    province_dict = dict()
    for province in provinces:
        province_key = province[2].replace(' ', '').replace('省', '').replace('市', '')   # 将“省”，“市”以及空格去掉，方便比较
        province_dict.update({province_key: province[1]})
    word = word.replace(' ', '').replace('省', '').replace('市', '')

    special_province = ['北京', '上海', '重庆', '天津']
    special_area = ['澳门', '香港']
    if word in province_dict:       # 判断是否有对应的省份
        code = province_dict[word]
        if word in special_province:
            word = word + '市'
        elif word in special_area:
            word = word + '特别行政区'
        else:
            word = word + '省'
        return {word: code}
    else:
        return None


def city_index(word):       # 城市索引对应
    cursor = conn.cursor()
    city_select_sql = 'select * from city'      # 查询标准城市
    cursor.execute(city_select_sql)
    cities = cursor.fetchall()
    city_dict = dict()
    for city in cities:
        city_key = city[2].replace(' ', '').replace('市', '')  # 将“省”，“市”以及空格去掉，方便比较
        city_dict.update({city_key: city[1]})
    word = word.replace(' ', '').replace('市', '')

    select_special_city_sql = "select name from city where name not like '%市'"
    cursor.execute(select_special_city_sql)
    select_special_city = cursor.fetchall()
    special_city_list = list()
    for c in select_special_city:
        special_city_list.append(c[0])

    if word in city_dict:       # 判断是否有对应的城市
        code = city_dict[word]
        if word not in special_city_list:
            word = word + '市'
        return {word: code}
    else:
        return None


def area_index(word):       # 地区索引对应
    cursor = conn.cursor()
    area_select_sql = 'select * from area'  # 查询标准地区(县、区)
    cursor.execute(area_select_sql)
    areas = cursor.fetchall()
    area_dict = dict()
    for area in areas:
        area_key = area[2].replace(' ', '').replace('市', '').replace('县', '').replace('区', '')  # 将“区”，“县”以及空格去掉，方便比较
        area_dict.update({area_key: area[1]})
    word = word.replace(' ', '').replace('市', '').replace('县', '').replace('区', '')
    if word in area_dict:
        code = area_dict[word]
        return {word: code}
    else:
        return None


def location_alignment():       # 利用国内标准的省市县划分将识别并提取出来的归属地进行对齐-----最大精度对齐到城市，区县级较少，没必要进行对齐
    cursor = conn.cursor()
    location_select_sql = 'select id, location from law'    # 查询提取出的归属地
    cursor.execute(location_select_sql)
    locations = cursor.fetchall()

    for location in locations:
        words = list(segmentor.segment(location[1]))
        for i in range(len(words)):
            province_info = province_index(words[i])
            if province_info is not None:        # 省份不是空的情况
                province_name = list(province_info.keys())[0]
                province_code = list(province_info.values())[0]
                city_info = None
                if i + 1 < len(words):
                    city_info = city_index(words[i + 1])
                if city_info is not None:
                    city_name = list(city_info.keys())[0]
                    city_code = list(city_info.values())[0]
                    # -----------------------------------做一次对齐更新，更新到城市
                    update_law(province_name + city_name, city_code, 3, location[0])
                else:
                    # -----------------------------------做一次对齐更新，更新到省份
                    update_law(province_name, province_code, 2, location[0])
                    pass
            elif city_index(words[i]) is not None:
                city_info = city_index(words[i])
                city_code = list(city_info.values())[0]
                city_name = list(city_info.keys())[0]
                select_sql = "select name from province where code = (select provincecode from city where code = %s)"
                cursor.execute(select_sql, (city_code))
                province_name = cursor.fetchone()[0]
                # --------------------------------------做一次对齐更新，更新到城市
                update_law(province_name + city_name, city_code, 3, location[0])


def update_law(location, location_code, location_level, law_id):
    cursor = conn.cursor()
    update_sql = "update law set location = %s, location_code = %s, location_level = %s where id = %s"
    try:
        cursor.execute(update_sql, (location, location_code, location_level, law_id))
        conn.commit()
        print(str(law_id) + '-----------------------UPDATE SUCCESS')
    except Exception as e:
        conn.rollback()
        print('\033[1;32;41m' + str(law_id) + ': FAILED---------' + e + '\033[0m')


if __name__ == '__main__':
    # location_extract()      # 归属地识别

    location_alignment()    # 标准归属地对齐
