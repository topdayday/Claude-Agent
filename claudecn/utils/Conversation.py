import boto3
import json

model_data =[
    {
        "model_id": "anthropic.claude-instant-v1",
        "version": "bedrock-2023-05-31",
    },
    {
        "model_id": "anthropic.claude-v2:1",
        "version": "bedrock-2023-05-31",
    },
]

bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-west-2")


def translate_conversation_his(contents):
    his = ''
    for content in contents:
        his += format_chat_history(content.content_in, content.content_out)
    return his


def format_chat_history(content_in, content_out):
    previous_chat_history = '"\n\nHuman: "' + content_in + '"\n\nAssistant: "' + content_out
    return previous_chat_history


def start_conversation(input_content, previous_chat_history, model_type='0'):
    claude_model = model_data[0]['model_id']
    claude_model_version = model_data[0]['version']
    if str(model_type) == '1':
        claude_model = model_data[1]['model_id']
        claude_model_version = model_data[1]['version']
    if previous_chat_history:
        body = json.dumps({
            "prompt": "\n\nHuman: " + previous_chat_history +
                      "\n\nHuman: " + input_content +
                      "\n\nAssistant:",
            "max_tokens_to_sample": 10000,
            "anthropic_version": claude_model_version
        })
    else:
        body = json.dumps({
            "prompt": "\n\nHuman: " + input_content +
                      "\n\nAssistant:",
            "max_tokens_to_sample": 10000,
            "anthropic_version": claude_model_version
        })
    output_content = ''
    try:
        response = bedrock.invoke_model(body=body, modelId=claude_model)
        response_body = json.loads(response.get("body").read())
        output_content = response_body.get("completion")
    except BaseException as e:
        print(e.args)
    return output_content














