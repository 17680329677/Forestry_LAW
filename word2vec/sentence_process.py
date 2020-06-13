# -*- coding : utf-8 -*-
# coding: utf-8
from pyltp import Parser, SentenceSplitter, Segmentor, Postagger
from gensim.models.word2vec import LineSentence
from gensim.models import Word2Vec
from data_resource import conn
import multiprocessing
import re
import numpy


MODEL_DIR_PATH = "F:\\ltp_data_v3.4.0\\"
SEGMENTOR_MODEL = MODEL_DIR_PATH + "cws.model"  # LTP分词模型库

segmentor = Segmentor()  # 初始化分词实例
segmentor.load(SEGMENTOR_MODEL)     # 加载分词模型库


def sentences_wash():
    cursor = conn.cursor()
    select_1_sql = '''select * from article_1'''
    select_2_sql = '''select * from article_2'''
    cursor.execute(select_1_sql)
    article_1 = cursor.fetchall()
    cursor.execute(select_2_sql)
    article_2 = cursor.fetchall()
    article = article_1 + article_2
    path_name = r'G:\Projects\train.txt'
    cn_reg = '^[\u4e00-\u9fa5]+$'
    with open(path_name, "a") as w:
        for art in article:
            content = str(art[2]).strip().replace('\n', '')
            content = re.sub("[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”《》〔〕：；！，。？、~@#￥%……&*（）]+", " ", content)
            words = list(segmentor.segment(content))
            line_list_new = []
            for word in words:
                if re.search(cn_reg, word):
                    line_list_new.append(word)
            w.write(' '.join(line_list_new) + '\n')
            print(content)


def read_news():
    file = r'E:\news_tensite_xml.dat'
    cn_reg = '^[\u4e00-\u9fa5]+$'
    title_reg = '<contenttitle>(.*)</contenttitle>'
    content_reg = '<content>(.*)</content>'
    path_name = r'G:\Projects\train.txt'
    with open(file, "r", encoding='gbk', errors='ignore') as f:
        with open(path_name, "a") as w:
            line = f.readline().replace('\n', '').strip()
            while line:
                title_patter = re.search(title_reg, line)
                content_patter = re.search(content_reg, line)
                if title_patter:
                    print(line)
                    title = title_patter.group(1)
                    title = re.sub("[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”《》〔〕：；！，。？、~@#￥%……&*（）]+", " ", title)
                    words = list(segmentor.segment(title))
                    line_list_new = []
                    for word in words:
                        if re.search(cn_reg, word):
                            line_list_new.append(word)
                    w.write(' '.join(line_list_new) + '\n')
                elif content_patter:
                    print(line)
                    content = content_patter.group(1)
                    content = re.sub("[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”《》〔〕：；！，。？、~@#￥%……&*（）]+", " ", content)
                    words = list(segmentor.segment(content))
                    line_list_new = []
                    for word in words:
                        if re.search(cn_reg, word):
                            line_list_new.append(word)
                    w.write(' '.join(line_list_new) + '\n')
                line = f.readline().replace('\n', '').strip()


def word_embedding_train():
    input_file_name = r'G:\Projects\train2.txt'
    print('begin to train')
    model = Word2Vec(LineSentence(input_file_name),
                     size=100,  # 词向量长度为100
                     window=5,
                     min_count=1,
                     sg=1,
                     workers=multiprocessing.cpu_count())
    print('train end and begin save')
    model.save('forestry_law.model')
    model.wv.save_word2vec_format('word2vec', binary=False)


def dp_based_similarity_core():
    cursor = conn.cursor()
    model = Word2Vec.load('../model/forestry_law.model')
    cn_reg = '^[\u4e00-\u9fa5]+$'
    select_sql = '''select * from dependency_parsing_result where parse_sentence = %s'''
    sentence1 = '各级林业主管部门负责木材经营加工的管理和监督。'
    sentence2 = '市园林主管部门应负责组织城市园林病虫害防治工作。'
    sentence2 = '市园林主管部门负责监督和技术指导。'
    # sentence2 = '没有违法所得或者违法所得不足三万元的，并处三千元以上三万元以下罚款。'
    cursor.execute(select_sql, (sentence1,))
    res1 = cursor.fetchall()
    group1 = []
    group2 = []
    for res in res1:
        front_word = res[7]
        relation = res[8]
        tail_word = res[9]
        if re.search(cn_reg, front_word) and re.search(cn_reg, tail_word):
            group1.append(tuple((front_word, relation, tail_word)))
        else:
            continue

    cursor.execute(select_sql, (sentence2,))
    res2 = cursor.fetchall()
    for res in res2:
        front_word = res[7]
        relation = res[8]
        tail_word = res[9]
        if re.search(cn_reg, front_word) and re.search(cn_reg, tail_word):
            group2.append(tuple((front_word, relation, tail_word)))
        else:
            continue
    max_len = max(len(group1), len(group2))
    print(max_len)
    sim_score = 0
    for pair1 in group1:
        for pair2 in group2:
            if pair1[1] == pair2[1]:
                if model[pair1[0]].any() and model[pair1[2]].any() and model[pair2[0]].any() and model[pair2[2]].any():
                    sim1 = model.similarity(pair1[0], pair2[0])
                    sim2 = model.similarity(pair1[2], pair2[2])
                    print(sim1)
                    print(sim2)
                    print('-----------------------------')
                    if sim1 > 0.35 and sim2 > 0.35:
                        sim_score = sim_score + 0.7*((sim1 + sim2)/2)/max_len
    print(sim_score)


if __name__ == '__main__':
    # sentences_wash()
    # word_embedding_train()
    # model = Word2Vec.load('../model/forestry_law.model')
    # print(model.similarity('公益林', '防护林'))
    # print(model.similarity('园林局', '林业局'))
    # read_news()
    dp_based_similarity_core()