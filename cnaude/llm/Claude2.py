import boto3
import json

model_data =[
    {
        "model_id": "anthropic.claude-v2:1",
        "version": "bedrock-2023-05-31",
        "max_output_tokens": 10240,
        "name": "claude-2-1",
    },
]

bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-west-2")


def translate_conversation_his_v2(contents):
    his = ''
    for content in contents:
        his += format_chat_history(content.content_in, content.content_out)
    return his


def format_chat_history(content_in, content_out):
    previous_chat_history = '"\n\nHuman: "' + content_in + '"\n\nAssistant: "' + content_out
    return previous_chat_history


def start_conversation_claude2(input_content, previous_chat_history=[], model_index=0):
    claude_model = model_data[model_index]
    if previous_chat_history:
        body = json.dumps({
            "prompt": "\n\nHuman: " + previous_chat_history +
                      "\n\nHuman: " + input_content +
                      "\n\nAssistant:",
            "temperature": 0.9,
            "max_tokens_to_sample": 10000,
            "top_k": 250,
            "top_p": 0.6,
            "anthropic_version": claude_model['version']
        })
    else:
        body = json.dumps({
            "prompt": "\n\nHuman: " + input_content +
                      "\n\nAssistant:",
            "temperature": 0.9,
            "max_tokens_to_sample": claude_model['max_output_tokens'],
            "top_k": 250,
            "top_p": 0.6,
            "anthropic_version": claude_model['version']
        })
    output_content = ''
    try:
        response = bedrock.invoke_model(body=body, modelId=claude_model['model_id'])
        response_body = json.loads(response.get("body").read())
        output_content = response_body.get("completion")
    except BaseException as e:
        print(e.args)
    return output_content


if __name__ == '__main__':
    output = start_conversation_claude2('what is your name ?', None)
    print(output)











