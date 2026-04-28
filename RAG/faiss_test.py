import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from red import load_outline

def list_to_matrix(l):

    #设置embedding模型
    embedding_model = "D:/Code/新生杯/sentence_transformers_models/all-MiniLM-L6-v2"
    model = SentenceTransformer(embedding_model)
    
    #将字符串列表转化为np矩阵
    embedding_matrix = model.encode(l, convert_to_tensor=False)
    embedding_matrix = [emb.astype('float32') for emb in embedding_matrix]
    embedding_matrix = np.array(embedding_matrix)

    return embedding_matrix

k = load_outline()
doc = []
for line in k.values():
    sen = line.split('。')
    for j in sen:
        doc.append(j)


 

query = '妙玉请刘姥姥喝茶'

def normalize(vector):
    vector /= np.linalg.norm(vector)
    return vector

doc_matrix = list_to_matrix(doc)
doc_matrix = normalize(doc_matrix)
d_d = doc_matrix.shape[1]
query_matrix = list_to_matrix(query)
query_matrix = np.array(query_matrix).reshape(1, -1)
query_matrix = normalize(query_matrix)
print(query)
d_q = query_matrix.shape[0]
    
index = faiss.IndexFlatIP(d_d)
index.add(doc_matrix)
distances, indices = index.search(query_matrix, 5)


print(distances)
print(indices)




