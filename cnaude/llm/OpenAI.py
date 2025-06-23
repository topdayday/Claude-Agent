import os
from openai import OpenAI


clientDeepSeek = OpenAI(
    api_key="api-key-deepseek",  
    base_url="https://api.deepseek.com",
    timeout=6000
)
clientQWen = OpenAI(
    api_key="api-key-qwen",  
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    timeout=6000
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
    token_usage = {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "model_name": ""
    }
    
    if model_index == 0:
        model_client = clientDeepSeek
        if len(message) == 1:
            model_id = 'deepseek-reasoner'
            token_usage["model_name"] = "deepseek-reasoner"
        else:
            model_id = 'deepseek-chat'
            token_usage["model_name"] = "deepseek-chat"
    elif model_index == 1:    
        model_client = clientQWen
        model_id = 'qwen-max-2025-01-25'
        token_usage["model_name"] = "qwen-max-2025-01-25"
    
    try:
        response = model_client.chat.completions.create( 
          model= model_id,
          messages= message,
          stream=False
        )
        output_content=response.choices[0].message.content
        
        # 提取token使用信息
        if hasattr(response, 'usage') and response.usage:
            token_usage["input_tokens"] = response.usage.prompt_tokens if hasattr(response.usage, 'prompt_tokens') else 0
            token_usage["output_tokens"] = response.usage.completion_tokens if hasattr(response.usage, 'completion_tokens') else 0
            token_usage["total_tokens"] = response.usage.total_tokens if hasattr(response.usage, 'total_tokens') else token_usage["input_tokens"] + token_usage["output_tokens"]
        
    except BaseException as e:
        print(e.args)
    
    return output_content, token_usage
