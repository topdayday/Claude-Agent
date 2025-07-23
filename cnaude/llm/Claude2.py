import boto3
import json
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
model_data =[
    {
        "model_id": "anthropic.claude-v2:1",
        "version": "bedrock-2023-05-31",
        "max_output_tokens": 10240,
        "name": "claude-2-1",
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



def translate_conversation_his_v2(contents):
    his = ''
    for content in contents:
        his += format_chat_history(content.content_in, content.content_out)
    return his


def format_chat_history(content_in, content_out):
    previous_chat_history = '"\n\nHuman: "' + content_in + '"\n\nAssistant: "' + content_out
    return previous_chat_history


def start_conversation_claude2(input_content, previous_chat_history=[], model_index=0):
    claude_model = model_data[model_index]
    if previous_chat_history:
        body = json.dumps({
            "prompt": "\n\nHuman: " + previous_chat_history +
                      "\n\nHuman: " + input_content +
                      "\n\nAssistant:",
            "temperature": 0.9,
            "max_tokens_to_sample": 10000,
            "top_k": 250,
            "top_p": 0.6,
            "anthropic_version": claude_model['version']
        })
    else:
        body = json.dumps({
            "prompt": "\n\nHuman: " + input_content +
                      "\n\nAssistant:",
            "temperature": 0.9,
            "max_tokens_to_sample": claude_model['max_output_tokens'],
            "top_k": 250,
            "top_p": 0.6,
            "anthropic_version": claude_model['version']
        })
    output_content = ''
    try:
        response = client.invoke_model(body=body, modelId=claude_model['model_id'])
        response_body = json.loads(response.get("body").read())
        output_content = response_body.get("completion")
    except BaseException as e:
        print(e.args)
    return output_content


if __name__ == '__main__':
    output = start_conversation_claude2('what is your name ?', None)
    print(output)











