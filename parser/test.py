"""
依存句法分析
"""
import pyltp
from pyltp import Parser


if __name__ == '__main__':

    math_path = "E:\\ltp_data_v3.4.0\\parser.model"  # LTP依存分析模型库

    parser = Parser()  # 初始化实例

    parser.load(math_path)  # 加载依存分析库

    words = ['中国', '是', '一个', '自由', '、', '和平', '的', '国家']

    postags = ['ns', 'v', 'm', 'a', 'wp', 'a', 'u', 'n']

    arcs = parser.parse(words, postags)  # 句法分析，这里的words是分词的结果，postags是词性标注的结果

    print("\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs))  # 依存分析，
