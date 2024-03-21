import boto3
import json

model_data =[
    {
        "model_id": "mistral.mixtral-8x7b-instruct-v0:1",
    },
]

bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-west-2")


api_demo={
 "modelId": "mistral.mixtral-8x7b-instruct-v0:1",
 "contentType": "application/json",
 "accept": "application/json",
 "body": "{\"prompt\":\"<s>[INST] this is where you place your input text [/INST]\", \"max_tokens\":200, \"temperature\":0.5, \"top_p\":0.9, \"top_k\":50}}"
}

prompt_format = "<s>[INST] %s [/INST]"


def start_conversation(input_content):
    claude_model = model_data[0]['model_id']
    body = json.dumps({
        "prompt": prompt_format % input_content,
        "max_tokens": 2048,
        "temperature": 0.5,
        "top_p": 0.9,
        "top_k": 50,
    })
    print(body)
    output_content = ''
    try:
        response = bedrock.invoke_model(body=body, modelId=claude_model)
        response_body = json.loads(response.get("body").read().decode('utf-8'))
        output_content = response_body.get("outputs")
    except BaseException as e:
        print(e.args)
    return output_content




if __name__ == '__main__':
    output_content = start_conversation('用java实现快速排序算法')
    print(output_content)








