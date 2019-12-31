#!/usr/bin/env python
# coding=utf-8
from data_resource import conn


def get_complex_relation():
    select_sql = '''select * from extract_relation'''
    cursor = conn.cursor()
    cursor.execute(select_sql)
    results = cursor.fetchall()
    count = 0
    for res in results:
        if res[6] is not None and res[7] is not None and res[8] is not None:
            count = count + 1
            print("%s--%s--%s" % (res[6], res[7], res[8]))
    print(count)


if __name__ == '__main__':
    get_complex_relation()