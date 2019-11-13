"""
依存句法分析
"""
import re
from data_resource import conn


def detail_content_parser():
    cursor = conn.cursor()
    select_sql = "select law_id, p_key, p_content from law_content_parse where id < 101"
    cursor.execute(select_sql)
    results = cursor.fetchall()
    for res in results:
        print(res[1] + ': ' + str(res[2]).split('\n')[0])


def class_one_sentences_extracte():       # 第一类文本的单句提取
    pattern = re.compile("第(.*?)(?:章|条)")       # 定义正则表达式用以判断是否是第一类
    cursor = conn.cursor()
    select_sql = "select id, law_id, p_key, p_content from law_content_parse"
    cursor.execute(select_sql)
    results = cursor.fetchall()

    complex_count = 0
    single_count = 0
    insert_complex_sentence = "insert into sentences (law_id, title_id, sentence, is_single) " \
                              "value (%s, %s, %s, %s)"
    for res in results:
        if pattern.match(res[2]):
            title_id = res[0]       # law_content_parse的主键ID，对应sentences表中的title_id
            law_id = res[1]     # 对应法律法规id
            if '：' in str(res[3]):
                complex_count = complex_count + 1
                try:
                    cursor.execute(insert_complex_sentence, (law_id, title_id, res[3], 0))
                    conn.commit()
                    print(str(res[3]) + '-----------Success')
                except Exception as e:
                    print('\033[1;32;41m' + str(res[3]) + ': FAILED---------' + '\033[0m')
                    conn.rollback()
                    print(e)
            else:
                single_count = single_count + 1
                sentences = str(res[3]).split('\n')
                for sentence in sentences:
                    if len(sentence) != 0:
                        try:
                            cursor.execute(insert_complex_sentence, (law_id, title_id, sentence, 1))
                            conn.commit()
                            print(str(sentence) + '-----------Success')
                        except Exception as e:
                            print('\033[1;32;41m' + sentence + ': FAILED---------' + '\033[0m')
                            conn.rollback()
                            print(e)


def article_1_sentence_extract():       # 将article_1 的句子尽心分割提取
    select_sql = "select * from article_1"
    cursor = conn.cursor()
    cursor.execute(select_sql)
    articles = cursor.fetchall()
    for article in articles:
        article_1_id = article[0]
        article_1_content = article[2]
        insert_article_1_sentence_sql = '''insert into article_1_sentence (article_1_id, is_single, content) value (%s, %s, %s)'''
        if '：' in article_1_content:
            is_single = 0
            article_1_sentence_content = str(article_1_content).split('：')[0].replace(" ", "")
            try:
                cursor.execute(insert_article_1_sentence_sql, (article_1_id, is_single, article_1_sentence_content))
                conn.commit()
            except Exception as e:
                conn.rollback()
                print('\033[1;32;41m' + str(article_1_id) + article_1_sentence_content + e + ': FAILED---------' + '\033[0m')

            article_1_clauses = str(article_1_content).split('：')[1].split("\n")
            select_article1_sentence_id = '''SELECT id from article_1_sentence where id = (SELECT max(id) FROM article_1_sentence);'''
            cursor.execute(select_article1_sentence_id)
            sentence_id = cursor.fetchone()[0]
            for article_1_clause in article_1_clauses:
                if article_1_clause is not None and article_1_clause != '':
                    insert_article_1_clause_sql = '''insert into article_1_clause (article_1_id, article_1_sentence_id, clause_content) value (%s, %s, %s)'''
                    try:
                        cursor.execute(insert_article_1_clause_sql, (article_1_id, sentence_id, str(article_1_clause).replace(" ", "")))
                        conn.commit()
                    except Exception as e:
                        conn.rollback()
                        print('\033[1;32;41m' + str(article_1_id) + article_1_clause + e + ': FAILED---------' + '\033[0m')
            print(article[2] + '============================================SUCCESS')
        else:
            is_single = 1
            try:
                cursor.execute(insert_article_1_sentence_sql, (article_1_id, is_single, article_1_content))
                conn.commit()
                print(article_1_content + '=========================================SUCCESS')
            except Exception as e:
                conn.rollback()
                print('\033[1;32;41m' + str(article_1_id) + '--' + e + ': FAILED---------' + '\033[0m')


def article_2_sentence_extract():       # 将article_2 的句子尽心分割提取
    select_article_2_sql = '''select * from article_2'''
    cursor = conn.cursor()
    cursor.execute(select_article_2_sql)
    articles = cursor.fetchall()
    for article in articles:
        article_2_id = article[0]
        article_2_content = article[2]
        insert_article_2_sentence_sql = '''insert into article_2_sentence (article_2_id, is_single, content) value (%s, %s, %s)'''
        if '：' in article_2_content:
            is_single = 0
            article_2_sentence_content = str(article_2_content).split('：')[0].replace(" ", "")
            try:
                cursor.execute(insert_article_2_sentence_sql, (article_2_id, is_single, article_2_sentence_content))
                conn.commit()
            except Exception as e:
                conn.rollback()
                print('\033[1;32;41m' + str(article_2_id) + article_2_sentence_content + e + ': FAILED---------' + '\033[0m')

            article_2_clauses = str(article_2_content).split('：')[1].split("\n")
            select_article2_sentence_id = '''SELECT id from article_2_sentence where id = (SELECT max(id) FROM article_2_sentence);'''
            cursor.execute(select_article2_sentence_id)
            sentence_id = cursor.fetchone()[0]
            for article_2_clause in article_2_clauses:
                if article_2_clause is not None and article_2_clause != '':
                    insert_article_2_clause_sql = '''insert into article_2_clause (article_2_id, article_2_sentence_id, clause_content) value (%s, %s, %s)'''
                    try:
                        cursor.execute(insert_article_2_clause_sql, (article_2_id, sentence_id, str(article_2_clause).replace(" ", "")))
                        conn.commit()
                    except Exception as e:
                        conn.rollback()
                        print('\033[1;32;41m' + str(article_2_id) + article_2_clause + e + ': FAILED---------' + '\033[0m')
            print(article[2] + '============================================SUCCESS')
        else:
            is_single = 1
            try:
                cursor.execute(insert_article_2_sentence_sql, (article_2_id, is_single, article_2_content))
                conn.commit()
                print(article_2_content + '=========================================SUCCESS')
            except Exception as e:
                conn.rollback()
                print('\033[1;32;41m' + str(article_2_id) + '--' + e + ': FAILED---------' + '\033[0m')


def clause_strip():     # 对法律条款去空格
    select_article_1_sql = '''select * from article_1_clause'''
    select_article_2_sql = '''select * from article_2_clause'''
    update_article_1_sql = '''update article_1_clause set clause_content = %s where id = %s'''
    update_article_2_sql = '''update article_2_clause set clause_content = %s where id = %s'''
    cursor = conn.cursor()
    cursor.execute(select_article_1_sql)
    article_1_clauses = cursor.fetchall()
    cursor.execute(select_article_2_sql)
    article_2_clauses = cursor.fetchall()
    for a1_clause in article_1_clauses:
        a1_clause_id = a1_clause[0]
        a1_clause_content = str(a1_clause[3]).strip()
        try:
            cursor.execute(update_article_1_sql, (a1_clause_content, a1_clause_id))
            conn.commit()
            print(str(a1_clause_id) + a1_clause_content + '------------------------------------SUCCESS')
        except Exception as e:
            conn.rollback()
            print('\033[1;32;41m' + str(a1_clause_id) + '--' + e + ': FAILED---------' + '\033[0m')
    print('=========================================================================================================')
    print('=========================================================================================================')
    print('=========================================================================================================')
    for a2_clause in article_2_clauses:
        a2_clause_id = a2_clause[0]
        a2_clause_content = str(a2_clause[3]).strip()
        try:
            cursor.execute(update_article_2_sql, (a2_clause_content, a2_clause_id))
            conn.commit()
            print(str(a2_clause_id) + a2_clause_content + '------------------------------------SUCCESS')
        except Exception as e:
            conn.rollback()
            print('\033[1;32;41m' + str(a2_clause_id) + '--' + e + ': FAILED---------' + '\033[0m')


if __name__ == '__main__':
    # detail_content_parser()
    # test_pyltp_sentence_split()
    # class_one_sentences_extracte()
    # article_2_sentence_extract()
    clause_strip()