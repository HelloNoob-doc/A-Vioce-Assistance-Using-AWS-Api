
def dic_key_to_list(d):
    li = []
    for key in d.keys():
        li.append(key)
    return li

########################################################################################
def transform(s):
    res=""
    for i in range(0,len(s)):
        res+=s[i]
    return res


def getsentence(f):
    sentence=""
    char1=f.read(1)
    if not char1:
        return sentence
    if not char1=='\n':
        sentence+=char1
        while True:
            char=f.read(1)
            if char=='.' or char=='\n':
                if char=='.':
                    sentence += char
                    char2=f.read(1)
                    if char2=='\n':
                        sentence+=char2
                    elif char2=='\"':
                        sentence += char2
                        char3=f.read(1)
                        if char3=='\n':
                            sentence+=char3
                    else:
                        sentence += char2
                break
            else:
                sentence+=char
        return sentence
    else:
        sentence+=char1
        return sentence

def load_text():
    knowledgebase={}

    #设置三层
    text={}
    knowledgebase['红楼梦']=text

    title=""
    line=""
    count=0
    with open("D:/Code/新生杯/RAG/Original.txt",encoding='utf-8') as f:

        #读取第一行标题
        line=getsentence(f)
        text[line]=""
        title=line

        #反复读取直到读完
        while True:
        # for i in range(0,1000):
            line = getsentence(f)
            # print(line)

            #判断读完
            if not line:
                break
            #利用两个换行符判断是否为标题
            if count==3:
                if line:
                    title=line
                    text[title]=""
                    text[title]+=line
                count=0
            elif line=='\n':
                count+=1

            #正常情况下把文本加入目前的标题下
            else:
                text[title]+=line
    return knowledgebase



##################################################################################################


def provide_number_of_chapters(n):
    knowledgebase = load_text()

    #key_array
    key_array = []
    for chapter in knowledgebase['红楼梦'].keys():
        key_array.append(chapter)


    res = ""
    #select
    for i in range(0,n):
        res += knowledgebase["红楼梦"][key_array[i]]

    return res


def fetch_chapter(a):
    knowledgebase = load_text()
    chapters = []
    chapters = dic_key_to_list(knowledgebase['红楼梦'])

    return knowledgebase['红楼梦'][chapters[a]]


######################################################################################


def load_outline():


    with open('D:/Code/新生杯/RAG/Outline_2.txt', encoding='utf-8') as f:
        
        dic = {}
        index = 0
        text = ''

        while True:

            char = f.read(1)
             
            #判断文件是否读完
            if not char:
                dic[str(index)] = text
                break
            
            
            if not char == '\n':
                text += char

            #遇到换行符则入字典
            else :
                dic[str(index)] = text
                text = ''
                index += 1
                char = f.read(1)


        return dic
    





            