import math
import jieba

from collections import Counter



class BM25:
    def __init__(self, doc, k1=1.2, b=0):
        
        #初始化各参数
        self.docs = doc
        self.k1 = k1
        self.b = b
        self.doc_len = [len(doc) for doc in self.docs]
        self.avgl = sum(self.doc_len) / len(self.docs)
        self.doc_freq = []
        self.idf = {}
        self.initialize()
    
    #计算逆文档频率
    def initialize(self):

        df = {}
        for doc in self.docs:
            self.doc_freq.append(Counter(doc))
            for word in set(doc):
                df[word] = df.get(word, 0) + 1

        for word, freq in df.items():
            self.idf[word] = math.log((len(self.docs) - freq +0.5) / (freq + 0.5) + 1)

    #计算BM25得分, query为列表!!!
    def score(self, doc, query):
        '''
        doc: 文档的索引
        '''
       

        score = 0.0
        for word in query:
            if word in self.doc_freq[doc]:
                freq = self.doc_freq[doc][word]

                score += ((self.idf[word]) * freq * (self.k1 + 1)) / (freq + self.k1 * (1 - self.b + self.b * self.doc_len[doc]))

        return score
    
    #query为列表!!!!
    def get_scores(self, query):


        scores = []
        for i in range(0,len(self.docs)):
            scores.append(self.score(i, query))
        
        return scores





def stri_to_lis(s):
    lis = []
    for char in s:
        lis.append(char)
    return lis


def dic_key_to_doc(d):
    doc = []
    for key in d['红楼梦'].keys():
        text = d['红楼梦'][key]
        text_list = stri_to_lis(text)
        doc.append(text_list)
    return doc

def return_top5(li):
    ind = []
    for i in range(0,5):
        ma = max(li)
        ind.append(li.index(ma))
        li.remove(ma)

    return ind

def dic_key_to_list(d):
    li = []
    for key in d.keys():
        li.append(key)
    return li


# doc = [ 
#     '妙玉用"成窑五彩小盖钟"招待贾母喝老君眉，却将刘姥姥用过的杯子要扔掉',
#     '刘姥姥二进荣国府，编"雪地抽柴女孩"故事，刚说"十七岁病死"贾府马棚便着火'
# ]

# query = '妙玉请刘姥姥喝茶'

# bm25 = BM25(doc=doc)

# scores = bm25.get_scores(query)
# print(scores.index(max(scores)))

