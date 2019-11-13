# -*- coding : utf-8 -*-
# coding: utf-8
# 句法分析的核心代码逻辑
from data_resource import conn
from pyltp import Parser, SentenceSplitter, Segmentor, Postagger, SementicRoleLabeller
from graphviz import Digraph
import time
import string


MODEL_DIR_PATH = "E:\\ltp_data_v3.4.0\\"
SEGMENTOR_MODEL = MODEL_DIR_PATH + "cws.model"  # LTP分词模型库
POSTAGGER_MODEL = MODEL_DIR_PATH + "pos.model"  # LTP词性标注模型库
PARSER_MODEL = MODEL_DIR_PATH + "parser.model"  # LTP依存分析模型库
ROLE_LABELLER_MODEL = MODEL_DIR_PATH + "pisrl_win.model"    # LTP语义角色标注模型库

segmentor = Segmentor()  # 初始化分词实例
postagger = Postagger()  # 初始化词性标注实例
parser = Parser()  # 初始化依存句法分析实例
labeller = SementicRoleLabeller()   # 初始化语义角色标注实例

segmentor.load(SEGMENTOR_MODEL)     # 加载分词模型库
postagger.load(POSTAGGER_MODEL)     # 加载词性标注模型库
parser.load(PARSER_MODEL)  # 加载依存分析库
labeller.load(ROLE_LABELLER_MODEL)      # 加载语义角色标注库


def test():
    select_sql = '''select * from sentences where is_single = 0 limit 0, 5'''
    cursor = conn.cursor()
    cursor.execute(select_sql)
    complex_sentences = cursor.fetchall()
    start_time = time.time()
    for sentence in complex_sentences:
        content = sentence[3]
        main_content = str(content).split('：')[0] + '：'
        sub_contents = str(content).split('：')[1].split('\n')
        words = list(segmentor.segment(main_content))
        postags = list(postagger.postag(words))
        arcs = parser.parse(words, postags)
        roles = labeller.label(words, postags, arcs)
        print(main_content)
        for index in range(len(roles)):
            role = roles[index]
            print(str(index + 1), '---核心动词为：', words[role.index])
            for arg in role.arguments:
                print(arg.name, '：', ''.join(words[arg.range.start: arg.range.end + 1]))
        print('******************************************************************************************')
        for role in roles:
            print(role.index,
                  "".join(["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end) for arg in role.arguments]))
        print('\n', '=============================================================', '\n')

    end_time = time.time()
    print("用时：", end_time - start_time, 's')


def test_role_labeller():
    sentence = "县级水利部门为项目的责任主体，对项目建设的全过程负总责。其主要职责为："
    words = list(segmentor.segment(sentence))
    postags = list(postagger.postag(words))
    arcs = parser.parse(words, postags)
    roles = labeller.label(words, postags, arcs)
    for role in roles:
        print(role.index,
              "".join(["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end) for arg in role.arguments]))
    # labeller.release()
    # dot = Digraph(comment='The Round Table')
    # arc_head = [a.head for a in arcs]
    # arc_relation = [a.relation for a in arcs]
    # tree = ['ROOT'] + words
    # postags = ['none'] + postags
    # for i in range(len(tree)):
    #     if postags[i] == 'v':
    #         dot.node('N' + str(i), tree[i] + '(' + postags[i] + ')', fontname="Microsoft YaHei", color='red')
    #     elif postags[i] == 'n':
    #         dot.node('N' + str(i), tree[i] + '(' + postags[i] + ')', fontname="Microsoft YaHei", color='blue')
    #     elif postags == 'ni':
    #         dot.node('N' + str(i), tree[i] + '(' + postags[i] + ')', fontname="Microsoft YaHei", color='yellow')
    #     else:
    #         dot.node('N' + str(i), tree[i] + '(' + postags[i] + ')', fontname="Microsoft YaHei")
    # for i in range(len(arc_head)):
    #     j = arc_head[i]
    #     dot.edge('N' + str(j), 'N' + str(i + 1), label=arc_relation[i])
    # dot.view()


def complex_main_sentence_analysis():       # 非单句主句依存句法分析以及语义角色标注，结果入库

    start_time = time.time()

    select_sql = '''select * from sentences where is_single = 0'''
    cursor = conn.cursor()
    cursor.execute(select_sql)
    complex_sentences = cursor.fetchall()
    for sentence in complex_sentences:
        sentence_id = sentence[0]
        main_sentence = str(sentence[3]).strip().split('：')[0] + '：'
        origin_words = list(segmentor.segment(main_sentence))      # 分词
        origin_postags = list(postagger.postag(origin_words))         # 词性标注
        arcs = parser.parse(origin_words, origin_postags)         # 依存句法分析
        roles = labeller.label(origin_words, origin_postags, arcs)        # 语义角色标注

        print('语义角色标注--------', str(len(roles)))     # 语义角色标注信息提取并存入数据库
        core_verb_list = list()
        insert_role_label_sql = '''insert into role_label (sentence_id, arg_name, arg_start, arg_end, core_verb_index) value (%s, %s, %s, %s, %s)'''
        for role in roles:
            core_verb_list.append(role.index)       # 建立核心动词索引列表
            for arg in role.arguments:
                arg_name = arg.name
                arg_start = arg.range.start
                arg_end = arg.range.end
                # 将语义角色标注信息插入到role_label表中
                try:
                    cursor.execute(insert_role_label_sql, (sentence_id, arg_name, arg_start, arg_end, role.index))
                    conn.commit()
                    print(str(sentence_id), main_sentence, '-----------', origin_words[role.index], arg_name, '-------------SUCCESS')
                except Exception as e:
                    conn.rollback()
                    print('\033[1;32;41m' + str(sentence_id) + main_sentence + e + ': ---------FAILED---------' + '\033[0m')

        # 提取动词信息，并插入数据库
        print('提取动词信息-------------------------------------------')
        insert_verb_sql = '''insert into verb (sentence_id, part_of_speech, loc_index, is_core) value (%s, %s, %s, %s)'''
        for index in range(len(origin_words)):
            if origin_postags[index] == 'v':
                is_core = 0
                if index in core_verb_list:
                    is_core = 1
                try:
                    cursor.execute(insert_verb_sql, (sentence_id, 'v', index, is_core))
                    conn.commit()
                    print(str(index), '--', origin_words[index], '-----------------SUCCESS')
                except Exception as e:
                    conn.rollback()
                    print('\033[1;32;41m' + str(index) + origin_words[index] + e + ': ---------FAILED---------' + '\033[0m')

        # 提取其他词和动词的关系，没有关系的设为NONE
        arc_head = [a.head for a in arcs]
        arc_relation = [a.relation for a in arcs]
        tree_node_list = ['ROOT'] + origin_words
        postags = ['NONE'] + origin_postags
        for i in range(len(arc_head)):
            j = arc_head[i]
            head_index = j - 1
            tail_index = i
            relation = arc_relation[i]

            if arc_relation[i] == 'HED':
                update_verb_sql = '''update verb set is_head = 1 where sentence_id = %s and loc_index = %s'''
                print('更新根动词情况：')
                try:
                    cursor.execute(update_verb_sql, (sentence_id, i))
                    conn.commit()
                    print('根动词-----index: ', str(i), '----', origin_words[i], '-----UPDATE SUCCESS')
                except Exception as e:
                    conn.rollback()
                    print('\033[1;32;41m' + '根动词---' + str(i) + origin_words[i] + e + ': ---------FAILED---------' + '\033[0m')
                continue

            if head_index not in core_verb_list and tail_index not in core_verb_list:
                continue
            elif head_index in core_verb_list:
                part_of_speech = postags[i + 1]
                core_verb_index = head_index
                word = origin_words[i]
                loc = 'tail'
            else:
                part_of_speech = postags[j]
                core_verb_index = tail_index
                word = tree_node_list[j]
                loc = 'head'
            # TODO:----------------------------数据库插入操作--------------------------------------------
            insert_words_sql = '''insert into words (sentence_id, part_of_speech, core_verb_index, relation, word, head_or_tail) 
                                  value (%s, %s, %s, %s, %s, %s)'''
            try:
                cursor.execute(insert_words_sql, (sentence_id, part_of_speech, core_verb_index, relation, word, loc))
                conn.commit()
                print(tree_node_list[j], postags[j], '----', origin_words[i], postags[i + 1], relation, '-----SUCCESS')
            except Exception as e:
                conn.rollback()
                print('\033[1;32;41m', tree_node_list[j], postags[j], '----', origin_words[i], postags[i + 1], relation, '-----FAILED', e, '\033[0m')

        print('\n', '===============================================================', '\n')

    end_time = time.time()
    print('处理', str(len(complex_sentences)), '条数据的总耗时为：', str(end_time - start_time), 's')


def update_article():
    select_article_1_sentence = '''select * from article_1_sentence where is_single = 0'''
    select_article_2_sentence = '''select * from article_2_sentence where is_single = 0'''
    update_article_1_sentence = '''update article_1_sentence set content = %s where id = %s'''
    update_article_2_sentence = '''update article_2_sentence set content = %s where id = %s'''
    cursor = conn.cursor()
    cursor.execute(select_article_1_sentence)
    article_1_sentences = cursor.fetchall()
    for sentence in article_1_sentences:
        sentence_id = sentence[0]
        content = sentence[3] + '：'
        try:
            cursor.execute(update_article_1_sentence, (content, sentence_id))
            conn.commit()
            print(str(sentence_id), '-1-', content, '------------------SUCCESS')
        except Exception as e:
            conn.rollback()
            print('\033[1;32;41m', str(sentence_id), '-2-', e, '-------FAILED', '\033[0m')

    print('\n', '=============================================================================================', '\n')

    cursor.execute(select_article_2_sentence)
    article_2_sentences = cursor.fetchall()
    for sentence in article_2_sentences:
        sentence_id = sentence[0]
        content = sentence[3] + '：'
        try:
            cursor.execute(update_article_2_sentence, (content, sentence_id))
            conn.commit()
            print(str(sentence_id), '-2-', content, '------------------SUCCESS')
        except Exception as e:
            conn.rollback()
            print('\033[1;32;41m', str(sentence_id), '-2-', e, '-------FAILED', '\033[0m')


if __name__ == '__main__':

    # test()

    # test_role_labeller()

    # complex_main_sentence_analysis()

    update_article()