import boto3
import json

model_data =[
    {
        "model_id": "meta.llama2-70b-chat-v1",
    },
]

bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-west-2")


def start_llama_conversation(input_content):
    claude_model = model_data[0]['model_id']
    body = json.dumps({
        "prompt": input_content,
        "max_gen_len": 2048,
        "temperature": 0.2,
        "top_p": 0.9
    })
    output_content = ''
    try:
        response = bedrock.invoke_model(body=body, modelId=claude_model)
        response_body = json.loads(response.get("body").read().decode('utf-8'))
        output_content = response_body.get("generation")
        output_content = output_content.replace('\n', "<br>")
    except BaseException as e:
        print(e.args)
    return output_content













