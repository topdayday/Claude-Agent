import boto3
import json

model_data =[
    {
        "model_id": "meta.llama3-70b-instruct-v1:0",
        "max_output_tokens": 8192,
        "name": "llama3-70b",
    },
    {
        "model_id": "meta.llama3-8b-instruct-v1:0",
        "max_output_tokens": 8192,
        "name": "llama3-8b",
    },
    {
        "model_id": "meta.llama2-70b-chat-v1",
        "max_output_tokens": 4096,
        "name": "llama2-70b",
    },
    {
        "model_id": "meta.llama2-13b-chat-v1",
        "max_output_tokens": 4096,
        "name": "llama2-13b",
    },
]

bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-west-2")


def start_conversation_llama(input_content):
    llama_model = model_data[0]
    body = json.dumps({
        "prompt": input_content,
        "max_gen_len": llama_model['max_output_tokens'],
        "temperature": 0.5,
        "top_p": 0.9,
    })
    output_content = ''
    try:
        response = bedrock.invoke_model(body=body, modelId=llama_model['model_id'])
        response_body = json.loads(response.get("body").read().decode('utf-8'))
        output_content = response_body.get("generation")
    except BaseException as e:
        print(e.args)
    return output_content


if __name__ == '__main__':
    output = start_conversation_llama('what is your name ?')
    print(output)










