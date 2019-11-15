# -*- coding : utf-8 -*-
# coding: utf-8
# 对切割为条款的法律数据再次清洗并分表，以便关系的表示

import re
from data_resource import conn


def chapter_article_process():          # 法一（有问题）：将法律文本的条款信息做进一步分表，分为两类，第一类包含“章”大标题，第二类只含条款
    select_sql = "select * from law_content_parse"
    cursor = conn.cursor()
    cursor.execute(select_sql)
    contents = cursor.fetchall()

    index = 0
    while index < len(contents):
        pattern_chapter = re.compile("第(.*?)章")
        pattern_article = re.compile("第(.*?)条")
        match_chapter = pattern_chapter.match(contents[index][2])
        if match_chapter:
            # 此处将章的信息插入chapter
            insert_chapter_sql = "insert into chapter (chapter_key, chapter_name, law_id) value (%s, %s, %s)"
            try:
                cursor.execute(insert_chapter_sql, (contents[index][2], contents[index][3], contents[index][1]))
                conn.commit()
                print(contents[index][5] + '----' + contents[index][2] + '----------------SUCCESS')
            except Exception as e:
                conn.rollback()
                print('\033[1;32;41m' + contents[index][5] + e + ': CHAPTER FAILED---------' + '\033[0m')
                return

            index = index + 1
            while index < len(contents):
                select_chapter_sql = 'SELECT id from chapter where id = (SELECT max(id) FROM chapter);'
                cursor.execute(select_chapter_sql)          # TODO： 此处添加逻辑判断是否已经读到下一篇法规
                chapter_id = cursor.fetchone()[0]
                match_article = pattern_article.match(contents[index][2])
                if match_article:
                    # 此处插入article信息
                    insert_article1_sql = "insert into article_1 (a_key, a_content, chapter_id) value (%s, %s, %s)"
                    try:
                        cursor.execute(insert_article1_sql, (contents[index][2], contents[index][3], chapter_id))
                        conn.commit()
                        print(contents[index][5] + '----' + contents[index][2] + '----------------SUCCESS')
                    except Exception as e:
                        conn.rollback()
                        print('\033[1;32;41m' + contents[index][5] + e + ': ARTICLE FAILED---------' + '\033[0m')
                        return
                    index = index + 1
                else:
                    print('-----------------------------' + contents[index][5] + '----------------------------------')
                    break
        else:
            insert_article2_sql = "insert into article_2 (a_key, a_content, law_id) value (%s, %s, %s)"
            try:
                cursor.execute(insert_article2_sql, (contents[index][2], contents[index][3], contents[index][1]))
                conn.commit()
                print(contents[index][5] + '----' + contents[index][2] + '----------------SUCCESS')
            except Exception as e:
                conn.rollback()
                print('\033[1;32;41m' + contents[index][5] + e + ': ARTICLE FAILED---------' + '\033[0m')
                return
            index = index + 1


def chapter_article_process_2():        # 法二：将法律文本的条款信息做进一步分表，分为两类，第一类包含“章”大标题，第二类只含条款
    cursor = conn.cursor()
    pattern_chapter = re.compile("第(.*?)章")
    pattern_article = re.compile("第(.*?)条")
    select_law_id_sql = "select law_id from law_content_parse group by law_id"
    # 先统计出law_id, 保存到list当中
    cursor.execute(select_law_id_sql)
    law_id_tuple = cursor.fetchall()
    law_id_list = list()
    for law in law_id_tuple:
        law_id_list.append(law[0])

    # 按照id查询law_content_parse, 并做处理
    select_law_content_sql = "select * from law_content_parse where law_id = %s"
    for law_id in law_id_list:
        cursor.execute(select_law_content_sql, (law_id,))
        contents = cursor.fetchall()

        index = 0
        while index < len(contents):
            match_chapter = pattern_chapter.match(contents[index][2])
            if match_chapter:
                # 此处将章的信息插入chapter
                insert_chapter_sql = "insert into chapter (chapter_key, chapter_name, law_id) value (%s, %s, %s)"
                try:
                    cursor.execute(insert_chapter_sql, (contents[index][2], contents[index][3], law_id))
                    conn.commit()
                    print(contents[index][5] + '----' + contents[index][2] + '----------------SUCCESS')
                except Exception as e:
                    conn.rollback()
                    print('\033[1;32;41m' + contents[index][5] + e + ': CHAPTER FAILED---------' + '\033[0m')
                    return

                index = index + 1
                while index < len(contents):
                    select_chapter_sql = 'SELECT id from chapter where id = (SELECT max(id) FROM chapter);'
                    cursor.execute(select_chapter_sql)
                    chapter_id = cursor.fetchone()[0]
                    match_article = pattern_article.match(contents[index][2])
                    if match_article:
                        # 此处插入article信息
                        insert_article1_sql = "insert into article_1 (a_key, a_content, chapter_id) value (%s, %s, %s)"
                        try:
                            cursor.execute(insert_article1_sql, (contents[index][2], contents[index][3], chapter_id))
                            conn.commit()
                            print(contents[index][5] + '----' + contents[index][2] + '----------------SUCCESS')
                        except Exception as e:
                            conn.rollback()
                            print('\033[1;32;41m' + contents[index][5] + e + ': ARTICLE FAILED---------' + '\033[0m')
                            return
                        index = index + 1
                    else:
                        print(
                            '-----------------------------' + contents[index][5] + '----------------------------------')
                        break
            else:
                insert_article2_sql = "insert into article_2 (a_key, a_content, law_id) value (%s, %s, %s)"
                try:
                    cursor.execute(insert_article2_sql, (contents[index][2], contents[index][3], law_id))
                    conn.commit()
                    print(contents[index][5] + '----' + contents[index][2] + '----------------SUCCESS')
                except Exception as e:
                    conn.rollback()
                    print('\033[1;32;41m' + contents[index][5] + e + ': ARTICLE FAILED---------' + '\033[0m')
                    return
                index = index + 1


def article_2_key_process():        # 将不包含“章”的条款的条款序号统一为 “第XX条”
    select_sql = "select id, a_key from article_2"
    update_sql = "update article_2 set a_key = %s where id = %s"
    cursor = conn.cursor()
    cursor.execute(select_sql)
    articles = cursor.fetchall()
    for article in articles:
        if '条' not in article[1]:
            article_key = '第' + str(article[1]).replace('、', '') + '条'
            try:
                cursor.execute(update_sql, (article_key, article[0]))
                conn.commit()
                print(str(article[0]) + article_key + '--------------------UPDATE SUCCESS')
            except Exception as e:
                conn.rollback()
                print('\033[1;32;41m' + str(article[0]) + article_key + e + ': ARTICLE FAILED---------' + '\033[0m')


if __name__ == '__main__':

    # chapter_article_process()

    # chapter_article_process_2()

    article_2_key_process()