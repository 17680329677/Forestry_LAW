# -*- coding : utf-8 -*-
# coding: utf-8
# 对切割为条款的法律数据再次清洗并分表，以便关系的表示

import re
from data_resource import conn


def chapter_article_process():      # 将法律文本的条款信息做进一步分表，分为两类，第一类包含“章”大标题，第二类只含条款
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


if __name__ == '__main__':
    chapter_article_process()