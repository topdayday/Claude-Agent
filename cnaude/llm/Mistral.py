import boto3
import json

model_data =[
    {
        "model_id": "mistral.mistral-large-2402-v1:0",
        "max_output_tokens": 32768,
        "name": "mistral-large",
    },
    {
        "model_id": "mistral.mixtral-8x7b-instruct-v0:1",
        "max_output_tokens": 32768,
        "name": "mixtral-8x7b",
    },
    {
        "model_id": "mistral.mistral-7b-instruct-v0:2",
        "max_output_tokens": 32768,
        "name": "mistral-7b",
    },
]

bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-west-2")


def start_conversation_mistral(input_content):
    mistral_model = model_data[0]
    model_id = mistral_model['model_id']
    body = json.dumps({
        "prompt": "<s>[INST] %s [/INST]" % input_content,
        "max_tokens": model_id['max_output_tokens'],
        "temperature": 0.5,
        "top_p": 0.9,
        "top_k": 50,
    })
    output_content = ''
    try:
        response = bedrock.invoke_model(body=body, modelId=model_id)
        response_body = json.loads(response.get("body").read().decode('utf-8'))
        output_content = response_body.get("outputs")
        output_content = output_content[0]['text']
    except BaseException as e:
        print(e.args)
    return output_content


if __name__ == '__main__':
    output = start_conversation_mistral('what is your name ?')
    print(output)








