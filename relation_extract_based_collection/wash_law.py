#!/usr/bin/env python
# coding=utf-8

from data_resource import conn


def wash_law(table_name):
    cursor = conn.cursor()
    select_sql = "select id, subject from %s" % table_name + " where subject like %s"
    cursor.execute(select_sql, ('%' + 'law' + '%',))
    results = cursor.fetchall()
    update_sql = "update %s " % table_name + "set subject = %s where id = %s"
    for res in results:
        subject = res[1][4:]
        cursor.execute(update_sql, (subject, res[0]))
        conn.commit()
        print(res[0], 'success')


if __name__ == '__main__':
    wash_law('new_forbid_relation')