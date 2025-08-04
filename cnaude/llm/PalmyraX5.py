import boto3
import json
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

model_data = [
    {
        "model_id": "us.writer.palmyra-x5-v1:0",
        "max_output_tokens": 8192,
        "name": "palmyra-x-5-32k",
    },
]

from botocore.client import Config

# 配置超时（单位：秒）
timeout_config = Config(
    connect_timeout=60,  # 连接超时设置为60秒
    read_timeout=600,    # 读取超时设置为600秒
    retries={'max_attempts': 3, 'mode': 'standard'}
)

client = boto3.client(service_name="bedrock-runtime", region_name="us-west-2", config=timeout_config)
bedrock_client = boto3.client(service_name="bedrock", region_name="us-west-2", config=timeout_config)


def list_available_models():
    """列出可用的模型"""
    try:
        response = bedrock_client.list_foundation_models()
        writer_models = [model for model in response['modelSummaries']]
        print("可用的Writer模型:")
        for model in writer_models:
            print(f"- {model['modelId']} ({model['modelName']})")
        return writer_models
    except Exception as e:
        logger.error(f"获取模型列表时出错: {e}")
        return []


def translate_conversation_his_palmyra(contents):
    """转换对话历史为Palmyra格式"""
    chats_history = []
    for content in contents:
        chat_history = format_chat_history(content.content_in, content.content_out)
        chats_history.extend(chat_history)
    return chats_history


def format_chat_history(content_in, content_out):
    """格式化聊天历史"""
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


def start_conversation_palmyra_x5(input_content, previous_chat_history=[], model_index=0):
    """
    启动Palmyra X5对话
    
    Args:
        input_content (str): 用户输入内容
        previous_chat_history (list): 之前的对话历史
        model_index (int): 模型索引，默认为0
    
    Returns:
        str: 模型响应内容
    """
    palmyra_model = model_data[model_index]
    
    # 构建消息列表
    messages = []
    
    # 添加系统消息
    messages.append({
        "role": "system",
        "content": "You are a helpful AI assistant. You give preference to answering in Chinese when appropriate."
    })
    
    # 添加历史对话
    if previous_chat_history:
        messages.extend(previous_chat_history)
    
    # 添加当前用户输入
    messages.append({
        "role": "user",
        "content": input_content
    })
    
    # 构建请求体 - 根据AWS Bedrock Palmyra X5文档格式
    body = json.dumps({
        "messages": messages,
        "max_tokens": palmyra_model['max_output_tokens'],
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40
    })
    
    output_content = ''
    try:
        response = client.invoke_model(
            body=body, 
            modelId=palmyra_model['model_id'],
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response.get("body").read())
        
        # 根据AWS Bedrock Palmyra X5文档的响应格式提取内容
        if 'choices' in response_body and len(response_body['choices']) > 0:
            choice = response_body['choices'][0]
            if 'message' in choice and 'content' in choice['message']:
                output_content = choice['message']['content']
            elif 'text' in choice:
                output_content = choice['text']
        elif 'completion' in response_body:
            output_content = response_body['completion']
        elif 'content' in response_body:
            output_content = response_body['content']
        else:
            # 如果响应格式不明确，记录完整响应用于调试
            logger.warning(f"Unexpected response format: {response_body}")
            output_content = str(response_body)
            
    except Exception as e:
        logger.error(f"处理Palmyra X5请求时出错: {e}")
        output_content = f"error: {e}"
    
    return output_content


def start_conversation_palmyra_x5_streaming(input_content, previous_chat_history=[], model_index=0):
    """
    启动Palmyra X5流式对话（如果支持）
    
    Args:
        input_content (str): 用户输入内容
        previous_chat_history (list): 之前的对话历史
        model_index (int): 模型索引，默认为0
    
    Yields:
        str: 流式响应内容片段
    """
    palmyra_model = model_data[model_index]
    
    # 构建消息列表
    messages = []
    
    # 添加系统消息
    messages.append({
        "role": "system",
        "content": "You are a helpful AI assistant. You give preference to answering in Chinese when appropriate."
    })
    
    # 添加历史对话
    if previous_chat_history:
        messages.extend(previous_chat_history)
    
    # 添加当前用户输入
    messages.append({
        "role": "user",
        "content": input_content
    })
    
    # 构建请求体
    body = json.dumps({
        "messages": messages,
        "max_tokens": palmyra_model['max_output_tokens'],
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "stop_sequences": [],
        "stream": True
    })
    
    try:
        response = client.invoke_model_with_response_stream(
            body=body,
            modelId=palmyra_model['model_id'],
            contentType='application/json',
            accept='application/json'
        )
        
        stream = response.get('body')
        if stream:
            for event in stream:
                chunk = event.get('chunk')
                if chunk:
                    chunk_data = json.loads(chunk.get('bytes').decode())
                    if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                        delta = chunk_data['choices'][0].get('delta', {})
                        if 'content' in delta:
                            yield delta['content']
                    elif 'content' in chunk_data:
                        yield chunk_data['content']
                        
    except Exception as e:
        logger.error(f"处理Palmyra X5流式请求时出错: {e}")
        yield f"error: {e}"


if __name__ == '__main__':
    # 首先检查可用的模型
    print("=== 检查可用的Writer模型 ===")
    list_available_models()
    
    测试基本对话功能
    print("\n=== 测试Palmyra X5对话 ===")
    try:
        output = start_conversation_palmyra_x5('你好，请介绍一下你自己')
        print("响应:", output)
    except Exception as e:
        print(f"测试错误: {e}")
    
    测试带历史记录的对话
    print("\n=== 测试带历史记录的对话 ===")
    try:
        history = [
            {"role": "user", "content": "我的名字是张三"},
            {"role": "assistant", "content": "你好张三，很高兴认识你！"}
        ]
        output = start_conversation_palmyra_x5('你还记得我的名字吗？', history)
        print("响应:", output)
    except Exception as e:
        print(f"历史对话测试错误: {e}")
    
    # 测试流式对话（如果支持）
    print("\n=== 测试流式对话 ===")
    try:
        print("流式响应: ", end="")
        for chunk in start_conversation_palmyra_x5_streaming('请写一首关于春天的短诗'):
            print(chunk, end="", flush=True)
        print()
    except Exception as e:
        print(f"流式对话测试错误: {e}")
    
    print("\n=== 配置的模型 ===")
    for i, model in enumerate(model_data):
        print(f"{i}: {model['name']} ({model['model_id']}) - Max tokens: {model['max_output_tokens']}")