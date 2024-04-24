import boto3
import json

model_data =[
    {
        "model_id": "anthropic.claude-3-opus-20240229-v1:0",
        "version": "bedrock-2023-05-31",
        "max_output_tokens": 204800,
        "name": "claude-3-opus",
        "description": "最智能的模型，适用于高度复杂的任务",
    },
    {
        "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
        "version": "bedrock-2023-05-31",
        "max_output_tokens": 204800,
        "name": "claude-3-sonnet",
        "description": "在智能和速度之间提供了理想的平衡，适合企业工作负载",
    },
    {
        "model_id": "anthropic.claude-3-haiku-20240307-v1:0",
        "version": "bedrock-2023-05-31",
        "max_output_tokens": 204800,
        "name": "claude-3-haiku",
        "description": "快速响应模型，适用于简单查询和请求",
    },
]

bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-west-2")


def translate_conversation_his_v3(contents):
    chats_history = []
    for content in contents:
        chat_history = format_chat_history(content.content_in, content.content_out)
        chats_history.extend(chat_history)
    return chats_history


def format_chat_history(content_in, content_out):
    chat_history=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": content_in
                }
            ]
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
        "temperature": 0.9,
        "max_tokens": claude_model['max_output_tokens'],
        "top_k": 250,
        "top_p": 0.6,
        "anthropic_version": claude_model['version']
    })
    output_content = ''
    try:
        response = bedrock.invoke_model(body=body, modelId=claude_model['model_id'])
        response_body = json.loads(response.get("body").read())
        output_contents = response_body.get("content")
        for  content in output_contents:
            if content['type'] == 'text':
                output_content = content['text']
    except BaseException as e:
        print(e.args)
    return output_content


if __name__ == '__main__':
    output = start_conversation_claude3('what is your name ?', None)
    print(output)








