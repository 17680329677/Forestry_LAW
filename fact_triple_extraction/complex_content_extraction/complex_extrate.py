#!/usr/bin/env python
# coding=utf-8
from data_resource import conn


def write_to_file_for_observe():
    select_dp_sql = '''select * from dependency_parsing_result limit 0, 994'''
    cursor = conn.cursor()
    cursor.execute(select_dp_sql)
    dp_results = cursor.fetchall()
    for dp_res in dp_results:
        print(dp_res)
    pass


if __name__ == '__main__':
    write_to_file_for_observe()