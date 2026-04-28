import asyncio
import json
import os
import time
import pyaudio
import sys
import boto3
import sounddevice
from concurrent.futures import ThreadPoolExecutor
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent, TranscriptResultStream
from langdetect import detect
from api_request_schema import api_request_list, get_model_ids

# 环境变量和配置
model_id = os.getenv('MODEL_ID', 'meta.llama3-70b-instruct-v1')
aws_region = os.getenv('AWS_REGION', 'us-east-1')

if model_id not in get_model_ids():
    print(f'Error: Model ID {model_id} is not valid. Set MODEL_ID env var to one of {get_model_ids()}.')
    sys.exit(0)

api_request = api_request_list[model_id]
config = {
    'log_level': 'debug',  # 日志级别：info, debug, none
    'region': aws_region,
    'polly': {
        'Engine': 'neural',
        'LanguageCode': 'en-US',  
        'VoiceId': 'Joanna', 
        'OutputFormat': 'pcm',
    },
    'bedrock': {
        'api_request': api_request
    },
    'language_mapping': {
        'en': {'transcribe_language': 'en-US', 'polly_language': 'en-US', 'polly_voice': 'Joanna'},
        'zh': {'transcribe_language': 'zh-CN', 'polly_language': 'cmn-CN', 'polly_voice': 'Zhiyu'},
    }
}

p = pyaudio.PyAudio()
bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name=config['region'])
polly = boto3.client('polly', region_name=config['region'])
transcribe_streaming = TranscribeStreamingClient(region=config['region'])

# 日志打印函数
def printer(text, level):
    if config['log_level'] == 'info' and level == 'info':
        print(text)
    elif config['log_level'] == 'debug' and level in ['info', 'debug']:
        print(text)

# 语言选择函数
def select_language():
    while True:
        language = input("请选择语言 (输入 'zh' 选择中文，输入 'en' 选择英文): ").strip().lower()
        if language in ['zh', 'en']:
            return language
        else:
            print("输入无效，请重新输入 'zh' 或 'en'。")

# 更新配置
def update_language_config(language):
    if language in config['language_mapping']:
        language_config = config['language_mapping'][language]
        config['polly']['LanguageCode'] = language_config['polly_language']
        config['polly']['VoiceId'] = language_config['polly_voice']
        global transcribe_streaming
        transcribe_streaming = TranscribeStreamingClient(region=config['region'])

# 用户输入管理
class UserInputManager:
    shutdown_executor = False
    executor = None

    @staticmethod
    def set_executor(executor):
        UserInputManager.executor = executor

    @staticmethod
    def start_shutdown_executor():
        UserInputManager.shutdown_executor = False
        raise Exception()  # 用于关闭 executor

    @staticmethod
    def start_user_input_loop():
        while True:
            sys.stdin.readline().strip()
            printer(f'[DEBUG] User input to shut down executor...', 'debug')
            UserInputManager.shutdown_executor = True

    @staticmethod
    def is_executor_set():
        return UserInputManager.executor is not None

    @staticmethod
    def is_shutdown_scheduled():
        return UserInputManager.shutdown_executor

# Bedrock 模型封装
class BedrockModelsWrapper:
    @staticmethod
    def define_body(text, language):  # 移除默认语言
        model_id = config['bedrock']['api_request']['modelId']
        model_provider = model_id.split('.')[0]
        body = config['bedrock']['api_request']['body']

        if model_provider == 'meta':
            if 'llama3' in model_id:
                body['prompt'] = f"""
                    <|begin_of_text|>
                    <|start_header_id|>user<|end_header_id|>
                    {text}, please output in {language}.
                    <|eot_id|>
                    <|start_header_id|>assistant<|end_header_id|>
                    """
            else:
                body['prompt'] = f"<s>[INST] {text}, please output in {language}. [/INST]"
        return body

    @staticmethod
    def get_stream_chunk(event):
        return event.get('chunk')

    @staticmethod
    def get_stream_text(chunk):
        model_id = config['bedrock']['api_request']['modelId']
        model_provider = model_id.split('.')[0]

        chunk_obj = json.loads(chunk.get('bytes').decode())
        if model_provider == 'meta':
            return chunk_obj['generation']
        elif model_provider == 'anthropic':
            if "claude-3" in model_id:
                if chunk_obj['type'] == 'content_block_delta':
                    return chunk_obj['delta']['text']
            else:
                return chunk_obj['completion']
        elif model_provider == 'cohere':
            return ' '.join([c["text"] for c in chunk_obj['generations']])
        elif model_provider == 'mistral':
            return chunk_obj['outputs'][0]['text']
        else:
            raise NotImplementedError('Unknown model provider.')

# Bedrock 封装
class BedrockWrapper:
    def __init__(self):
        self.speaking = False

    def is_speaking(self):
        return self.speaking

    def invoke_bedrock(self, text, language):  # 移除默认语言
        printer('[DEBUG] Bedrock generation started', 'debug')
        self.speaking = True

        body = BedrockModelsWrapper.define_body(text, language)  # 传递用户选择的语言
        printer(f"[DEBUG] Request body: {body}", 'debug')

        try:
            body_json = json.dumps(body)
            response = bedrock_runtime.invoke_model_with_response_stream(
                body=body_json,
                modelId=config['bedrock']['api_request']['modelId'],
                accept=config['bedrock']['api_request']['accept'],
                contentType=config['bedrock']['api_request']['contentType']
            )

            bedrock_stream = response.get('body')
            audio_gen = to_audio_generator(bedrock_stream)

            reader = Reader()
            for audio in audio_gen:
                reader.read(audio)

            reader.close()

        except Exception as e:
            print(e)
            time.sleep(2)
            self.speaking = False

        time.sleep(1)
        self.speaking = False
        printer('\n[DEBUG] Bedrock generation completed', 'debug')

# 音频生成器
def to_audio_generator(bedrock_stream):
    prefix = ''
    for event in bedrock_stream:
        chunk = BedrockModelsWrapper.get_stream_chunk(event)
        if chunk:
            text = BedrockModelsWrapper.get_stream_text(chunk)
            if '.' in text:
                a = text.split('.')[:-1]
                to_polly = ''.join([prefix, '.'.join(a), '. '])
                prefix = text.split('.')[-1]
                print(to_polly, flush=True, end='')
                yield to_polly
            else:
                prefix = ''.join([prefix, text])

    if prefix != '':
        print(prefix, flush=True, end='')
        yield f'{prefix}.'

    print('\n')

# 音频播放器
class Reader:
    def __init__(self):
        self.polly = boto3.client('polly', region_name=config['region'])
        self.audio = p.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True)
        self.chunk = 1024

    def read(self, data):
        response = self.polly.synthesize_speech(
            Text=data,
            Engine=config['polly']['Engine'],
            LanguageCode=config['polly']['LanguageCode'],
            VoiceId=config['polly']['VoiceId'],
            OutputFormat=config['polly']['OutputFormat'],
        )

        stream = response['AudioStream']
        while True:
            if UserInputManager.is_executor_set() and UserInputManager.is_shutdown_scheduled():
                UserInputManager.start_shutdown_executor()

            data = stream.read(self.chunk)
            self.audio.write(data)
            if not data:
                break

    def close(self):
        time.sleep(1)
        self.audio.stop_stream()
        self.audio.close()

# 事件处理器
class EventHandler(TranscriptResultStreamHandler):
    text = []
    last_time = 0
    sample_count = 0
    max_sample_counter = 4

    def __init__(self, transcript_result_stream: TranscriptResultStream, bedrock_wrapper, current_language):
        super().__init__(transcript_result_stream)
        self.bedrock_wrapper = bedrock_wrapper
        self.current_language = current_language

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        if not self.bedrock_wrapper.is_speaking():
            if results:
                for result in results:
                    if not result.is_partial:
                        for alt in result.alternatives:
                            text = alt.transcript
                            print(text, flush=True, end=' ')
                            EventHandler.text.append(text)

                            if len(EventHandler.text) != 0:
                                input_text = ' '.join(EventHandler.text)
                                printer(f'\n[INFO] User input: {input_text}', 'info')

                                executor = ThreadPoolExecutor(max_workers=1)
                                UserInputManager.set_executor(executor)
                                loop.run_in_executor(
                                    executor,
                                    self.bedrock_wrapper.invoke_bedrock,
                                    input_text,
                                    self.current_language  # 使用用户选择的语言
                                )

                                EventHandler.text.clear()
                                EventHandler.sample_count = 0

# 麦克风流处理
class MicStream:
    def __init__(self, current_language):  # 初始化时传入用户选择的语言
        self.current_language = current_language

    async def mic_stream(self):
        loop = asyncio.get_event_loop()
        input_queue = asyncio.Queue()

        def callback(indata, frame_count, time_info, status):
            loop.call_soon_threadsafe(input_queue.put_nowait, (bytes(indata), status))

        # 初始化音频流
        stream = sounddevice.RawInputStream(
            channels=1,
            samplerate=16000,
            callback=callback,
            blocksize=2048 * 2,
            dtype="int16"
        )
        with stream:
            while True:
                indata, status = await input_queue.get()
                yield indata, status

    async def write_chunks(self, stream):
        async for chunk, status in self.mic_stream():
            await stream.input_stream.send_audio_event(audio_chunk=chunk)
        await stream.input_stream.end_stream()

    async def basic_transcribe(self):
        # 启动用户输入监听线程
        loop.run_in_executor(ThreadPoolExecutor(max_workers=1), UserInputManager.start_user_input_loop)

        # 初始化 Transcribe 流
        stream = await transcribe_streaming.start_stream_transcription(
            language_code=config['language_mapping'][self.current_language]['transcribe_language'],
            media_sample_rate_hz=16000,
            media_encoding="pcm",
        )
        # 处理转录结果
        handler = EventHandler(stream.output_stream, BedrockWrapper(), self.current_language)
        await asyncio.gather(self.write_chunks(stream), handler.handle_events())

# 主程序
info_text = f'''
*************************************************************
[INFO] Supported FM models: {get_model_ids()}.
[INFO] Change FM model by setting <MODEL_ID> environment variable. Example: export MODEL_ID=meta.llama2-70b-chat-v1

[INFO] AWS Region: {config['region']}
[INFO] Amazon Bedrock model: {config['bedrock']['api_request']['modelId']}
[INFO] Polly config: engine {config['polly']['Engine']}, voice {config['polly']['VoiceId']}
[INFO] Log level: {config['log_level']}

[INFO] Hit ENTER to interrupt Amazon Bedrock. After you can continue speaking!
[INFO] Go ahead with the voice chat with Amazon Bedrock!
*************************************************************
'''
print(info_text)

# 用户选择语言
selected_language = select_language()
update_language_config(selected_language)

# 显式创建事件循环
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

try:
    loop.run_until_complete(MicStream(selected_language).basic_transcribe())  # 传递用户选择的语言
except (KeyboardInterrupt, Exception) as e:
    print(f"Error: {e}")
    loop.close()