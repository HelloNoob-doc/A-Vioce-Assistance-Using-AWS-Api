# 关于红楼梦RAG的使用方法说明
## 环境变量配置
python版本: python 3.13.0

第三方库下载:

1.直接使用 requirements.txt 直接下载
```
pip install ./requirements.txt
```
包括了boto3==1.29.2, amazon-transcribe==0.6.2, numpy, faiss

## 使用说明

主要功能为提供带有专业知识库的问题解决。使用方法即为输入问题，大概10秒左右后回提供回答

## 项目结构
--root(RAG) <br>
$~~$--BM25 <br>
$~~~~$--BM25_paras.py<br>
$~~~~$--BM25_Score.py<br>
$~~~~$--BM25_searching_on_mainIdea.py<br>
$~~$myFaiss<br>
$~~~~$--faiss_doc_to_indice<br>
$~~$--clice_problem<br>
$~~~~$--slice_problem.py<br>
主目录中含有主要运行程序与相关必要文件