#!/usr/bin/env python
# coding=utf-8
from data_resource import conn

SELECT_DP_SQL = '''select * from dependency_parsing_result 
                   where parse_sentence = %s and class = %s and sentence_id = %s'''
SELECT_SDP_SQL = '''select * from semantic_dependency_result 
                    where parse_sentence = %s and class = %s and sentence_id = %s'''
SELECT_SRL_SQL = '''select * from semantic_role_label_result 
                    where parse_sentence = %s and class = %s and sentence_id = %s'''
OUTPUT_FILE = "F:\\forestry_law_test\\article_1_complex\\test.txt"


def decode_srl_results(srl_results):
    srl_dict = dict()
    for srl in srl_results:
        verb = srl[7]
        if verb in srl_dict:
            srl_dict[verb].append(tuple((srl[8], srl[9])))
        else:
            srl_dict.update({verb: []})
            srl_dict[verb].append(tuple((srl[8], srl[9])))
    return srl_dict


def write_to_file_for_observe():
    query_for_parse_sentence = '''select complete_sentence, parse_sentence, class, sentence_id 
                                  from dependency_parsing_result group by parse_sentence order by id'''
    cursor = conn.cursor()
    cursor.execute(query_for_parse_sentence)
    parse_sentences = cursor.fetchall()

    with open(OUTPUT_FILE, "a") as w:
        for parse_sentence in parse_sentences:
            w.write("原句：" + parse_sentence[0] + '\n')
            w.write("解析：" + parse_sentence[1] + '\n')
            cursor.execute(SELECT_DP_SQL, (parse_sentence[1], parse_sentence[2], parse_sentence[3]))
            dp_results = cursor.fetchall()
            cursor.execute(SELECT_SDP_SQL, (parse_sentence[1], parse_sentence[2], parse_sentence[3]))
            sdp_results = cursor.fetchall()
            cursor.execute(SELECT_SRL_SQL, (parse_sentence[1], parse_sentence[2], parse_sentence[3]))
            srl_results = decode_srl_results(cursor.fetchall())
            w.write("-----------------------------依存句法分析结果---------------------------\n")
            for dp in dp_results:
                front_word = dp[7]
                relation_name = dp[8]
                tail_word = dp[9]
                w.write("%s -----(%s)---- %s\n" % (front_word, relation_name, tail_word))
            w.write("-----------------------------语义角色标注结果---------------------------\n")
            for verb in srl_results:
                w.write(verb + "：\t")
                for role_info in srl_results[verb]:
                    w.write(role_info[0] + '-' + role_info[1] + '\t')
                w.write('\n')
            w.write("-----------------------------语义依存分析结果---------------------------\n")
            for sdp in sdp_results:
                front_word = sdp[7]
                relation_name = sdp[8]
                tail_word = sdp[9]
                w.write("%s -----(%s)---- %s\n" % (front_word, relation_name, tail_word))
            w.write("\n********************************************************************************************\n")


def complex_extraction():
    query_for_parse_sentence = '''select complete_sentence, parse_sentence, class, sentence_id 
                                  from dependency_parsing_result 
                                  where is_complex = 1 and sentence_id > 9481 group by parse_sentence order by id'''
    cursor = conn.cursor()
    cursor.execute(query_for_parse_sentence)
    parse_sentences = cursor.fetchall()
    for parse_sentence in parse_sentences:
        complete_sentence = parse_sentence[0]
        parsing_sentence = parse_sentence[1]
        cursor.execute(SELECT_DP_SQL, (parse_sentence[1], parse_sentence[2], parse_sentence[3]))
        dp_results = cursor.fetchall()
        cursor.execute(SELECT_SDP_SQL, (parse_sentence[1], parse_sentence[2], parse_sentence[3]))
        sdp_results = cursor.fetchall()
        cursor.execute(SELECT_SRL_SQL, (parse_sentence[1], parse_sentence[2], parse_sentence[3]))
        srl_results = decode_srl_results(cursor.fetchall())
        # TODO: 调用复杂句关系抽取核心
        complex_extraction_core(dp_results, sdp_results, srl_results, complete_sentence, parsing_sentence)


def complex_extraction_core(dp_results, sdp_results, srl_results, complete_sentence, parsing_sentence):
    # TODO: 复杂句抽取关系核心
    # 1. 找到核心动词 以及 与 核心动词并列的动词
    core_verb = None
    coo_verb_list = []
    for dp_res in dp_results:
        if dp_res[7] == 'Root':
            core_verb = dp_res[9]
            break
    for dp_res in dp_results:
        if dp_res[8] == '并列关系-COO' and (core_verb == dp_res[7] or core_verb == dp_res[9]):
            if core_verb == dp_res[7]:
                coo_verb_list.append(dp_res[9])
            else:
                coo_verb_list.append(dp_res[7])
    # 2. 判断与核心动词之间是否存在主谓关系, 若存在，通过定中关系-ATT将主语做补全修饰
    core_subject = None     # 核心动词对应的主语，此处命名为核心主语core_subject
    for dp_res in dp_results:
        if dp_res[8] == '主谓关系-SBV' and dp_res[7] == core_verb:
            core_subject = dp_res[9]
    core_subject = subject_complete(core_subject, dp_results)       # 调用递归方式，将核心主语补全
    if core_subject is None:
        # TODO: 找不到主谓关系，也就是没有核心主语，此时如何处理待决定
        pass
    # 3. 结合dp 和 srl结果进行关系抽取
    # 3.1 抽取核心动词标注的语义角色对应的关系
    relation_list = []
    if core_verb in srl_results:
        core_srl_list = srl_results[core_verb]
        core_srl_dict = srl_info_extract(core_srl_list)
        print(parsing_sentence, '（核心主语：', core_subject, '）--', len(coo_verb_list))
        relation_list = core_comprehensive_analysis(core_verb,
                                                    core_srl_dict,
                                                    complete_sentence,
                                                    parsing_sentence,
                                                    core_subject)
    # 3.2 核心动词没有对应的语义角色 或者 与核心动词并列的动词列表不为空时，分析并列动词的语义角色关系
    # TODO: 核心动词没有对应的语义角色时，如何分析
    if coo_verb_list is not None and len(coo_verb_list) > 0:
        for coo_verb in coo_verb_list:
            if coo_verb in srl_results:
                print(coo_verb, ': ', srl_results[coo_verb])
                srl_info_dict = srl_info_extract(srl_results[coo_verb])
                relation_list = coo_comprehensive_analysis(relation_list,   # 核心动词关系分析后的关系列表
                                                           core_subject,
                                                           coo_verb,
                                                           srl_info_dict,)
    if relation_list is not None and len(relation_list) > 0:
        law_id = dp_results[0][1]           # 对应法律id
        content_class = dp_results[0][2]    # 文本来自article_1 or article_2
        chapter_id = dp_results[0][3]       # chapter_id
        sentence_id = dp_results[0][4]      # sentence_id
        # is_complex = dp_results[0][10]      # 是否是复杂句（包含子句)
        # 存入数据库
        save_relation(relation_list, law_id, content_class, chapter_id, sentence_id)
        print("=========================================================================================")
        print()


def save_relation(relation_list, law_id, content_class, chapter_id, sentence_id):
    cursor = conn.cursor()
    insert_sql = '''insert into extract_relation 
                    (law_id, class, chapter_id, sentence_id, is_contain, subject, relation, object)
                    value (%s, %s, %s, %s, %s, %s, %s, %s)'''
    for relation in relation_list:
        subject = relation[0]
        relation_name = relation[1]
        object = relation[2]
        is_contain = 0
        if object == '根据章节条款信息补全list':
            is_contain = 1
        try:
            cursor.execute(insert_sql, (law_id,
                                        content_class,
                                        chapter_id,
                                        sentence_id,
                                        is_contain,
                                        subject,
                                        relation_name,
                                        object))
            conn.commit()
            print(subject, relation_name, object, '--------saved--------')
        except Exception as e:
            conn.rollback()
            print('\033[1;32;41m' + relation + e + ': FAILED---------' + '\033[0m')


def subject_complete(subject, dp_results):          # 利用定中关系，使用递归调用将主语补全
    last_word = subject
    index = len(dp_results) - 1
    while index >= 0:
        if dp_results[index][8] == '定中关系-ATT' and last_word == dp_results[index][7]:
            subject = dp_results[index][9] + subject
            if index - 1 >= 0 and dp_results[index - 1][8] == '定中关系-ATT' and dp_results[index][9] == dp_results[index - 1][7]:
                last_word = dp_results[index][9]
        elif dp_results[index][7] == last_word and dp_results[index][8] == '主谓关系-SBV':
            subject = dp_results[index][9] + subject
        index = index - 1
    return subject


def srl_info_extract(srl_info_list):        # 整理语义角色标注结果，将某动词的语义结果整理为字典，key为语义角色
    srl_info_dict = dict()
    for srl_info in srl_info_list:
        role_label = srl_info[0]
        role_content = srl_info[1]
        if role_label in srl_info_dict:
            srl_info_dict[role_label].append(role_content)
        else:
            srl_info_dict.update({role_label: []})
            srl_info_dict[role_label].append(role_content)
    return srl_info_dict


# 核心动词语义角色标注关系分析
def core_comprehensive_analysis(verb, srl_info_dict, complete_sentence, parsing_sentence, core_subject):
    relation_list = []
    # 1. 有A0, A1, MNR
    if 'A0' in srl_info_dict and 'A1' in srl_info_dict and 'MNR' in srl_info_dict:
        method_subject = srl_info_dict['A0'][0]     # 获取主语(首实体)
        method_mnr = srl_info_dict['MNR'][0]        # 获取mnr方法
        method_object = srl_info_dict['A1'][0]      # 获取宾语(尾实体)
        relation_list.append(tuple((method_subject, verb, method_object)))
        if is_contain_sentence(method_mnr):
            contain_subject = method_object
            relation_list.append(tuple((contain_subject, method_mnr, '根据章节条款信息补全list')))
    # 2. 有A0, A1, 无MNR
    elif 'A0' in srl_info_dict and 'A1' in srl_info_dict and 'MNR' not in srl_info_dict:
        subject = srl_info_dict['A0'][0]
        relation = verb
        object = srl_info_dict['A1'][0]
        if is_contain_sentence(object):
            relation_list.append(tuple((subject, relation + object, '根据章节条款信息补全list')))
        else:
            relation_list.append(tuple((subject, relation, object)))
    # 3. 有A0，有MNR，无A1和其他
    elif 'A0' in srl_info_dict and 'MNR' in srl_info_dict and 'A1' not in srl_info_dict:
        subject = srl_info_dict['A0'][0]
        mnr = srl_info_dict['MNR'][0]
        if is_contain_sentence(mnr):
            beg_index = str(parsing_sentence).index(mnr)
            object = parsing_sentence[beg_index + len(mnr):].replace("：", "")
            if verb == object:      # 如果提取出的宾语（尾实体）就是当前动词本身，将MNR和宾语合起来作为关系
                relation_list.append(tuple((subject, mnr + object, '根据章节条款信息补全list')))
            elif verb in object:
                relation_list.append(tuple((subject, verb, str(object).replace(verb, ""))))
                relation_list.append(tuple((object, mnr, '根据章节条款信息补全list')))
    # 4. 没有A0，有MNR，有A1
    elif 'A0' not in srl_info_dict and 'MNR' in srl_info_dict and 'A1' in srl_info_dict:
        if srl_info_dict['A1'][0] == core_subject:
            relation_list.append(tuple((core_subject, srl_info_dict['MNR'][0] + verb, '根据章节条款信息补全list')))
        elif is_contain_sentence(srl_info_dict['A1'][0]):
            relation_list.append(tuple((srl_info_dict['A1'][0], verb, '根据章节条款信息补全list')))
    # 5. 只有'A0'
    elif 'A0' in srl_info_dict and 'A1' not in srl_info_dict and 'MNR' not in srl_info_dict:
        relation_list.append(tuple((core_subject, verb, '根据章节条款信息补全list')))
    # 6. 只有'A1'
    elif 'A0' not in srl_info_dict and 'A1' in srl_info_dict and 'MNR' not in srl_info_dict:
        if core_subject is None or core_subject == '':
            relation_list.append(tuple((srl_info_dict['A1'][0], verb, '根据章节条款信息补全list')))
        else:
            relation_list.append(tuple((core_subject, srl_info_dict['A1'][0], '根据章节条款信息补全list')))
    # 7. 只有'MNR'
    elif 'A0' not in srl_info_dict and 'A1' not in srl_info_dict and 'MNR' in srl_info_dict:
        if core_subject is not None and core_subject != '':
            relation_list.append(tuple((core_subject, verb + '方式(依据)', srl_info_dict['MNR'][0])))
        else:
            relation_list.append(tuple((verb + srl_info_dict['MNR'][0], '方式(依据)', '根据章节条款信息补全list')))
    return relation_list


# 并列动词语义角色关系分析
def coo_comprehensive_analysis(relation_list, core_subject, coo_verb, srl_info_dict):
    if 'A0' in srl_info_dict and 'A1' not in srl_info_dict and 'MNR' not in srl_info_dict:
        if core_subject is not None:
            common_str, common_len = get_num_of_common_substr(srl_info_dict['A0'][0], core_subject)
        else:
            common_str = ''
            common_len = 0
        if common_len >= 2 and (is_contain_sentence(srl_info_dict['A0'][0]) or is_contain_sentence(coo_verb)):
            subject = srl_info_dict['A0'][0].replace(common_str, core_subject)
            # TODO: 判断是否是复杂句
            relation_list.append(tuple((subject, coo_verb, '根据章节条款信息补全list')))
        elif len(relation_list) > 0 and (is_contain_sentence(srl_info_dict['A0'][0]) or is_contain_sentence(coo_verb)):
            coo_subject = relation_list[-1][2]
            relation_list.append(tuple((coo_subject, srl_info_dict['A0'][0] + coo_verb, '根据章节条款信息补全list')))
    elif 'A0' not in srl_info_dict and 'A1' in srl_info_dict and 'MNR' not in srl_info_dict:
        if relation_list is not None and \
                len(relation_list) != 0 and \
                (is_contain_sentence(srl_info_dict['A1'][0]) or is_contain_sentence(coo_verb)):
            coo_subject = relation_list[-1][2]
            relation_list.append(tuple((coo_subject, coo_verb + srl_info_dict['A1'][0], '根据章节条款信息补全list')))
        else:
            relation_list.append(tuple((core_subject, coo_verb + srl_info_dict['A1'][0], '根据章节条款信息补全list')))
    return relation_list


def is_contain_sentence(content):
    complex_words = ['下列', '以下', '包括', '如下']
    if '为' == content[-1]:
        return True
    for word in complex_words:
        if word in content:
            return True
    return False


def get_num_of_common_substr(str1, str2):
    lstr1 = len(str1)
    lstr2 = len(str2)
    record = [[0 for i in range(lstr2 + 1)] for j in range(lstr1 + 1)]  # 多一位
    maxNum = 0  # 最长匹配长度
    p = 0  # 匹配的起始位

    for i in range(lstr1):
        for j in range(lstr2):
            if str1[i] == str2[j]:
                # 相同则累加
                record[i + 1][j + 1] = record[i][j] + 1
                if record[i + 1][j + 1] > maxNum:
                    # 获取最大匹配长度
                    maxNum = record[i + 1][j + 1]
                    # 记录最大匹配长度的终止位置
                    p = i + 1
    return str1[p - maxNum:p], maxNum


if __name__ == '__main__':
    # write_to_file_for_observe()
    complex_extraction()