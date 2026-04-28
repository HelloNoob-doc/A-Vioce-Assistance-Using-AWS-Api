import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from red import load_outline



###################################################################################

#将列表转化为np矩阵的函数
def list_to_matrix(l):

    #设置embedding模型
    embedding_model = "D:/Code/新生杯/sentence_transformers_models/all-MiniLM-L6-v2"
    model = SentenceTransformer(embedding_model)
    
    #将字符串列表转化为np矩阵
    embedding_matrix = model.encode(l, convert_to_tensor=False)
    embedding_matrix = [emb.astype('float32') for emb in embedding_matrix]
    embedding_matrix = np.array(embedding_matrix)

    return embedding_matrix

##################################################################################

def normalize(vector):
    vector /= np.linalg.norm(vector)
    return vector

#计算各文本与问题的相似度
def faiss_search(query, doc):


    doc_matrix = list_to_matrix(doc)
    doc_matrix = normalize(doc_matrix)
    d_d = doc_matrix.shape[1]
   

    query_matrix = list_to_matrix(query)
    query_matrix = np.array(query_matrix).reshape(1, -1)
    query_matrix = normalize(query_matrix)
    d_q = query_matrix.shape[0]
    

    index = faiss.IndexFlatIP(d_d)
    nlist = 5
    index_ivf = faiss.IndexIVFFlat(index, d_d, nlist)
    index_ivf.train(doc_matrix)
    index_ivf.add(doc_matrix)
    index_ivf.nprobe = 3
    
    distances, indices = index_ivf.search(query_matrix, 1)

    return distances, indices



######################################################################################

def search_on_sentences(query):
    
    distances = []
    sentences = []
    index = 0
    indexs = []

    k = load_outline()

################
#将doc切割成句子, 然后每章进行一次，记录最大相似度，然后比较得出最近章节

    doc = []
    for line in k.values():
        doc.append(line)
   

    for line in doc:
        sentence = line.split('。')

        for sen in sentence:
           
            sentences.append(sen)
            index += 1

        indexs.append(index)

    distance, indice = faiss_search(doc=sentences, query=query)

    indice_e = indice[0][0]

    for i in range(len(indexs)):
        if i == 0 :
            if indice_e <indexs[0]:
                return i
        else:
            if indice_e >= indexs[i-1] and indice_e < indexs[i]:
                return i



######################################################################################







