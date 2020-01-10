#!/usr/bin/env python
# coding=utf-8
from data_resource import conn


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
    select_sql = '''select * from single_extract_relation where class = 1 order by sentence_id'''
    cursor = conn.cursor()
    cursor.execute(select_sql)
    results = cursor.fetchall()
    single_relation_dict = dict()
    for res in results:
        subject = res[6]
        relation = res[7]
        object = res[8]
        if subject in single_relation_dict:
            single_relation_dict[subject].append(subject + '--' + relation + '--' + object)
        else:
            single_relation_dict.update({subject: []})
            single_relation_dict[subject].append(subject + '--' + relation + '--' + object)

    output_file = "C:\\Users\\dhz\\Desktop\\template\\single_relation.txt"
    with open(output_file, "a") as w:
        for subject in single_relation_dict:
            for rel in single_relation_dict[subject]:
                w.write(rel + '\n')
            w.write("============================================================================\n")
    return single_relation_dict


def single_relation_merge():
    cursor = conn.cursor()
    select_sql = '''select law_id, 
                           class, 
                           chapter_id, 
                           sentence_id, 
                           is_contain, 
                           subject, 
                           relation, 
                           object 
                    from single_extract_relation_copy1'''
    insert_sql = '''insert into single_extract_relation (law_id, 
                                                         class, 
                                                         chapter_id, 
                                                         sentence_id, 
                                                         is_contain, 
                                                         subject, 
                                                         relation,
                                                         object)
                     value (%s, %s, %s, %s, %s, %s, %s, %s)'''
    cursor.execute(select_sql)
    new_results = cursor.fetchall()
    for res in new_results:
        try:
            cursor.execute(insert_sql, res)
            print(res, '-------------insert success')
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(res, e)


if __name__ == '__main__':
    single_relation_merge()