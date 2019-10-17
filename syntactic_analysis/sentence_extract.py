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


if __name__ == '__main__':
    # detail_content_parser()
    # test_pyltp_sentence_split()
    class_one_sentences_extracte()
