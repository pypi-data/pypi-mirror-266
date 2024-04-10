import re
from typing import List

#文本切分的方法
def split_text(text: str) -> List[str]:   ##此处需要进一步优化逻辑
    sentence_size = 100
    # text = re.sub(r"\n{3,}", r"\n", text)
    # text = re.sub('\s', " ", text)
    # text = re.sub("\n\n", "", text)

    text = re.sub(r'([;；.!?。！？\?])([^”’])', r"\1\n\2", text)  # 单字符断句符
    text = re.sub(r'(\.{6})([^"’”」』])', r"\1\n\2", text)  # 英文省略号
    text = re.sub(r'(\…{2})([^"’”」』])', r"\1\n\2", text)  # 中文省略号
    text = re.sub(r'([;；!?。！？\?]["’”」』]{0,2})([^;；!?，。！？\?])', r'\1\n\2', text)
    # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
    text = text.rstrip()  # 段尾如果有多余的\n就去掉它
    # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
    ls = [i for i in text.split("\n") if i]
    for ele in ls:
        if len(ele) > sentence_size:
            ele1 = re.sub(r'([,，.]["’”」』]{0,2})([^,，.])', r'\1\n\2', ele)
            ele1_ls = ele1.split("\n")
            for ele_ele1 in ele1_ls:
                if len(ele_ele1) > sentence_size:
                    ele_ele2 = re.sub(r'([\n]{1,}| {2,}["’”」』]{0,2})([^\s])', r'\1\n\2', ele_ele1)
                    ele2_ls = ele_ele2.split("\n")
                    for ele_ele2 in ele2_ls:
                        if len(ele_ele2) > sentence_size:
                            ele_ele3 = re.sub('( ["’”」』]{0,2})([^ ])', r'\1\n\2', ele_ele2)
                            ele2_id = ele2_ls.index(ele_ele2)
                            ele2_ls = ele2_ls[:ele2_id] + [i for i in ele_ele3.split("\n") if i] + ele2_ls[
                                                                                                   ele2_id + 1:]
                    ele_id = ele1_ls.index(ele_ele1)
                    ele1_ls = ele1_ls[:ele_id] + [i for i in ele2_ls if i] + ele1_ls[ele_id + 1:]

            id = ls.index(ele)
            ls = ls[:id] + [i for i in ele1_ls if i] + ls[id + 1:]
    return ls


def improve_segments(li : list[str],standard_len = 150):
    '''
        li :  文章原来切片
        standard_len : 合并后理想回复平均长度
        返回  : list[str] ，切片优化结果
    '''
    if type == False:
        return li
    else :
        ret = []
        for item in li:
            if ret == [] or len(ret[-1]) + len(item) >= int(standard_len * 1.2):
                ret.append(item)
            else :
                ret[-1] = ret[-1] + item
        if len(ret) >= 2 and len(ret[-1]) <= 50 :
            ret[-2] = ret[-2] + ret[-1]
            return ret[:-1]
        else :
            return ret


if __name__ == "__main__" :
    passage = r"2023年6月26日上午，受武汉光电国家研究中心能源功能实验室申燕教授邀请，日本福井大学陈竞鸢教授做客武汉光电论坛第186期，做了题为“受纳米技术启发的双电层电容概念”的报告。首先，申燕教授对陈竞鸢教授作了隆重介绍，包括其研究方向和学术贡献。党委副书记吴非教授为陈竞鸢教授授牌，随后报告正式开始。陈竞鸢教授介绍了他们研究室多年来在纳米电极、多相分散体系、双电层电容方面的研究成果。主要介绍了在使用纳米电极作为探针时，发现纳米区域反应的特异性可以解析为包括菲克第一定律延迟的现象，阐明了扩散的延迟反映了离子传导的延迟、并开发了可以直接检测动态行为的测量方法。对仅考虑离子分布引起的电容的Gouy-Chapman理论提出质疑，从理论和实验两个角度推进了双电层电容的理论研究。报告现场气氛活跃，研究中心及其他学院师生就热点问题与陈竞鸢教授一行进行了热烈的交流和讨论。陈竞鸢教授1982年毕业于天津科技大学。1996年获日本福井大学博士学位，师从青木光一教授。从事解决“电化学的基础问题”的研究。曾担任金泽大学理学院讲师，犹他大学化学系访问学者。之后，回到日本，在福井大学任副教授，并于2017年晋升为应用物理学正教授。"

    split_text_li = improve_segments( split_text(passage))

    for idx,item in enumerate(split_text_li) :
        print("切片{}为:{}".format(idx,item))