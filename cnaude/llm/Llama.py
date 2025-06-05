import boto3
import json

model_data =[
    {
        "model_id": "us.meta.llama4-maverick-17b-instruct-v1:0",
        "max_output_tokens": 8192,
        "name": "llama4-maverick-17b",
    },
    {
        "model_id": "us.meta.llama4-scout-17b-instruct-v1:0",
        "max_output_tokens": 8192,
        "name": "llama4-maverick-17b",
    },
    {
        "model_id": "meta.llama3-1-70b-instruct-v1:0",
        "max_output_tokens": 2048,
        "name": "llama3-1-70b",
    },
    {
        "model_id": "meta.llama3-70b-instruct-v1:0",
        "max_output_tokens": 2048,
        "name": "llama3-70b",
    },
    {
        "model_id": "meta.llama3-8b-instruct-v1:0",
        "max_output_tokens": 2048,
        "name": "llama3-8b",
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
 


def translate_conversation_his_llama(contents):
    chats_history= ''
    for content in contents:
        chat_history = format_chat_history(content.content_in, content.content_out)
        chats_history += chat_history
    return chats_history


def format_chat_history(content_in, content_out):
    message = '''
    <|start_header_id|>user<|end_header_id|>{0}<|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>{1}<|eot_id|>
    '''.format(content_in, content_out)
    return message


def start_conversation_llama(input_content, previous_chat_history='', model_index=0):
    llama_model = model_data[model_index]
    input_prompt = '''
    <|begin_of_text|>
    <|start_header_id|>system<|end_header_id|>
    You give preference to answering in Chinese.
    <|eot_id|>
    {0}
    <|start_header_id|>user<|end_header_id|>
    {1}
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    '''.format(previous_chat_history, input_content)
    body = json.dumps({
        "prompt": input_prompt,
        "max_gen_len": llama_model['max_output_tokens'],
        "temperature": 0.5,
        "top_p": 0.9,
    })
    output_content = ''
    try:
        response = bedrock.invoke_model(body=body, modelId=llama_model['model_id'])
        response_body = json.loads(response.get("body").read().decode('utf-8'))
        output_content = response_body.get("generation")
        output_content = output_content.replace('<|eot_id|>', '')
    except BaseException as e:
        print(e.args)
    return output_content


if __name__ == '__main__':
    output = start_conversation_llama('what is your name ?')
    print(output)










