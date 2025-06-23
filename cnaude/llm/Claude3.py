import boto3
import json
 
model_data =[



    {
        "model_id": "us.anthropic.claude-sonnet-4-20250514-v1:0",
        "version": "bedrock-2023-05-31",
        "max_output_tokens": 2048,
        "name": "claude-3-5",
    },
    {
        "model_id": "us.anthropic.claude-opus-4-20250514-v1:0",
        "version": "bedrock-2023-05-31",
        "max_output_tokens": 10240,
        "name": "claude-3-5",
    },
    {
        "model_id": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "version": "bedrock-2023-05-31",
        "max_output_tokens": 131072,
        "name": "claude-3-7",
    },
    {
        "model_id": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "version": "bedrock-2023-05-31",
        "max_output_tokens": 204800,
        "name": "claude-3-opus",
    },
    {
        "model_id": "anthropic.claude-3-opus-20240229-v1:0",
        "version": "bedrock-2023-05-31",
        "max_output_tokens": 204800,
        "name": "claude-3-opus",
    },
    {
        "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
        "version": "bedrock-2023-05-31",
        "max_output_tokens": 204800,
        "name": "claude-3-sonnet",
    },
    {
        "model_id": "anthropic.claude-3-haiku-20240307-v1:0",
        "version": "bedrock-2023-05-31",
        "max_output_tokens": 204800,
        "name": "claude-3-haiku",
    },
]

from botocore.client import Config

# 配置超时（单位：秒）
# 你可以根据你的需求调整这些值
timeout_config = Config(
    connect_timeout=60,  # 连接超时设置为60秒
    read_timeout=600,     # 读取超时设置为600秒 (Bedrock 模型响应可能需要一些时间)
    # 可选：配置重试次数
    retries={'max_attempts': 3, 'mode': 'standard'}
)
client = boto3.client(service_name="bedrock-runtime", region_name="us-west-2", config=timeout_config)


def translate_conversation_his_v3(contents):
    chats_history = []
    for content in contents:
        chat_history = format_chat_history(content.content_in, content.content_out)
        chats_history.extend(chat_history)
    return chats_history


def format_chat_history(content_in, content_out):
    chat_history=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": content_in
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": content_out
                }
            ]
        }
    ]
    return chat_history


def start_conversation_claude3(input_content, previous_chat_history=[], model_index=0):
    claude_model = model_data[model_index]
    message = []
    if previous_chat_history:
        message.extend(previous_chat_history)
    message.extend([
            {
                "role": "user",
                "content":[
                    {
                        "type": "text",
                        "text": input_content
                    }
                ]
            }
        ])
    body = json.dumps({
        "messages": message,
        "temperature": 0.9,
        "max_tokens": claude_model['max_output_tokens'],
        "top_k": 250,
        "top_p": 0.9,
        "anthropic_version": claude_model['version']
    })
    output_content = ''
    token_usage = {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "model_name": claude_model['name']
    }
    try:
        response = client.invoke_model(body=body, modelId=claude_model['model_id'])
        response_body = json.loads(response.get("body").read())
        output_contents = response_body.get("content")
        for  content in output_contents:
            if content['type'] == 'text':
                output_content = content['text']
        
        # 提取token使用信息
        usage = response_body.get("usage", {})
        token_usage["input_tokens"] = usage.get("input_tokens", 0)
        token_usage["output_tokens"] = usage.get("output_tokens", 0)
        token_usage["total_tokens"] = token_usage["input_tokens"] + token_usage["output_tokens"]
        
    except BaseException as e:
        print(e.args)
    
    # 返回包含token使用信息的结果
    return output_content, token_usage


if __name__ == '__main__':
    output, usage = start_conversation_claude3('what is your name ?', None)
    print(output)
    print(usage)








