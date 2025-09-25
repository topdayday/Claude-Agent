import oci
import logging
import base64
import mimetypes
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Setup basic variables
# Auth Config
compartment_id = "ocid1.tenancy.oc1..aaaaaaaai5eyg3zscen25zdcxlsajdnms4bcjthoqthdkqfef55pbcs67o7a"
CONFIG_PROFILE = "DEFAULT"
config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)

# Service endpoint
endpoint = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

# Model configuration
models_data = [
    {
        "model_id": "ocid1.generativeaimodel.oc1.us-chicago-1.amaaaaaask7dceya3bsfz4ogiuv3yc7gcnlry7gi3zzx6tnikg6jltqszm2q",
        "max_tokens": 131000,
        "temperature": 1.0,
        "top_p": 1.0,
        "top_k": 0,
        "description": "Grok AI Model",
        "type": "text",
    }
]

def encode_file_to_base64(file_path):
    """将文件编码为base64字符串"""
    try:
        with open(file_path, 'rb') as file:
            return base64.b64encode(file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding file {file_path}: {e}")
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
        '.webp': 'image/webp',
        '.bmp': 'image/bmp',
        '.tiff': 'image/tiff'
    }
    
    return extension_map.get(file_extension, 'application/octet-stream')


def create_content_from_file(file_path, file_type=None):
    """创建文件内容对象，支持图片和文档"""
    try:
        logger.info(f"Processing file: {file_path}, type: {file_type}")
        
        base64_data = encode_file_to_base64(file_path)
        if not base64_data:
            raise ValueError(f"Failed to encode file: {file_path}")
        
        media_type = get_media_type(file_path)
        logger.info(f"Detected media type: {media_type}")
        
        # 根据媒体类型判断是图片还是文档
        if file_type is None:
            if media_type.startswith('image/'):
                file_type = 'image'
            else:
                file_type = 'document'
        
        logger.info(f"Final file type: {file_type}")
        
        if file_type == 'image':
            # 创建图片内容（通过 ImageUrl 的 data URL 方式传入 base64 数据）
            image_content = oci.generative_ai_inference.models.ImageContent()
            image_url = oci.generative_ai_inference.models.ImageUrl()
            image_url.url = f"data:{media_type};base64,{base64_data}"
            try:
                image_url.detail = oci.generative_ai_inference.models.ImageUrl.DETAIL_AUTO
            except Exception:
                pass
            image_content.image_url = image_url
            logger.info(f"Created ImageContent via ImageUrl data URI, mime_type: {media_type}, data length: {len(base64_data)}")
            return image_content
        else:
            # 当前 SDK 的通用聊天内容仅支持 TEXT 与 IMAGE，两者之外跳过
            raise ValueError("Only image files are supported as chat content in the current SDK")
            
    except Exception as e:
        logger.error(f"Error creating content from file {file_path}: {e}")
        raise


def translate_conversation_his_grok(contents):
    """Convert conversation history to Grok format"""
    messages = []
    for content in contents:
        # Add user message
        user_content = oci.generative_ai_inference.models.TextContent()
        user_content.text = content.content_in
        user_message = oci.generative_ai_inference.models.Message()
        user_message.role = "USER"
        user_message.content = [user_content]
        messages.append(user_message)
        
        # Add assistant message
        assistant_content = oci.generative_ai_inference.models.TextContent()
        assistant_content.text = content.content_out
        assistant_message = oci.generative_ai_inference.models.Message()
        assistant_message.role = "ASSISTANT"
        assistant_message.content = [assistant_content]
        messages.append(assistant_message)
    
    return messages

def start_conversation_grok_with_documents(input_content=None, input_files=None, previous_chat_history=[], model_index=0):
    """Start conversation with Grok AI model supporting documents and images"""
    try:
        logger.info(f"Starting Grok conversation with documents. Input content: {input_content}")
        logger.info(f"Input files: {input_files}")
        
        # Initialize client
        generative_ai_inference_client = oci.generative_ai_inference.GenerativeAiInferenceClient(
            config=config, 
            service_endpoint=endpoint, 
            retry_strategy=oci.retry.NoneRetryStrategy(), 
            timeout=(10, 240)
        )
        
        # Get model configuration
        model_data = models_data[model_index]
        logger.info(f"Using model: {model_data['model_id']}")
        
        # Prepare messages
        messages = []
        
        # Add previous chat history
        if previous_chat_history:
            messages.extend(previous_chat_history)
            logger.info(f"Added {len(previous_chat_history)} previous messages")
        
        # Prepare user message content
        user_content_list = []
        
        # Add text content if provided
        if input_content:
            text_content = oci.generative_ai_inference.models.TextContent()
            text_content.text = input_content
            user_content_list.append(text_content)
            logger.info(f"Added text content: {input_content[:100]}...")
        
        # Add file content if provided
        if input_files:
            logger.info(f"Processing {len(input_files)} files")
            for i, file_info in enumerate(input_files):
                file_path = file_info.get('path')
                file_type = file_info.get('type', None)  # 'image', 'document', or None for auto-detect
                
                logger.info(f"Processing file {i+1}: {file_path}, type: {file_type}")
                
                try:
                    file_content = create_content_from_file(file_path, file_type)
                    user_content_list.append(file_content)
                    logger.info(f"Successfully added file content {i+1}")
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
                    continue
        
        # Check if we have any content
        if not user_content_list:
            raise ValueError("No content provided (neither text nor files)")
        
        logger.info(f"Total content items: {len(user_content_list)}")
        
        # Create user message
        user_message = oci.generative_ai_inference.models.Message()
        user_message.role = "USER"
        user_message.content = user_content_list
        messages.append(user_message)
        
        logger.info(f"Created user message with {len(user_content_list)} content items")
        
        # Create chat request
        chat_request = oci.generative_ai_inference.models.GenericChatRequest()
        chat_request.api_format = oci.generative_ai_inference.models.BaseChatRequest.API_FORMAT_GENERIC
        chat_request.messages = messages
        chat_request.max_tokens = model_data['max_tokens']
        chat_request.temperature = model_data['temperature']
        chat_request.top_p = model_data['top_p']
        chat_request.top_k = model_data['top_k']
        
        # Create chat detail
        chat_detail = oci.generative_ai_inference.models.ChatDetails()
        chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(
            model_id=model_data['model_id']
        )
        chat_detail.chat_request = chat_request
        chat_detail.compartment_id = compartment_id
        
        # Send request
        chat_response = generative_ai_inference_client.chat(chat_detail)
        
        # Extract response text
        if (chat_response.data and 
            chat_response.data.chat_response and 
            chat_response.data.chat_response.choices and 
            len(chat_response.data.chat_response.choices) > 0):
            
            choice = chat_response.data.chat_response.choices[0]
            if (choice.message and 
                choice.message.content and 
                len(choice.message.content) > 0):
                return choice.message.content[0].text
        
        return "Sorry, I couldn't generate a response."
        
    except Exception as e:
        logger.error(f"Error in Grok conversation with documents: {e}")
        return f"Error: {str(e)}"


def start_conversation_grok(content_in, previous_chat_history=[], model_index=0):
    """Start conversation with Grok AI model"""
    try:
        # Initialize client
        generative_ai_inference_client = oci.generative_ai_inference.GenerativeAiInferenceClient(
            config=config, 
            service_endpoint=endpoint, 
            retry_strategy=oci.retry.NoneRetryStrategy(), 
            timeout=(10, 240)
        )
        
        # Get model configuration
        model_data = models_data[model_index]
        
        # Prepare messages
        messages = []
        
        # Add previous chat history
        if previous_chat_history:
            messages.extend(previous_chat_history)
        
        # Add current user message
        content = oci.generative_ai_inference.models.TextContent()
        content.text = content_in
        message = oci.generative_ai_inference.models.Message()
        message.role = "USER"
        message.content = [content]
        messages.append(message)
        
        # Create chat request
        chat_request = oci.generative_ai_inference.models.GenericChatRequest()
        chat_request.api_format = oci.generative_ai_inference.models.BaseChatRequest.API_FORMAT_GENERIC
        chat_request.messages = messages
        chat_request.max_tokens = model_data['max_tokens']
        chat_request.temperature = model_data['temperature']
        chat_request.top_p = model_data['top_p']
        chat_request.top_k = model_data['top_k']
        
        # Create chat detail
        chat_detail = oci.generative_ai_inference.models.ChatDetails()
        chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(
            model_id=model_data['model_id']
        )
        chat_detail.chat_request = chat_request
        chat_detail.compartment_id = compartment_id
        
        # Send request
        chat_response = generative_ai_inference_client.chat(chat_detail)
        
        # Extract response text
        if (chat_response.data and 
            chat_response.data.chat_response and 
            chat_response.data.chat_response.choices and 
            len(chat_response.data.chat_response.choices) > 0):
            
            choice = chat_response.data.chat_response.choices[0]
            if (choice.message and 
                choice.message.content and 
                len(choice.message.content) > 0):
                return choice.message.content[0].text
        
        return "Sorry, I couldn't generate a response."
        
    except Exception as e:
        logger.error(f"Error in Grok conversation: {e}")
        return f"Error: {str(e)}"