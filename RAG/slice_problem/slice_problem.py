import json
import time
import boto3


from api_request_schema import api_request_list



outputting=False
flag=True
flag2=True

#定义文字处理成音频的函数
def resMaker1(stream2):#{a->c->a->a}
    prefix=''
    if stream2:
        for event in stream2:
            chunk=event.get('chunk')
            if chunk:
                chunk_obj=''
                text=''
                chunk_obj=json.loads(chunk.get('bytes').decode())
                text=str(chunk_obj['generation'])
                if '.' in text and not text == '.':
                    a = text.split('.')[:-1]
                    to_polly=''.join([prefix,'.'.join(a),''])
                    prefix=text.split('.')[-1]
                    return to_polly
                else:
                    prefix=''.join([prefix,text])
        if prefix !='':
            return f'{prefix}.'
        print('\n')

#{a->c->a}将输入文字投入bedrock
def invoke1(text):
    global outputting
    global flag
    outputting=True

    # text = modify(text)

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
        
        #转成文本
        a = resMaker1(stream2)#{a->c->a->a}
        
        
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(2)
        outputting = False
    time.sleep(1)
    outputting = False
    flag = True
    return a




##########################################################################

def slice_problem(query):

    modified_query = '请你将以下问题分割为多个问题并输出，你本身不用回答原问题。问题为：'+query
 
    #第一层分割，AI的输出
    sliced_1 = invoke1(modified_query)

    #第二层分割，通过换行符分割，并去除多余符号
    sliced_2 = sliced_1.split('\n')
    for line in sliced_2:
        if not '.' in line:
            sliced_2.remove(line)
    for i in range(0,2):
        sliced_2.remove(sliced_2[0])    


    return sliced_2




    



    