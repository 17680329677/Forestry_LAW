#!/usr/bin/env python
# coding=utf-8
from data_resource import conn


def get_complex_relation():
    select_sql = '''select * from extract_relation'''
    cursor = conn.cursor()
    cursor.execute(select_sql)
    results = cursor.fetchall()
    count = 0
    results_dict = dict({'have_colon': [], 'is_complex': [], 'accord': [], 'not_complex': [], 'other': []})
    for res in results:
        if res[6] is not None and res[7] is not None and res[8] is not None:
            if res[6] == "根据章节条款信息补全list" and res[8] == "根据章节条款信息补全list":
                continue
            # 1. 首实体中包含“:”  --- have_colon
            if "：" in res[6]:
                results_dict['have_colon'].append(res[6] + '--' + res[7] + '--' + res[8])
            # 2. 关系中提现出包含款的 -- is_complex
            elif is_contain_sentence(res[7]):
                results_dict['is_complex'].append(res[6] + '--' + res[7] + '--' + res[8])
            # 3. 依据关系 -- accord
            elif '(依据)' in res[7]:
                results_dict['accord'].append(res[6] + '--' + res[7] + '--' + res[8])
            elif "根据章节条款信息补全list" not in res[6] and "根据章节条款信息补全list" not in res[8]:
                results_dict['not_complex'].append(res[6] + '--' + res[7] + '--' + res[8])
            else:
                results_dict['other'].append(res[6] + '--' + res[7] + '--' + res[8])
            count = count + 1
    for rel in results_dict['have_colon']:
        print(rel)
    return results_dict


def colon_process(results_dict):
    for res in results_dict['have_colon']:
        if '应当' in res:
            print(str(res).split('应当'))
        elif '应' in res:
            print(str(res).split('应'))


def is_contain_sentence(content):
    complex_words = ['下列', '以下', '包括', '如下']
    if '为' == content[-1]:
        return True
    for word in complex_words:
        if word in content:
            return True
    return False


if __name__ == '__main__':
    colon_process(get_complex_relation())