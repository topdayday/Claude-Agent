from google import genai
from google.genai import types
import os
import base64
import mimetypes
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 模型配置数据
models_data = [
    {
        "model_id": "gemini-3-pro-preview",
        "max_output_tokens": 65535,
        "temperature": 1.0,
        "top_p": 0.95,
        "description": "Gemini 3 Pro with thinking capabilities",
        "thinking_level": "HIGH",
    },
    {
        "model_id": "gemini-3-flash-preview",
        "max_output_tokens": 65535,
        "temperature": 1.0,
        "top_p": 0.95,
        "description": "Gemini 3 flash with thinking capabilities",
        "thinking_level": "HIGH",
    },
    {
        "model_id": "gemini-2.5-pro",
        "max_output_tokens": 65535,
        "temperature": 1.0,
        "top_p": 0.95,
        "description": "Gemini 2.5 Pro",
        "thinking_level": "MEDIUM",
    },
    {
        "model_id": "gemini-2.0-flash-thinking-exp-01-21",
        "max_output_tokens": 8192,
        "temperature": 1.0,
        "top_p": 0.95,
        "description": "Gemini 2.0 Flash with thinking",
        "thinking_level": "MEDIUM",
    },
]

def get_genai_client():
    """
    创建并返回 GenAI 客户端
    需要设置环境变量 GOOGLE_CLOUD_API_KEY
    """
 
    api_key = 'change to your api_key' #
    if not api_key:
        raise ValueError("GOOGLE_CLOUD_API_KEY environment variable not set")

    return genai.Client(
        vertexai=True,
        api_key=api_key,
    )

def encode_file_to_base64(file_path):
    """将文件编码为base64字符串"""
    try:
        with open(file_path, 'rb') as file:
            return base64.b64encode(file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding file {file_path}: {e}")
        return None

def get_mime_type(file_path):
    """根据文件扩展名获取MIME类型"""
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
        '.txt': 'text/plain',
        '.csv': 'text/csv',
        '.json': 'application/json',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    return extension_map.get(file_extension, 'application/octet-stream')

def create_part_from_file(file_path, file_type='document'):
    """
    从文件创建 Part 对象

    Args:
        file_path: 文件路径
        file_type: 文件类型 ('image' 或 'document')
    """
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()

        mime_type = get_mime_type(file_path)

        # 根据文件类型和MIME类型创建相应的Part
        if file_type == 'image' or mime_type.startswith('image/'):
            # 对于图片，使用 inline_data
            return types.Part.from_bytes(
                data=file_data,
                mime_type=mime_type
            )
        else:
            # 对于文档，使用 inline_data
            return types.Part.from_bytes(
                data=file_data,
                mime_type=mime_type
            )
    except Exception as e:
        logger.error(f"Error creating part from file {file_path}: {e}")
        return None

def translate_conversation_his_gemini3(contents):
    """
    将数据库中的对话历史转换为Gemini API格式

    Args:
        contents: Conversation对象列表

    Returns:
        格式化的对话历史列表
    """
    chats_history = []
    for content in contents:
        chat_history = format_chat_history(content.content_in, content.content_out)
        chats_history.extend(chat_history)
    return chats_history

def format_chat_history(content_in, content_out):
    """
    格式化单条对话历史

    Args:
        content_in: 用户输入内容
        content_out: 模型输出内容

    Returns:
        包含用户和模型消息的列表
    """
    user_message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=content_in)]
    )
    model_message = types.Content(
        role="model",
        parts=[types.Part.from_text(text=content_out)]
    )
    return [user_message, model_message]

def start_conversation_gemini3(content_in, previous_chat_history=[], model_index=0):
    """
    纯文本对话（向后兼容）

    Args:
        content_in: 用户输入文本
        previous_chat_history: 历史对话（Content对象列表）
        model_index: 模型索引

    Returns:
        模型输出文本
    """
    model_data = models_data[model_index]

    try:
        client = get_genai_client()

        # 构建消息内容
        contents = []

        # 添加历史对话
        if previous_chat_history:
            contents.extend(previous_chat_history)

        # 添加当前用户输入
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=content_in)]
        ))

        # 配置生成参数
        generate_content_config = types.GenerateContentConfig(
            temperature=model_data['temperature'],
            top_p=model_data['top_p'],
            max_output_tokens=model_data['max_output_tokens'],
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="OFF"
                )
            ],
            system_instruction=[types.Part.from_text(text="请尽量用简体中文和我对话")],
        )

        # 如果模型支持 thinking，添加 thinking_config
        if model_data.get('thinking_level'):
            generate_content_config.thinking_config = types.ThinkingConfig(
                thinking_level=model_data['thinking_level']
            )

        # 调用API
        response = client.models.generate_content(
            model=model_data['model_id'],
            contents=contents,
            config=generate_content_config,
        )

        # 提取文本响应
        output_content = ''
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text') and part.text:
                    output_content += part.text

        return output_content if output_content else "No response generated"

    except Exception as e:
        logger.error(f"处理请求时出错: {e}")
        return f"error: {e}"

def start_conversation_gemini3_with_documents(input_content=None, input_files=None, previous_chat_history=[], model_index=0):
    """
    支持文档和图片的对话

    Args:
        input_content: 用户输入文本（可选）
        input_files: 文件列表，格式：[{'path': '文件路径', 'type': 'image'/'document'}, ...]
        previous_chat_history: 历史对话（Content对象列表）
        model_index: 模型索引

    Returns:
        模型输出文本
    """
    model_data = models_data[model_index]

    try:
        client = get_genai_client()

        # 构建消息内容
        contents = []

        # 添加历史对话
        if previous_chat_history:
            contents.extend(previous_chat_history)

        # 构建当前用户消息的parts
        user_parts = []

        # 添加文本内容
        if input_content:
            user_parts.append(types.Part.from_text(text=input_content))

        # 添加文件内容
        if input_files:
            for file_info in input_files:
                file_path = file_info.get('path')
                file_type = file_info.get('type', 'document')

                part = create_part_from_file(file_path, file_type)
                if part:
                    user_parts.append(part)
                else:
                    logger.warning(f"Failed to process file: {file_path}")

        # 确保至少有一个part
        if not user_parts:
            raise ValueError("No content provided (neither text nor files)")

        # 添加当前用户消息
        contents.append(types.Content(
            role="user",
            parts=user_parts
        ))

        # 配置生成参数
        generate_content_config = types.GenerateContentConfig(
            temperature=model_data['temperature'],
            top_p=model_data['top_p'],
            max_output_tokens=model_data['max_output_tokens'],
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="OFF"
                )
            ],
            system_instruction=[types.Part.from_text(text="请尽量用简体中文和我对话")],
        )

        # 如果模型支持 thinking，添加 thinking_config
        if model_data.get('thinking_level'):
            generate_content_config.thinking_config = types.ThinkingConfig(
                thinking_level=model_data['thinking_level']
            )

        # 调用API
        response = client.models.generate_content(
            model=model_data['model_id'],
            contents=contents,
            config=generate_content_config,
        )

        # 提取文本响应
        output_content = ''
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text') and part.text:
                    output_content += part.text

        return output_content if output_content else "No response generated"

    except Exception as e:
        logger.error(f"处理请求时出错: {e}")
        return f"error: {e}"


# 测试代码
if __name__ == '__main__':
    # 测试纯文本对话
    print("=== 测试纯文本对话 ===")
    output = start_conversation_gemini3("你好，请介绍一下你自己")
    print(f"文本对话: {output}")

    # # 测试带图片的对话
    # print("\n=== 测试图片分析 ===")
    # try:
    #     files = [
    #         {'path': 'path/to/your/image.jpg', 'type': 'image'}
    #     ]
    #     output = start_conversation_gemini3_with_documents(
    #         input_content="请描述这张图片的内容",
    #         input_files=files
    #     )
    #     print(f"图片分析: {output}")
    # except Exception as e:
    #     print(f"图片分析错误: {e}")

    # # 测试带文档的对话
    # print("\n=== 测试文档分析 ===")
    # try:
    #     files = [
    #         {'path': 'path/to/your/document.pdf', 'type': 'document'}
    #     ]
    #     output = start_conversation_gemini3_with_documents(
    #         input_content="请总结这个文档的主要内容",
    #         input_files=files
    #     )
    #     print(f"文档分析: {output}")
    # except Exception as e:
    #     print(f"文档分析错误: {e}")
