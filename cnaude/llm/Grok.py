import oci
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Setup basic variables
# Auth Config
compartment_id = "compartment_id"
CONFIG_PROFILE = "DEFAULT"
config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)

# Service endpoint
endpoint = "endpoint"

# Model configuration
models_data = [
    {
        "model_id": "model_id",
        "max_tokens": 131000,
        "temperature": 1.0,
        "top_p": 1.0,
        "top_k": 0,
        "description": "Grok AI Model",
        "type": "text",
    }
]

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