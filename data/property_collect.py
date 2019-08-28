# -*- coding : utf-8 -*-
# coding: utf-8
# 法律内容属性抽取


def law_parse(path):
    law_content = {'name': '',              # 法规名称
                   'status': '',            # 时效性
                   'location_dep': '',      # 地区部门
                   'year': '',              # 年份
                   'pub_unit': '',          # 颁布单位
                   'pub_time': '',          # 颁布时间
                   'implement_time': '',    # 实施时间
                   'classify': '',          # 法规分类
                   'key_word': '',          # 关键词
                   'content_id': '',        # 文号
                   'credit_line': '',       # 题注
                   'catalogue': '',         # 目录摘要
                   'content': ''}           # 法规全文

    with open(path, "r", encoding='gbk', errors='ignore') as f:
        line = f.readline().strip()
        while line:
            if line.startswith('【法规名称】'):
                law_content['name'] = line.split('】')[-1].strip()
            elif line.startswith('【时效性】'):
                law_content['status'] = line.split('】')[-1].strip()
            elif line.startswith('【地区部门】'):
                law_content['location_dep'] = line.split('】')[-1].strip()
            elif line.startswith('【年份】'):
                law_content['year'] = line.split('】')[-1].strip()
            elif line.startswith('【颁布单位】'):
                law_content['pub_unit'] = line.split('】')[-1].strip()
            elif line.startswith('【颁布时间】'):
                law_content['pub_time'] = line.split('】')[-1].strip()
            elif line.startswith('【实施时间】'):
                law_content['implement_time'] = line.split('】')[-1].strip()
            elif line.startswith('【法规分类】'):
                law_content['classify'] = line.split('】')[-1].strip()
            elif line.startswith('【关键词】'):
                law_content['key_word'] = line.split('】')[-1].strip()
            elif line.startswith('【文号】'):
                law_content['content_id'] = line.split('】')[-1].strip()
            elif line.startswith('【题注】'):
                law_content['credit_line'] = line.split('】')[-1].strip()
            elif line.startswith('【目录摘要】'):
                law_content['catalogue'] = line.split('】')[-1].strip()
            elif line.startswith('【法规全文】'):
                law_content['content'] = line.split('】')[-1].strip()
                line = f.readline().strip()
                while line:
                    law_content['content'] += line
                    line = f.readline()
            line = f.readline().strip()
    return law_content


# if __name__ == '__main__':
#     law_parse(r"C:\Users\dhz1216\Desktop\wenben\“三北”防护林体系建设资金管理暂行办法.txt")