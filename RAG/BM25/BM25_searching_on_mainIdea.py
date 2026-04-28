import jieba
import sys

from BM25.BM25_Score import BM25


from red import load_outline



def search_on_outline(query):

    query = jieba.lcut_for_search(query)
    
    doc = []
    dic = load_outline()
    for line in dic.values():
        line = jieba.lcut(line)
        doc.append(line)

   
    bm25 = BM25(doc=doc)
    

    scores = bm25.get_scores(query)
    

    
    return scores.index(max(scores))


