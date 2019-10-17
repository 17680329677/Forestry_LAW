from pyltp import Parser, SentenceSplitter, Segmentor, Postagger
from data_resource import conn
import networkx as nx
import matplotlib.pyplot as mp

MODEL_DIR_PATH = "E:\\ltp_data_v3.4.0\\"
SEGMENTOR_MODEL = MODEL_DIR_PATH + "cws.model"  # LTP分词模型库
POSTAGGER_MODEL = MODEL_DIR_PATH + "pos.model"  # LTP词性标注模型库
PARSER_MODEL = MODEL_DIR_PATH + "parser.model"  # LTP依存分析模型库

segmentor = Segmentor()  # 初始化分词实例
postagger = Postagger()  # 初始化词性标注实例
parser = Parser()  # 初始化依存句法分析实例

segmentor.load(SEGMENTOR_MODEL)     # 加载分词模型库
postagger.load(POSTAGGER_MODEL)     # 加载词性标注模型库
parser.load(PARSER_MODEL)  # 加载依存分析库


def test_pyltp_sentence_split():
    cursor = conn.cursor()
    select_sql = "select p_content from law_content_parse"
    cursor.execute(select_sql)
    results = cursor.fetchall()
    count = 0
    for res in results:
        if '：' in res[0] and count == 0:
            sens = SentenceSplitter.split(res[0])
            print('\n'.join(sens))
            count = count + 1


def test_pyltp():

    words = ['中国', '是', '一个', '自由', '、', '和平', '的', '国家']

    postags = ['ns', 'v', 'm', 'a', 'wp', 'a', 'u', 'n']

    arcs = parser.parse(words, postags)  # 句法分析，这里的words是分词的结果，postags是词性标注的结果

    print("\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs))  # 依存分析，


def ltp_networks():
    sentence = "任何单位和个人都有保护古树名木的义务"
    words = list(segmentor.segment(sentence))   # 分词
    postags = list(postagger.postag(words))     # 词性标注
    arcs = parser.parse(words, postags)     # 依存句法分析

    # 释放模型
    segmentor.release()
    postagger.release()
    parser.release()

    # 可视化
    G = nx.DiGraph()    # 无多重边有向图
    ah = [a.head for a in arcs]
    tree = ['ROOT'] + words
    # 添加节点和边
    for w in tree:
        G.add_node(w)
    for i in range(len(ah)):
        j = ah[i]
        G.add_edge(words[i], tree[j])

    # 可视化
    mp.rcParams['font.sans-serif'] = ['SimHei']     # 用黑体显示中文
    nx.draw(G, with_labels=True, node_color='lightgreen', font_size=15, node_size=2000, width=3, alpha=0.8)
    mp.show()


if __name__ == '__main__':
    # test_pyltp()
    ltp_networks()