import os
from openai import OpenAI
import traceback

clientDeepSeek = OpenAI(
    api_key="{Your-App-Key}",  
    base_url="https://api.deepseek.com",
)
clientQWen = OpenAI(
    api_key="{Your-App-Key}",  
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def translate_conversation_his_openai(contents):
    chats_history = []
    for content in contents:
        chat_history = format_chat_history(content.content_in, content.content_out)
        chats_history.extend(chat_history)
    return chats_history


def format_chat_history(content_in, content_out):
    chat_history=[
        {
            "role": "user",
            "content": content_in
        },
        {
            "role": "system",
            "content": content_out
        }
    ]
    return chat_history


def start_conversation_openai(input_content, previous_chat_history=[], model_index=0):
    message = []
    if previous_chat_history:
        message.extend(previous_chat_history)
    message.extend([
            {
                "role": "user",
                "content":input_content
            }
        ])
    output_content = ''
    if model_index == 0:
        model_client = clientDeepSeek
        # model_id = 'deepseek-chat'
        model_id = 'deepseek-reasoner'
    elif model_index == 1:    
        model_client = clientQWen
        model_id = 'qwen-max-2025-01-25'
    try:
        response = model_client.chat.completions.create( 
          model= model_id,
          messages= message,
          stream=False
        )
        output_content=response.choices[0].message.content
    except BaseException as e:
        # 获取异常类型、值和回溯对象
        etype, value, tb = sys.exc_info()
        # 使用 traceback.format_exception 格式化异常信息
        error_message = ''.join(traceback.format_exception(etype, value, tb))
        output_content = error_message
        print("捕获到的异常信息：")
        print(error_message)
    return output_content
