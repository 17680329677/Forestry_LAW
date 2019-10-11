# -*- coding : utf-8 -*-
# coding: utf-8
# 调用百度ai平台 做依存句法分析

from aip import AipNlp

APP_ID = '17235487'
API_KEY = 'zsGiGqSEioWdLbNsnvzKn9MC'
SECRET_KEY = 'MvQaujU4Of5sSHo7AgwRGNm4blM3ycs1'
client = AipNlp(APP_ID, API_KEY, SECRET_KEY)


def test_parse(text):
    dt = client.depParser(text)
    print(dt)


if __name__ == '__main__':
    text = '第九条　违反《条例》有下列行为之一的，除按照《条例》规定作出其他处理外，对责任者处200元以上1000元以下的罚款：' \
           '（一）在绿地内倾倒、排放污水、污物等，严重污染绿地的；' \
           '（二）擅自改变绿地使用性质、擅自临时占用绿地的。'
    test_parse(text)