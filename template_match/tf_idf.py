#!/usr/bin/env python
# coding=utf-8
import re
from pyltp import Segmentor
import numpy as np
from gensim.models import Word2Vec
from data_resource import conn
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_DIR_PATH = "F:\\ltp_data_v3.4.0\\"
SEGMENTOR_MODEL = MODEL_DIR_PATH + "cws.model"  # LTP分词模型库

segmentor = Segmentor()  # 初始化分词实例
segmentor.load(SEGMENTOR_MODEL)     # 加载分词模型库

print('--开始加载词向量模型--')
model = Word2Vec.load('../model/forestry_law.model')
print('--词向量模型加载完毕--')


def get_template_and_segment(user_question):
    cn_reg = '^[\u4e00-\u9fa5]+$'
    cursor = conn.cursor()
    select_sql = '''select * from question_template'''
    cursor.execute(select_sql)
    results = list(cursor.fetchall())
    results.append(tuple((-1, user_question, '')))
    template_list = []
    for res in results:
        template_list.append(res[1])

    segment_result = []
    for template in template_list:
        words = list(segmentor.segment(template))
        temp_str = ""
        temp_list = []
        for word in words:
            if re.search(cn_reg, word):
                temp_list.append(word)
        temp_str = " ".join(temp_list)
        segment_result.append(temp_str)
    return segment_result, results


def calculate_tf_idf(segment_results):
    vectorizer = CountVectorizer()
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(vectorizer.fit_transform(segment_results))
    word = vectorizer.get_feature_names()
    weight = tfidf.toarray()
    # for i in range(len(weight)):
    #     print(u"-------这里输出第", i, u"类文本的词语tf-idf权重------")
    #     for j in range(len(word)):
    #         print(word[j], weight[i][j])
    return word, weight


def calculate_question_vec(segment_results, word, weight):
    vec_dict = {}
    for sentence_index in range(len(segment_results)):
        # print(weight[sentence_index])
        temp_words = segment_results[sentence_index].split(' ')
        vec = 0
        for w in temp_words:
            if w in word and w in model:
                w_index = word.index(w)
                power = weight[sentence_index][w_index]
                # print(print(sentence_index, w, power))
                word_vec = model[w]
                vec = vec + power * word_vec
        vec_dict.update({sentence_index: vec})
    return vec_dict


def cos_sim(vector_a, vector_b):
    """
    计算两个向量之间的余弦相似度
    :param vector_a: 向量 a
    :param vector_b: 向量 b
    :return: sim
    """
    vector_a = np.mat(vector_a)
    vector_b = np.mat(vector_b)
    num = float(vector_a * vector_b.T)
    denom = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    sim = num / denom
    return sim


def calculate_sim(vec_dict, template_results):
    vec_len = len(vec_dict)
    user_question_vec = vec_dict[vec_len - 1]
    vec_dict.pop(vec_len - 1)
    print(len(vec_dict))
    sim_dict = {}
    for template_index in vec_dict:
        temp_vec_list = []
        temp_vec = vec_dict[template_index]
        temp_vec_list.append(temp_vec)
        temp_vec_list.append(user_question_vec)
        sim = cos_sim(temp_vec, user_question_vec)
        sim_dict.update({template_index: sim})

    sim_res = sorted(sim_dict.items(), key=lambda x: x[1], reverse=True)
    template_num = sim_res[0][0]
    match_template = template_results[template_num][1]
    relation_type = template_results[template_num][2]
    return match_template, relation_type


if __name__ == '__main__':
    segment_results, template_results = get_template_and_segment("$Forest 需要对什么负责？")
    word, weight = calculate_tf_idf(segment_results)
    vec_dict = calculate_question_vec(segment_results, word, weight)
    calculate_sim(vec_dict, template_results)


