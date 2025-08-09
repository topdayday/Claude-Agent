import boto3
import json
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

model_data = [
    {
        "model_id": "openai.gpt-oss-120b-1:0", 
        "max_output_tokens": 4096,
        "name": "gpt-oss-120b",
    },
    {
        "model_id": "openai.gpt-oss:20b-1:0",
        "max_output_tokens": 4096,
        "name": "gpt-oss-20b",
    },
]

from botocore.client import Config

# 配置超时（单位：秒）
timeout_config = Config(
    connect_timeout=60,  # 连接超时设置为60秒
    read_timeout=600,     # 读取超时设置为600秒 (Bedrock 模型响应可能需要一些时间)
    # 可选：配置重试次数
    retries={'max_attempts': 3, 'mode': 'standard'}
)
bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-west-2", config=timeout_config)


def translate_conversation_his_gptoss(contents):
    chats_history = []
    for content in contents:
        chat_history = format_chat_history(content.content_in, content.content_out)
        chats_history.extend(chat_history)
    return chats_history


def format_chat_history(content_in, content_out):
    chat_history = [
        {
            "role": "user",
            "content": content_in
        },
        {
            "role": "assistant", 
            "content": content_out
        }
    ]
    return chat_history


def start_conversation_gptoss(input_content, previous_chat_history=[], model_index=0):
    gptoss_model = model_data[model_index]
    messages = []
    
    if previous_chat_history:
        messages.extend(previous_chat_history)
    
    messages.append({
        "role": "user",
        "content": input_content
    })
    
    body = json.dumps({
        "messages": messages,
        "max_completion_tokens": gptoss_model['max_output_tokens'],
        "temperature": 0.7,
        "top_p": 0.9,
    })
    
    output_content = ''
    try:
        response = bedrock.invoke_model(body=body, modelId=gptoss_model['model_id'])
        response_body = json.loads(response.get("body").read().decode('utf-8'))
        
        # GPT-OSS 模型的响应格式处理
        if 'choices' in response_body:
            output_content = response_body['choices'][0]['message']['content']
        elif 'content' in response_body:
            output_content = response_body['content']
        elif 'generation' in response_body:
            output_content = response_body['generation']
        else:
            # 如果响应格式不明确，尝试获取第一个可能的文本内容
            output_content = str(response_body)
        
        # 清理可能的内部推理标签
        if '<reasoning>' in output_content and '</reasoning>' in output_content:
            # 移除所有 <reasoning>...</reasoning> 标签及其内容
            import re
            output_content = re.sub(r'<reasoning>.*?</reasoning>', '', output_content, flags=re.DOTALL)
            output_content = output_content.strip()
            
    except BaseException as e:
        logger.error(f"Error calling GPT-OSS model: {e}")
        print(e.args)
    
    return output_content


if __name__ == '__main__':
    output = start_conversation_gptoss('What is your name?')
    print(output)