from BM25.BM25_paras import get_para
from BM25.BM25_searching_on_mainIdea import search_on_outline

from slice_problem.slice_problem import slice_problem

from myFaiss.faiss_doc_to_indice import search_on_sentences

from red import load_outline
#################################################################

outlinedic = load_outline()
outline = []
for line in outlinedic.values():
    outline.append(line)

#先通过余弦相似度索引再通过BM25索引
def faiss_BM25(query):
    global outline
    

    idx = search_on_sentences(query=query)
    
    return outline[idx], get_para(query=query, ind=idx)


#两步均通过BM25索引
def BM25_BM25(query):
    global outline
    
    idx = search_on_outline(query=query)

    return outline[idx], get_para(query=query, ind=idx)

#########################################################################


#最终整理，获取提示
def query_to_hint(query):


    problems = slice_problem(query)
    print(problems)
    lines_para_dic = {}
    p=' '

    for problem in problems:

        line, para = BM25_BM25(query)
        
        if line not in lines_para_dic.keys():
            lines_para_dic[line] = []
        if para not in lines_para_dic[line]:
            lines_para_dic[line].append(para)
        p += problem + '\n'


    hint = ''
    for key in lines_para_dic.keys():
        hint += key + '\n'
        for para in lines_para_dic[key]:
            hint += para + '\n'


    hint = '///拆解问题的方向:' + p + '///参考文本:' + hint

    return hint


            


    










