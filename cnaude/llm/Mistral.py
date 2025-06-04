import boto3
import json

model_data =[
    {
        "model_id": "mistral.mistral-large-2402-v1:0",
        "max_output_tokens": 4096,
        "name": "mistral-large",
    },
    {
        "model_id": "mistral.mixtral-8x7b-instruct-v0:1",
        "max_output_tokens": 4096,
        "name": "mixtral-8x7b",
    },
    {
        "model_id": "mistral.mistral-7b-instruct-v0:2",
        "max_output_tokens": 4096,
        "name": "mistral-7b",
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



def translate_conversation_his_mistral(contents):
    chats_history = []
    for content in contents:
        chat_history = format_chat_history(content.content_in, content.content_out)
        chats_history.extend(chat_history)
    return chats_history


def format_chat_history(content_in, content_out):
    message_in = {"role": "user", "content": content_in}
    message_out = {"role": "system", "content": content_out}
    return [message_in,message_out]


input_text_prompt = '''
<s>[INST]####You(system) are talking to user, this is what you talked about. #### [/INST][INST]<<SYS>>{0}<</SYS>>#### {1}[/INST]
'''


def start_conversation_mistral(input_content, previous_chat_history=[], model_index=0):
    mistral_model = model_data[model_index]
    body = json.dumps({
        "prompt": input_text_prompt.format(json.dumps(previous_chat_history), input_content),
        "max_tokens": mistral_model['max_output_tokens'],
        "temperature": 0.2,
        "top_p": 0.9,
        "top_k": 50,
    })
    output_content = ''
    try:
        response = bedrock.invoke_model(body=body, modelId=mistral_model['model_id'])
        response_body = json.loads(response.get("body").read().decode('utf-8'))
        output_content = response_body.get("outputs")
        output_content = output_content[0]['text']
    except BaseException as e:
        print(e.args)
    return output_content


if __name__ == '__main__':
    output = start_conversation_mistral('what is your name ?')
    print(output)








