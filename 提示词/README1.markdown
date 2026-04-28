# 异步 LLM 调用系统

基于 Python 的异步客户端，用于与 AWS Bedrock 的 LLama3-70B 模型交互，支持流式响应和竞赛模式。

## 功能特点

- **异步操作**：采用 `asyncio` 实现非阻塞 I/O
- **双模式支持**：
  - 标准聊天模式
  - 竞赛模式（自动格式化专业回答）
- **流式响应**：实时输出处理
- **状态管理**：线程安全操作控制
- **AWS 集成**：Bedrock Runtime API 客户端

## 代码结构

```python
import asyncio
import json
import boto3

class State:  # 全局状态管理器
    outputting = False  # 输出状态锁
    running = True     # 程序运行标志
    competition_mode = False  # 竞赛模式开关

async def invoke_async(text, is_competition=False):  # 核心调用逻辑
    # 处理提示词构造和流式响应
    # 实现竞赛模式专业格式化
    # 管理 AWS Bedrock API 调用

async def input_loop():  # 用户交互处理器
    # 异步处理用户输入
    # 管理程序生命周期

async def main():  # 程序入口
    # 初始化并协调各组件