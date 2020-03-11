# -*- coding : utf-8 -*-
# coding: utf-8
from pyltp import Parser, SentenceSplitter, Segmentor, Postagger
from gensim.models.word2vec import LineSentence
from gensim.models import Word2Vec
from data_resource import conn
import multiprocessing
import re


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


if __name__ == '__main__':
    # sentences_wash()
    # word_embedding_train()
    model = Word2Vec.load('../model/forestry_law.model')
    print(model.similarity('公益林', '防护林'))
    print(model.similarity('园林局', '林业局'))
    # read_news()