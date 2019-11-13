from pyltp import Parser, SentenceSplitter, Segmentor, Postagger, SementicRoleLabeller
from data_resource import conn
import networkx as nx
import matplotlib.pyplot as mp

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
    sentence = "本办法自发布之日起执行，由水利部负责解释。"
    sentence = "本办法由林业部负责解释。"
    sentence = "城市公共绿地的养护管理由市和区县城市绿化行政主管部门负责"
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
        # G.add_edge(words[i], tree[j])
        G.add_edge(tree[j], words[i])

    # 可视化
    mp.rcParams['font.sans-serif'] = ['SimHei']     # 用黑体显示中文
    nx.draw(G, with_labels=True, node_color='lightgreen', font_size=15, node_size=2000, width=3, alpha=0.8)
    fig = mp.gcf()
    fig.set_size_inches(12, 8)
    mp.show()


def role_labeller_test():       # 语义角色标注测试
    # sentence = "本办法由林业部负责解释。"
    # sentence = "城市公共绿地的养护管理由市和区县城市绿化行政主管部门负责"
    sentence = "项目开工须具备下列条件："
    words = list(segmentor.segment(sentence))
    postags = list(postagger.postag(words))  # 词性标注
    arcs = parser.parse(words, postags)  # 依存句法分析
    roles = labeller.label(words, postags, arcs)
    print(len(roles))
    for role in roles:
        print(role.index, "".join(["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end) for arg in role.arguments]))
    labeller.release()


if __name__ == '__main__':
    # test_pyltp()
    # ltp_networks()
    role_labeller_test()