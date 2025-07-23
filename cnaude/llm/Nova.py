import boto3
import json

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

model_data =[
    {
        "model_id": "us.amazon.nova-pro-v1:0",
        "max_output_tokens": 2048,
        "name": "llama3-1-70b",
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
bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-west-2", config=timeout_config)



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
                    "text": content_in
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
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
        "top_p": 0.6,
        "anthropic_version": claude_model['version']
    })
    output_content = ''
    try:
        response = bedrock.invoke_model(body=body, modelId=claude_model['model_id'])
        response_body = json.loads(response.get("body").read())
        output_contents = response_body.get("content")
        for  content in output_contents:
            if content['type'] == 'text':
                output_content = content['text']
    except BaseException as e:
        print(e.args)
    return output_content

#
# if __name__ == '__main__':
#     output = start_conversation_claude3('what is your name ?', None)
#     print(output)




def start_conversation_nova(input_content, previous_chat_history='', model_index=0):

    output_content = ''
    try:
        response = bedrock.invoke_model(body=body, modelId='us.amazon.nova-pro-v1:0')
        response_body = json.loads(response.get("body").read().decode('utf-8'))
        output_content = response_body.get("generation")
    except BaseException as e:
        print(e.args)
    return output_content


if __name__ == '__main__':

    client =  boto3.client(service_name="bedrock-runtime", region_name="us-east-2")

    # 构建请求payload
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": "你知道大熊猫吗"
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "text": "当然知道！大熊猫（学名：*Ailuropoda melanoleuca*），是一种生活在中国的珍稀哺乳动物，以其独特的黑白相间的毛色而闻名。"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "text": "请你给他写一首诗歌吧"
                    }
                ]
            },
        ]
    }

    # 调用模型
    response = client.invoke_model(
        modelId='us.amazon.nova-pro-v1:0',  # 替换为正确的模型ID
        body=json.dumps(payload)
    )

    # 处理响应
    response_body = json.loads(response['body'].read())
    print(response_body)










