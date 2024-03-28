import boto3
import json

model_data =[
    {
        "model_id": "meta.llama2-70b-chat-v1",
    },
]

bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-west-2")


def start_conversation_llama(input_content):
    claude_model = model_data[0]['model_id']
    body = json.dumps({
        "prompt": input_content,
        "max_gen_len": 2048,
        "temperature": 0.9,
        "top_p": 0.6,
    })
    output_content = ''
    try:
        response = bedrock.invoke_model(body=body, modelId=claude_model)
        response_body = json.loads(response.get("body").read().decode('utf-8'))
        output_content = response_body.get("generation")
    except BaseException as e:
        print(e.args)
    return output_content


if __name__ == '__main__':
    output = start_conversation_llama('what is your name ?')
    print(output)










