from vertexai.generative_models._generative_models import ResponseBlockedError
from vertexai.preview.generative_models import GenerativeModel, Part
import base64
import mimetypes
from pathlib import Path
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
# temperature
# 温度取值范围【0-2】
# 温度可以控制词元选择的随机性。较低的温度适合希望获得真实或正确回复的提示，
# 而较高的温度可能会引发更加多样化或意想不到的结果。
# 如果温度为 0，系统始终会选择概率最高的词元。

# max_output_tokens
# 输出词元取值范围
# 输出词元限制决定了一条提示的最大文本输出量。
# 一个词元约为 4 个字符。
models_data = [
    {
        "model_id": "gemini-2.5-pro",
        "max_output_tokens": 65535,
        "temperature": 1.0,
        "top_p": 1,
        "description": "2M content window",
        "type": "multiplex",
    },
    {
        "model_id": "gemini-2.5-pro-preview-05-06",
        "max_output_tokens": 65535,
        "temperature": 1.0,
        "top_p": 1,
        "description": "2M content window",
        "type": "multiplex",
    },
    {
        "model_id": "gemini-2.5-pro-preview-06-05",
        "max_output_tokens": 65535,
        "temperature": 1.0,
        "top_p": 1,
        "description": "2M content window",
        "type": "multiplex",
    },
    {
        "model_id": "gemini-2.0-flash-thinking-exp-01-21",
        "max_output_tokens": 8192,
        "temperature": 1.0,
        "top_p": 1,
        "description": "2M content window",
        "type": "multiplex",
    },
    {
        "model_id": "gemini-2.0-flash-001",
        "max_output_tokens": 8192,
        "temperature": 1.0,
        "top_p": 1,
        "description": "2M content window",
        "type": "multiplex",
    },
    {
        "model_id": "gemini-1.5-flash-002",
        "max_output_tokens": 8192,
        "temperature": 1.0,
        "top_p": 1,
        "description": "2M content window",
        "type": "multiplex",
    },
    {
        "model_id": "gemini-1.5-pro-002",
        "max_output_tokens": 8192,
        "temperature": 1.0,
        "top_p": 1,
        "description": "2M content window",
        "type": "multiplex",
    },
    {
        "model_id": "gemini-1.5-pro-preview-0409",
        "max_output_tokens": 8192,
        "temperature": 1.0,
        "top_p": 1,
        "description": "1M content window",
        "type": "multiplex",
    },
    {
        "model_id": "gemini-1.0-pro-vision-001",
        "max_output_tokens": 2048,
        "temperature": 1.0,
        "top_p": 1,
        "description": "针对视觉进行了优化,稳定",
        "type": "multiplex",
    },
    {
        "model_id": "gemini-1.0-pro-001",
        "max_output_tokens": 8192,
        "temperature": 1.0,
        "top_p": 1,
        "description": "性能稳定优化版",
        "type": "text",
    },
    {
        "model_id": "gemini-1.0-pro-002",
        "max_output_tokens": 8192,
        "temperature": 1.0,
        "top_p": 1,
        "description": "性能稳定优化版",
        "type": "text",
    },
    {
        "model_id": "gemini-pro",
        "max_output_tokens": 2048,
        "temperature": 1.0,
        "top_p": 1,
        "description": "早期版本",
        "type": "text",
    },
]

def load_file_as_part(file_path):
    """
    加载文件并转换为Gemini可以处理的Part对象
    支持图片、PDF、文档等多种格式
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    # 获取MIME类型
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type is None:
        # 根据文件扩展名手动设置MIME类型
        ext = file_path.suffix.lower()
        mime_map = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.mp4': 'video/mp4',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav'
        }
        mime_type = mime_map.get(ext, 'application/octet-stream')
    # 读取文件内容
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    # 创建Part对象
    return Part.from_data(data=file_data, mime_type=mime_type)

def create_multimodal_content(text_content, file_paths=None):
    """
    创建包含文本和文件的多模态内容
    """
    parts = []
    
    # 添加文本内容
    if text_content:
        parts.append(Part.from_text(text_content))
    
    # 添加文件内容
    if file_paths:
        if isinstance(file_paths, str):
            file_paths = [file_paths]
        
        for file_path in file_paths:
            try:
                file_part = load_file_as_part(file_path)
                parts.append(file_part)
            except Exception as e:
                logger.error(f"加载文件失败 {file_path}: {e}")
    
    return parts

def translate_conversation_his_gemini(contents):
    chats_history = []
    for content in contents:
        chat_history = format_chat_history(content.content_in, content.content_out)
        chats_history.extend(chat_history)
    return chats_history

def format_chat_history(content_in, content_out):
    message_in = {"role": "user", "content": content_in}
    message_out = {"role": "model", "content": content_out}
    return [message_in, message_out]

def start_conversation_gemini(content_in, previous_chat_history=[], model_index=0, file_paths=None):
    """
    开始与Gemini的对话，支持文本和文档输入
    
    Args:
        content_in: 文本输入内容
        previous_chat_history: 之前的对话历史
        model_index: 模型索引
        file_paths: 文件路径列表，支持图片、PDF、文档等
    """
    model_data = models_data[model_index]
    config = {
        "max_output_tokens": model_data['max_output_tokens'],
        "temperature":  model_data['temperature'],
        "top_p": model_data['top_p'],
    }
    
    output_content = ''
    model = GenerativeModel(model_data['model_id'])
    
    try:
        # 如果有文件输入，使用多模态内容
        if file_paths:
            # 创建多模态内容
            multimodal_parts = create_multimodal_content(content_in, file_paths)
            
            # 如果有历史对话，需要先发送历史内容
            if previous_chat_history:
                chat = model.start_chat()
                # 发送历史对话
                for history_item in previous_chat_history:
                    if history_item['role'] == 'user':
                        chat.send_message(history_item['content'], generation_config=config)
                
                # 发送当前多模态消息
                message_out = chat.send_message(multimodal_parts, generation_config=config)
            else:
                # 直接发送多模态内容
                message_out = model.generate_content(multimodal_parts, generation_config=config)
        else:
            # 纯文本模式，保持原有逻辑
            input_content = []
            input_content_obj = {"role": "user", "content": content_in}
            if previous_chat_history:
                input_content.extend(previous_chat_history)
            input_content.append(input_content_obj)
            output_content_str = "\n".join([f"{m['role']}: {m['content']}" for m in input_content])
            
            chat = model.start_chat()
            message_out = chat.send_message(output_content_str, generation_config=config)
        
        output_content = message_out.candidates[0].content.parts[0].text
        
    except ResponseBlockedError as e:
        logger.error(f"响应被阻止: {e.args}")
    except Exception as e:
        logger.error(f"处理请求时出错: {e}")
    
    return output_content


# if __name__ == '__main__':
    # pass
    # 测试纯文本对话
    # print("=== 测试纯文本对话 ===")
    # test = 'who are you ?'
    # output = start_conversation_gemini(test)
    # print('文本对话 ===>  ' + output)
    
    # 测试文档输入（需要提供实际的文件路径）
    # print("\n=== 测试文档输入 ===")
    # 示例：分析图片
    # image_path = r"C:\Users\Administrator\Desktop\task_job.bat"
    # file_part = load_file_as_part(image_path)
   
    # output = start_conversation_gemini("请描述这张图片的内容", file_paths=[image_path])
    # print('图片分析 ===>  ' + output)
    
    # 示例：分析PDF文档
    # pdf_path = "path/to/your/document.pdf"
    # output = start_conversation_gemini("请总结这个PDF文档的主要内容", file_paths=[pdf_path])
    # print('PDF分析 ===>  ' + output)
    
    # 示例：多文件输入
    # files = ["document.pdf", "image.jpg", "text.txt"]
    # output = start_conversation_gemini("请分析这些文件的内容", file_paths=files)
    # print('多文件分析 ===>  ' + output)
    
    # print("文档支持功能已添加！")
    # print("支持的文件类型：")
    # print("- 图片：JPG, PNG, GIF, WebP")
    # print("- 文档：PDF, DOC, DOCX, TXT, MD")
    # print("- 音视频：MP4, MP3, WAV")
    
    # for model_idx in range(5):
    #     output = start_conversation_gemini('what is your name ?', model_idx)
    #     print(models_data[model_idx]['model_id'] + '===>  ' + output)