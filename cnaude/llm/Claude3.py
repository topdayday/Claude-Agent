import boto3
import json
import base64

import mimetypes
from pathlib import Path
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

model_data =[
     {
        "model_id": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        "version": "bedrock-2023-05-31",
        "max_output_tokens": 21333,
        "name": "claude-4-5",
    },
    {
        "model_id": "us.anthropic.claude-opus-4-1-20250805-v1:0",
        "version": "bedrock-2023-05-31",
        "max_output_tokens": 21333,
        "name": "claude-4-1",
    },
    {
        "model_id": "us.anthropic.claude-sonnet-4-20250514-v1:0",
        "version": "bedrock-2023-05-31",
        "max_output_tokens": 21333,
        "name": "claude-4-0",
    },
    {
        "model_id": "us.anthropic.claude-opus-4-20250514-v1:0",
        "version": "bedrock-2023-05-31",
        "max_output_tokens": 21333,
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


def encode_file_to_base64(file_path):
    """将文件编码为base64字符串"""
    try:
        with open(file_path, 'rb') as file:
            return base64.b64encode(file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding file {file_path}: {e}")
        return None


def get_media_type(file_path):
    """根据文件扩展名获取媒体类型"""
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        return mime_type
    
    # 手动处理一些常见的文档类型
    file_extension = Path(file_path).suffix.lower()
    extension_map = {
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.txt': 'text/plain',
        '.csv': 'text/csv',
        '.json': 'application/json',
        '.xml': 'application/xml',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    return extension_map.get(file_extension, 'application/octet-stream')


def create_content_block(content_type, content_data, file_path=None):
    """创建内容块，支持文本和文档"""
    if content_type == "text":
        return {
            "type": "text",
            "text": content_data
        }
    elif content_type == "document":
        if not file_path:
            raise ValueError("Document content requires file_path")
        
        base64_data = encode_file_to_base64(file_path)
        if not base64_data:
            raise ValueError(f"Failed to encode file: {file_path}")
        
        media_type = get_media_type(file_path)
        
        return {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": base64_data
            }
        }
    elif content_type == "image":
        if not file_path:
            raise ValueError("Image content requires file_path")
        
        base64_data = encode_file_to_base64(file_path)
        if not base64_data:
            raise ValueError(f"Failed to encode file: {file_path}")
        
        media_type = get_media_type(file_path)
        
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": base64_data
            }
        }
    else:
        raise ValueError(f"Unsupported content type: {content_type}")


def translate_conversation_his_v3(contents):
    chats_history = []
    for content in contents:
        chat_history = format_chat_history(content.content_in, content.content_out)
        chats_history.extend(chat_history)
    return chats_history


def format_chat_history(content_in, content_out, content_in_files=None):
    """格式化聊天历史，支持文本和文档"""
    user_content = []
    
    # 添加文本内容
    if content_in:
        user_content.append({
            "type": "text",
            "text": content_in
        })
    
    # 添加文件内容
    if content_in_files:
        for file_info in content_in_files:
            file_path = file_info.get('path')
            file_type = file_info.get('type', 'document')  # 默认为文档类型
            
            try:
                content_block = create_content_block(file_type, None, file_path)
                user_content.append(content_block)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
    
    chat_history = [
        {
            "role": "user",
            "content": user_content
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
    """原始函数，仅支持文本内容（保持向后兼容）"""
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
        # "temperature": 0.9,
        "max_tokens": claude_model['max_output_tokens'],
        "top_k": 250,
        "top_p": 0.9,
        "anthropic_version": claude_model['version']
    })
    output_content = ''
    try:
        response = client.invoke_model(body=body, modelId=claude_model['model_id'])
        response_body = json.loads(response.get("body").read())
        output_contents = response_body.get("content")
        for  content in output_contents:
            if content['type'] == 'text':
                output_content = content['text']
    except BaseException as e:
        logger.error(f"处理请求时出错: {e}")
        output_content = f"error: {e}"
    return output_content


def start_conversation_claude3_with_documents(input_content=None, input_files=None, previous_chat_history=[], model_index=0):
    """支持文档和图片的Claude3对话函数"""
    claude_model = model_data[model_index]
    message = []
    
    if previous_chat_history:
        message.extend(previous_chat_history)
    
    # 构建用户消息内容
    user_content = []
    
    # 添加文本内容
    if input_content:
        user_content.append({
            "type": "text",
            "text": input_content
        })
    
    # 添加文件内容
    if input_files:
        for file_info in input_files:
            file_path = file_info.get('path')
            file_type = file_info.get('type', 'document')  # 默认为文档类型
            
            try:
                content_block = create_content_block(file_type, None, file_path)
                user_content.append(content_block)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                logger.error(f"Error processing file {file_path}: {e}")
                continue
    
    # 如果没有任何内容，返回错误
    if not user_content:
        logger.error("No content provided (neither text nor files)")
        raise ValueError("No content provided (neither text nor files)")
    
    message.append({
        "role": "user",
        "content": user_content
    })
    
    body = json.dumps({
        "messages": message,
        "temperature": 0.9,
        "max_tokens": claude_model['max_output_tokens'],
        "top_k": 250,
        "top_p": 0.9,
        "anthropic_version": claude_model['version']
    })
    
    output_content = ''
    try:
        response = client.invoke_model(body=body, modelId=claude_model['model_id'])
        response_body = json.loads(response.get("body").read())
        output_contents = response_body.get("content")
        for content in output_contents:
            if content['type'] == 'text':
                output_content = content['text']
    except BaseException as e:
        logger.error(f"处理请求时出错: {e}")
        output_content = f"error: {e}"
    return output_content


# if __name__ == '__main__':
    # 测试原始文本功能
    # print("=== 测试文本对话 ===")
    # output = start_conversation_claude3('what is your name ?', None)
    # print(output)
    
    # 测试文档支持功能的示例
    # print("\n=== 文档支持功能使用示例 ===")
    
    # 示例1：仅文本
    # try:
    #     output = start_conversation_claude3_with_documents(
    #         input_content="请帮我分析一下这个问题"
    #     )
    #     print("纯文本对话:", output[:100] + "..." if len(output) > 100 else output)
    # except Exception as e:
    #     print(f"纯文本对话错误: {e}")
    
    # 示例2：文本 + 文档（需要实际文件路径）
    # 注意：这里的文件路径需要根据实际情况修改
   
    # try:
    #     files = [
    #         # {'path': 'example.pdf', 'type': 'document'},
    #         {'path': r"C:\Users\Administrator\Desktop\screen\11.jpg", 'type': 'image'}
    #     ]
    #     output = start_conversation_claude3_with_documents(
    #         input_content="请分析这些文件的内容",
    #         input_files=files
    #     )
    #     print("文档对话:", output[:100] + "..." if len(output) > 100 else output)
    # except Exception as e:
    #     print(f"文档对话错误: {e}")
 
    
    # print("\n=== 支持的文件类型 ===")
    # print("文档类型: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, CSV, JSON, XML")
    # print("图片类型: JPG, JPEG, PNG, GIF, WEBP")
    # print("\n=== 使用方法 ===")
    # print("1. 仅文本: start_conversation_claude3_with_documents(input_content='你的问题')")
    # print("2. 文本+文档: start_conversation_claude3_with_documents(")
    # print("   input_content='你的问题',")
    # print("   input_files=[{'path': '文件路径', 'type': 'document'}]")
    # print(")")
    # print("3. 文本+图片: start_conversation_claude3_with_documents(")
    # print("   input_content='你的问题',")
    # print("   input_files=[{'path': '图片路径', 'type': 'image'}]")
    # print(")")








