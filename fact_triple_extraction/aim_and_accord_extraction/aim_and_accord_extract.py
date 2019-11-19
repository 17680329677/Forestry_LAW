#!/usr/bin/env python
# coding=utf-8

from fact_triple_extraction.aim_and_accord_extraction.xf_ltp_test import *
import time
import re


def get_article_1_first_sentence():         # 获取article_1 第一章-第一条的内容
    cursor = conn.cursor()
    sql = '''select id, a_key, a_content, chapter_id from article_1 where chapter_id in (select id from chapter where chapter_key = "第一章") and a_key = "第一条"'''
    cursor.execute(sql)
    results = cursor.fetchall()
    return results


def get_article_2_first_sentence():
    cursor = conn.cursor()
    sql = '''select * from article_2 where a_key = "第一条" and id in (select article_2_id from article_2_sentence where is_single = 1)'''
    sql = '''select * from article_2 where id in (select article_2_id from article_2_sentence where is_single = 1)'''
    cursor.execute(sql)
    results = cursor.fetchall()
    pattern_1 = "^为(.*)[根|依]据(.*)"
    pattern_2 = "^[根|依]据(.*)，为(.*)"
    pattern_3 = "^(根|依)据(.*)"
    pattern_4 = "^为(.*)"

    count = 0
    article_2_aim_and_accord_sentences = list()
    for result in results:
        law_id = result[3]
        contents = str(result[2]).strip().split('\n')
        for content in contents:
            if re.findall(pattern_1, str(content)):
                count += 1
                article_2_aim_and_accord_sentences.append(tuple((law_id, content.strip())))
            elif re.findall(pattern_2, str(content)):
                count += 1
                article_2_aim_and_accord_sentences.append(tuple((law_id, content.strip())))
            elif re.findall(pattern_3, str(content)):
                count += 1
                article_2_aim_and_accord_sentences.append(tuple((law_id, content.strip())))
            elif re.findall(pattern_4, str(content)):
                count += 1
                article_2_aim_and_accord_sentences.append(tuple((law_id, content.strip())))
    print(count)
    return article_2_aim_and_accord_sentences


def get_chapter_law_mapping():
    cursor = conn.cursor()
    select_sql = '''select id, law_id from chapter where chapter_key = "第一章"'''
    cursor.execute(select_sql)
    resutlts = cursor.fetchall()
    chapter_to_law = dict()
    for res in resutlts:
        chapter_to_law.update({res[0]: res[1]})
    return chapter_to_law


def short_name_extraction(content):        # 目标和根据中的实体和实体简称抽取(主要是根据中的法律法规名称)
    pattern_law_name = "《(.*?)》"
    pattern_short_name = "简称《(.*?)》"
    law_name_list = re.findall(pattern_law_name, content)
    if len(law_name_list) == 0:
        return None
    else:
        mapping_dict = dict()
        for law in law_name_list:
            mapping_dict.update({law: ''})
        short_name_list = re.findall(pattern_short_name, content)
        if len(short_name_list) == 0:
            return mapping_dict
        else:
            for s in short_name_list:
                law_index = law_name_list.index(s) - 1
                mapping_dict.update({law_name_list[law_index]: s})
                mapping_dict.pop(s)
            return mapping_dict


def article_1_extraction():             # 利用讯飞接口分析法律法规颁布的目的和根据
    article_1_first_sentences = get_article_1_first_sentence()
    for sentence in article_1_first_sentences:
        content = str(sentence[1]).split('：')[0].replace('\n', '')
        if len(content) > 150:
            continue
        try:
            content_nlp(content)
            time.sleep(1)
        except Exception as e:
            print(content, e)
            try_count = 0
            while try_count < 5:
                content_nlp(content)
                time.sleep(1)
                try_count += 1


def article_1_extraction_by_re(chapter_to_law):       # 利用正则表达式分离颁布的目的和根据
    sentences = get_article_1_first_sentence()
    count = 0
    for sentence in sentences:
        chapter_id = sentence[3]
        content = str(sentence[2]).replace('\n', '')
        count = count + 1
        index_dict = dict()
        if '为了' in content:
            index_dict.update({'aim': str(content).index('为了')})
        elif '为' in content:
            index_dict.update({'aim': str(content).index('为')})
        else:
            index_dict.update({'aim': -1})

        if "根据" in content:
            index_dict.update({'accord': str(content).index('根据')})
        elif "依据" in content:
            index_dict.update({'accord': str(content).index('依据')})
        else:
            index_dict.update({'accord': -1})

        if "结合" in content:
            index_dict.update({'combine': str(content).index('结合')})
        else:
            index_dict.update({'combine': -1})

        index_dict = sorted(index_dict.items(), key=lambda item: item[1])
        while len(index_dict) > 0 and index_dict[0][1] == -1:
            index_dict.pop(0)

        result_dict = dict()
        for index in range(len(index_dict)):
            if index == 0 and len(index_dict) == 1:
                result_dict.update({index_dict[index][0]: content[index_dict[index][1]:]})
            elif index < len(index_dict) - 1:
                result_dict.update({index_dict[index][0]: content[index_dict[index][1]:index_dict[index + 1][1]]})
            else:
                result_dict.update({index_dict[index][0]: content[index_dict[index][1]:]})
        with open(r"C:\Users\dhz1216\Desktop\test\aim_and_accord_new.txt", "a") as w:
            w.write(content + '\n')
            if 'aim' in result_dict:
                aim_list = str(result_dict['aim']).split('，')
                w.write('目的：\n' + "\n".join(aim_list) + '\n===============================================\n')
            if 'accord' in result_dict:
                accord_list = str(result_dict['accord']).split('，')
                w.write('根据：\n' + "\n".join(accord_list) + '\n===============================================\n')
            if 'combine' in result_dict:
                combine_list = str(result_dict['combine']).split('，')
                w.write('结合：\n' + "\n".join(combine_list) + '\n===============================================\n')
            w.write('================================================================' + '\n')
        # TODO: 将信息存入数据库
        law_id = chapter_to_law[chapter_id]
        save_aim_and_accord(law_id, result_dict)


def article_2_extraction_by_re():       # 利用正则表达式分离颁布的目的和根据
    sentences = get_article_2_first_sentence()
    for sentence in sentences:
        content = str(sentence[1]).replace('\n', '')
        index_dict = dict()
        if '为了' in content:
            index_dict.update({'aim': str(content).index('为了')})
        elif '为' in content:
            index_dict.update({'aim': str(content).index('为')})
        else:
            index_dict.update({'aim': -1})

        if "根据" in content:
            index_dict.update({'accord': str(content).index('根据')})
        elif "依据" in content:
            index_dict.update({'accord': str(content).index('依据')})
        else:
            index_dict.update({'accord': -1})

        if "结合" in content:
            index_dict.update({'combine': str(content).index('结合')})
        else:
            index_dict.update({'combine': -1})

        index_dict = sorted(index_dict.items(), key=lambda item: item[1])
        while len(index_dict) > 0 and index_dict[0][1] == -1:
            index_dict.pop(0)

        result_dict = dict()
        for index in range(len(index_dict)):
            if index == 0 and len(index_dict) == 1:
                result_dict.update({index_dict[index][0]: content[index_dict[index][1]:]})
            elif index < len(index_dict) - 1:
                result_dict.update({index_dict[index][0]: content[index_dict[index][1]:index_dict[index + 1][1]]})
            else:
                result_dict.update({index_dict[index][0]: content[index_dict[index][1]:]})
        with open(r"C:\Users\dhz1216\Desktop\test\aim_and_accord_new.txt", "a") as w:
            w.write(content + '\n')
            if 'aim' in result_dict:
                aim_list = str(result_dict['aim']).split('，')
                w.write('目的：\n' + "\n".join(aim_list) + '\n===============================================\n')
            if 'accord' in result_dict:
                accord_list = str(result_dict['accord']).split('，')
                w.write('根据：\n' + "\n".join(accord_list) + '\n===============================================\n')
            if 'combine' in result_dict:
                combine_list = str(result_dict['combine']).split('，')
                w.write('结合：\n' + "\n".join(combine_list) + '\n===============================================\n')
            w.write('================================================================' + '\n')
        # TODO: 将信息存入数据库
        law_id = sentence[0]
        save_aim_and_accord(law_id, result_dict)


def save_aim_and_accord(law_id, info):
    insert_law_aim = '''insert into law_aim (law_id, content) value (%s, %s)'''
    cursor = conn.cursor()
    if 'aim' in info:
        aim = info['aim']
        if '为了' in aim:
            aim = str(aim).replace('为了', '')
        elif '为' in aim:
            aim = str(aim).replace('为', '')
        aim_list = list(filter(None, str(aim).split('，')))
        for aim in aim_list:
            try:
                cursor.execute(insert_law_aim, (law_id, aim))
                conn.commit()
            except Exception as e:
                conn.rollback()
                print('\033[1;32;41m' + str(law_id) + aim + e + ': FAILED---------' + '\033[0m')
        print(law_id, '---------------------AIM INSERT SUCCESS')

    if 'accord' in info:
        accord = str(info['accord']).replace("\n", "")
        if '根据' in accord:
            accord = accord.replace('根据', '')
        elif '依据' in accord:
            accord = accord.replace('依据', '')
        accord_list = list(filter(None, str(accord).split('，')))
        for i in range(len(accord_list)):
            content = accord_list[i]
            if '制定本' in content and content.index('制定本') > 2:
                accord_list[i] = content[0:content.index('制定本')]
            elif '制定本' in content:
                accord_list[i] = ''
        accord_list = list(filter(None, accord_list))
        insert_law_accord = '''insert into law_accord (law_id, is_accord_law, content, law_name, short_name) value (%s, %s, %s, %s, %s)'''
        for a in accord_list:
            short_name_mapping = short_name_extraction(a)
            if short_name_mapping is not None and len(short_name_mapping) != 0:
                for law_name in short_name_extraction(a):
                    short_name = short_name_mapping[law_name]
                    try:
                        cursor.execute(insert_law_accord, (law_id, 1, a, law_name, short_name))
                        conn.commit()
                    except Exception as e:
                        conn.rollback()
                        print('\033[1;32;41m' + str(law_id) + a + '---' + e + '\033[0m')
            else:
                is_accord_law = 0
                a = str(a).strip()
                if len(a) < 5 or len(a) > 20:
                    continue
                elif '宪法' in a:
                    is_accord_law = 1
                    law_name = '中华人民共和国宪法'
                    short_name = '宪法'
                else:
                    is_accord_law = 0
                    law_name = ''
                    short_name = ''
                try:
                    cursor.execute(insert_law_accord, (law_id, is_accord_law, a, law_name, short_name))
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    print('\033[1;32;41m' + str(law_id) + a + '---' + e + '\033[0m')
            print(law_id, '----', a, '-------SUCCESS')


def accord_law_mapping():       # 依据法律ID对应
    select_accord_sql = '''select id, law_name from law_accord where is_accord_law = 1'''
    select_law_sql = '''select id, name from law where name = %s'''
    update_law_sql = '''update law_accord set accord_law_id = %s where id = %s'''
    cursor = conn.cursor()
    cursor.execute(select_accord_sql)
    accords = cursor.fetchall()
    print(len(accords))
    for accord in accords:
        accord_id = accord[0]
        law_name = accord[1]
        cursor.execute(select_law_sql, (law_name,))
        law = cursor.fetchone()
        if law:
            try:
                cursor.execute(update_law_sql, (law[0], accord_id))
                conn.commit()
                print(law[0], '------', law_name, '-----', law[1], '----SUCCESS')
            except Exception as e:
                conn.rollback()
                print('\033[1;32;41m' + str(accord_id) + law_name + e + ': FAILED---------' + '\033[0m')
        else:
            try:
                cursor.execute(update_law_sql, (-1, accord_id))
                conn.commit()
                print(law_name, '----SUCCESS')
            except Exception as e:
                conn.rollback()
                print('\033[1;32;41m' + str(accord_id) + law_name + e + ': FAILED---------' + '\033[0m')


if __name__ == '__main__':
    # print('================================================ARTICLE 1==============================================\n')
    # chapter_to_law = get_chapter_law_mapping()
    # article_1_extraction_by_re(chapter_to_law)
    # print('\n==============================================ARTICLE 2==============================================\n')
    # get_article_2_first_sentence()
    # article_2_extraction_by_re()
    accord_law_mapping()