from BM25.BM25_Score import BM25
import jieba


from red import load_text
###
from BM25.BM25_searching_on_mainIdea import search_on_outline
###


knowledgement = load_text()


def slice_para(text):
    res = []
    for p in text.split('\n'):
        for p2 in p.split('\u3000\u3000'):
            res.append(p2)
    return res

################################################



#################################################

def BM25_on_para(query, chapter):
    
    
    text = slice_para(knowledgement['红楼梦'][chapter])
    
    bm25 = BM25(text)

    scores = bm25.get_scores(query=jieba.lcut(query))

    return(text[scores.index(max(scores))])

def get_para(query, ind):

    i = ind
    
    chapters = []
    for key in knowledgement['红楼梦'].keys():
        chapters.append(key)
    chapter = chapters[i]
   

    return BM25_on_para(query=query, chapter=chapter)