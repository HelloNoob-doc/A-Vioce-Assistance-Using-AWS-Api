import asyncio
import json
import time
import sys
import boto3


from Combined_Selection import query_to_hint
from api_request_schema import api_request_list, get_model_ids



outputting=False
flag=True
flag2=True

# 定义关键词检索处理函数
def modify(text):

    text += "现在我将问你一个关于红楼梦的问题，请你根据我的参考文本和你的知识回答，如果我的参考文本与你的知识产生冲突，则以我的参考文本为主，并且需要回答我提供的拆解思路中的全部问题，请你根据这些来" + "。回答我的问题。" + "///我的问题是:" + text + query_to_hint(text)
    return text


#定义文字处理成音频的函数
def resMaker(stream2):#{a->c->a->a}
    prefix=''
    if stream2:
        for event in stream2:
            chunk=event.get('chunk')
            if chunk:
                chunk_obj=''
                text=''
                chunk_obj=json.loads(chunk.get('bytes').decode())
                text=str(chunk_obj['generation'])
                if '.' in text:
                    a = text.split('.')[:-1]
                    to_polly=''.join([prefix,'.'.join(a),'.'])
                    prefix=text.split('.')[-1]
                    print(to_polly,flush=True,end='')
                    yield to_polly
                else:
                    prefix=''.join([prefix,text])
        if prefix !='':
            print(prefix,flush=True,end='')
            yield f'{prefix}.'
        print('\n')

#{a->c->a}将输入文字投入bedrock
def invoke(text):
    global outputting
    global flag
    outputting=True
    text = modify(text)

    #形成输入格式
    body = api_request_list['meta.llama3-70b-instruct-v1']["body"]
    body['prompt'] = f"""
                    <|begin_of_text|>
                    <|start_header_id|>user<|end_header_id|>
                    {text}, please output in Chinese.
                    <|eot_id|>
                    <|start_header_id|>assistant<|end_header_id|>
                    """
    
    #投入bedrock, 获取输出信息，转成音频模式，读出
    try:
        body_json = json.dumps(body)
        bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
        response = bedrock_runtime.invoke_model_with_response_stream(
            body = body_json,
            modelId = "meta.llama3-70b-instruct-v1:0",
            accept = "*/*",
            contentType = "application/json"
        )
        stream2 = response.get('body')
        
        #转成音频
        a = resMaker(stream2)#{a->c->a->a}
        for i in a:
            i = ''
        
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(2)
        outputting = False
    time.sleep(1)
    outputting = False
    flag = True



#{a->a}流中持续打印
def start():
    while True:
        sys.stdin.readline().strip()
        shutdown = True


class get:
    global outputting
    global flag
    txt=[]
    def __init__(self):
        self.txt=[]
    
    async def get(self):
        global flag,flag2
        flag=False
        
        await asyncio.sleep(2)
        if not outputting:
            self.txt=input("用户:")
            if self.txt=='stop':
                flag2=False
                print("stop!")
            invoke(self.txt)
            self.txt=[]


info_text = f'''
*************************************************************
[INFO] Go ahead with the voice chat with Amazon Bedrock!
*************************************************************
'''
print(info_text)

#获取红楼梦知识库
# knowledgebase=load_text()



loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
task=get()
txt=[]

try:
    #运行入口{a}
   while True:
       if flag==True:
        loop.run_until_complete(task.get())
       if flag2==False:
           break

    
    #投出错误
except (KeyboardInterrupt, Exception) as e:
    print(e)

loop.close
print("程序结束")
