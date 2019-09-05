# -*- coding : utf-8 -*-
# coding: utf-8
# jieba分词尝试

import jieba
import jieba.posseg as pseg
import enum

train_list = ['《天津市城市绿化条例》实施细则', '安徽省绿化标准', '安徽省森林和野生动物类型自然保护区管理办法',
             '百色市古树名木保护管理办法', '包头市水土保持条例', '北京市郊区植树造林条例', '北京市人民政府办公厅关于进一步加强本市森林防火工作的通知',
             '北京市实施《中华人民共和国种子法》办法', '北京市实施《中华人民共和国种子法》办法', '财政部、国家税务总局关于林业税收政策问题的通知',
             '郴州市城市绿地和树木认建认养管理暂行办法', '大连市加快林业综合开发若干政策规定', '广东省森林防火管理规定',
             '广东省湿地保护条例', '贵州省贵阳市绿化条例', '国家发展计划委员会、财政部关于野生动植物进出口管理费收费标准的通知', '国家级公益林管理办法',
             '国家级文化生态保护区管理办法', '国家林业局关于发展油茶产业的意见', '河北省邯郸市城市绿化条例', '河北省湿地保护规定', '吉林省人民政府关于加强城市绿化工作的通知',
             '建设项目环境保护管理办法', '九江市城区绿地认养办法', '昆明市森林防火规定', '辽宁省本溪市环城森林公园管理条例', '辽宁省水土保持条例', '林业事业费管理办法']

test_list = ['内蒙古自治区环境保护条例', '内蒙古自治区人民政府办公厅关于印发退耕还林工程管理办法的通知', '内蒙古自治区森林草原防火办法',
             '宁夏回族自治区农业环境保护条例', '宁夏回族自治区森林防火办法', '农业野生植物保护办法', '青岛市林地保护管理规定', '青海省人民政府办公厅关于进一步加强森林病虫害防治工作的通知',
             '青海省湿地保护条例', '全国生态环境保护纲要', '森林和野生动物类型自然保护区管理办法']

dev_list = ['厦门市人民政府办公厅关于加强湿地保护管理的通知', '厦门市林地保护办法', '山东省森林资源管理条例', '山西省农业环境保护条例',
            '山西省实施《中华人民共和国森林法》办法', '陕西省华山风景名胜区条例', '陕西省水土保持条例', '深圳市生态公益林条例']

def demo():
    path = r"C:\Users\dhz1216\Desktop\wenben\全国生态环境保护纲要.txt"
    with open(path, encoding='gbk', errors='ignore') as f:
        line = f.readline().strip()
        while line:
            seg_list = jieba.cut(line, cut_all=False)
            print("/ ".join(seg_list))
            print('\n')
            line = f.readline().strip()


def process(path):
    with open(path, encoding='gbk', errors='ignore') as f:
        line = f.readline().strip()
        while line:
            words = pseg.cut(line)
            with open(r"C:\Users\dhz1216\Desktop\signal\dev.txt", "a") as w:
                for word, flag in words:
                    flag = flag_change(flag)
                    word = list(word)
                    for c in word:
                        if word.index(c) > 0:
                            flag = flag.replace('B', 'I')
                        w.write(c + " " + flag + '\n')
                    # print('%s %s' % (word, flag))
            line = f.readline().strip()


def flag_change(flag):
    filter_list = ['n', 'ns', 'nr', 'nt', 'nz']
    flag = str(flag)
    if flag in filter_list:
        if flag == 'n':
            flag = 'B-S'
        elif flag == 'nr':
            flag = 'B-PER'
        elif flag == 'ns':
            flag = 'B-LOC'
        elif flag == 'nt':
            flag = 'B-ORG'
        else:
            flag = 'B-O'
    else:
        flag = 'O'
    return flag


if __name__ == '__main__':
    # demo()
    for file in dev_list:
        path = r"C:\Users\dhz1216\Desktop\wenben"
        path = path + "\\" + file + ".txt"
        process(path)

    # process(path)