from graphviz import Digraph
from pyltp import Parser, SentenceSplitter, Segmentor, Postagger

MODEL_DIR_PATH = "F:\\ltp_data_v3.4.0\\"
SEGMENTOR_MODEL = MODEL_DIR_PATH + "cws.model"  # LTP分词模型库
POSTAGGER_MODEL = MODEL_DIR_PATH + "pos.model"  # LTP词性标注模型库
PARSER_MODEL = MODEL_DIR_PATH + "parser.model"  # LTP依存分析模型库

segmentor = Segmentor()  # 初始化分词实例
postagger = Postagger()  # 初始化词性标注实例
parser = Parser()  # 初始化依存句法分析实例

segmentor.load(SEGMENTOR_MODEL)  # 加载分词模型库
postagger.load(POSTAGGER_MODEL)  # 加载词性标注模型库
parser.load(PARSER_MODEL)  # 加载依存分析库


def syntactic_test():
    sentence = "本办法自发布之日起执行，由水利部负责解释。"
    sentence = "本办法由林业部负责解释。"
    sentence = "林地的所有权分为国家所有和集体所有。"
    sentence = "县级以上人民政府应当科学合理地划定湿地生态红线，确保湿地生态功能不降低、面积不减少、性质不改变"
    sentence = "因保护湿地给湿地所有者或者经营者合法权益造成损失的，应当依法给予补偿。"
    sentence = "任何单位和个人不得在城市绿线范围内进行拦河截溪、取土采石、设置垃圾堆场、排放污水以及其他对生态环境构成破坏的活动。"
    sentence = "各级林业主管部门负责木材经营加工的管理和监督。"
    sentence = "省环境保护行政主管部门根据保护农业生态环境的需要，制定地方农业生态环境标准。"
    sentence = "植保植检站是本市农业植物检疫机构, 负责本市农业植物检疫工作。"
    sentence = "城市绿化行政主管部门根据市区两级绿化管养分工，负责行政区域内的绿化管理工作。"
    sentence = "镇人民政府负责本辖区的农业环境质量。"
    sentence = "《良种壮苗合格证》应当存入造林单位的造林档案。"
    sentence = "国有建设用地应当实行有偿使用。"
    words = list(segmentor.segment(sentence))  # 分词
    postags = list(postagger.postag(words))  # 词性标注
    arcs = parser.parse(words, postags)  # 依存句法分析

    dot = Digraph(comment='The Round Table')
    arc_head = [a.head for a in arcs]
    arc_relation = [a.relation for a in arcs]
    tree = ['ROOT'] + words
    postags = ['none'] + postags
    for i in range(len(tree)):
        if postags[i] == 'v':
            dot.node('N' + str(i), tree[i] + '(' + postags[i] + ')', fontname="Microsoft YaHei", color='red')
        elif postags[i] == 'n':
            dot.node('N' + str(i), tree[i] + '(' + postags[i] + ')', fontname="Microsoft YaHei", color='blue')
        elif postags == 'ni':
            dot.node('N' + str(i), tree[i] + '(' + postags[i] + ')', fontname="Microsoft YaHei", color='yellow')
        else:
            dot.node('N' + str(i), tree[i] + '(' + postags[i] + ')', fontname="Microsoft YaHei")
    for i in range(len(arc_head)):
        j = arc_head[i]
        dot.edge('N' + str(j), 'N' + str(i + 1), label=arc_relation[i])
    dot.view()


def graphviz_try():
    dot = Digraph(comment='The Round Table')
    dot.node('A', 'ROOT')
    dot.node('B', 'LEFT')
    dot.node('L', 'RIGHT')
    dot.edges(['AB', 'AL'])
    dot.edge('B', 'L', constraint='false')
    dot.view()


if __name__ == '__main__':

    # graphviz_try()

    syntactic_test()