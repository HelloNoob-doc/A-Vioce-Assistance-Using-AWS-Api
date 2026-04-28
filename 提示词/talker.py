import asyncio
import json
import time
import boto3

# 全局状态变量（统一管理）
class State:
    outputting = False
    running = True
    competition_mode = False

# 修改后的invoke函数
async def invoke_async(text, is_competition=False):
    State.outputting = True
    State.competition_mode = is_competition
    
    try:
        # 构造请求（保留您添加的比赛模式逻辑）
        if State.competition_mode:
            text = f"""作为数据结构的专业讲师，请严格按以下要求用中文回答：
1. 分点论述（至少3点）
2. 包含代码时用标准格式
3. 给出代码示例的时候一定要用 c++ 语言
4. 输出两个版本，一个版本是针对完全没编程基础的新手，另一版本针对有基础的
问题：{text}"""
        else:
            text += ' 请用中文回答'

        body = {
            "prompt": f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>{text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>",
            "max_gen_len": 4096,
            "temperature": 0.5
        }
        
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        response = bedrock_runtime.invoke_model_with_response_stream(
            body=json.dumps(body),
            modelId="meta.llama3-70b-instruct-v1:0",
            accept="*/*",
            contentType="application/json"
        )
        
        # 非阻塞式处理输出
        for event in response['body']:
            if chunk := event.get('chunk'):
                data = json.loads(chunk['bytes'].decode())
                print(data['generation'], end='', flush=True)
                
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
    finally:
        State.outputting = False
        print("\n")  # 保持输出整洁

# 异步输入处理
async def input_loop():
    while State.running:
        if not State.outputting:
            user_input = await asyncio.get_event_loop().run_in_executor(
                None, input, "用户输入: "
            )
            if user_input.lower() == 'stop':
                State.running = False
            else:
                await invoke_async(user_input, State.competition_mode)

# 主函数
async def main():
    print("""*************************************************************
[INFO] 输入普通问题直接提问，比赛模式请添加 --competition
*************************************************************""")
    
    # 启动输入循环
    await input_loop()

# 启动程序
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序安全退出")