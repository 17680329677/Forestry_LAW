#!/usr/bin/env python
# coding=utf-8
from data_resource import conn


LAW_PROPERTY = {
    'name': 1,
    'location_dep': 2,
    'year': 3,
    'pub_unit': 4,
    'pub_time': 5,
    'implement_time': 6,
    'classify': 7,
    'key_word': 8,
    'content_id': 9,
    'credit_line': 10,
    'catalogue': 11,
    'status': 12,
    'text_name': 13,
    'location': 14,
    'location_code': 15,
    'location_level': 16,
    'key_words': 17,
    'type': 18,
    'class_id': 19,
    'province_code': 20
}


def law_info_segment():
    cursor = conn.cursor()
    select_sql = '''select * from law'''
    cursor.execute(select_sql)
    results = cursor.fetchall()
    property_list = []
    for i in LAW_PROPERTY:
        property_list.append(i)
    for res in results:
        law_id = res[0]
        for property_name in property_list:
            index = LAW_PROPERTY[property_name]
            property_val = res[index]
            if property_val is None or property_val == '':
                property_val = '未知'
                update_sql = 'update law set %s' % property_name + ' = %s where id = %s'
                cursor.execute(update_sql, (property_val, law_id))
                conn.commit()
                print(law_id, property_name, res[index], property_val)


if __name__ == '__main__':
    law_info_segment()