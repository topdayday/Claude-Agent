import boto3
import json
from botocore.exceptions import ClientError

client = boto3.client("bedrock-runtime", region_name="us-west-2")
model_id = "us.deepseek.r1-v1:0"


def start_conversation_deepseek(prompt):
    formatted_prompt = f"""
    <｜begin▁of▁sentence｜><｜User｜>{prompt}<｜Assistant｜><think>\n
    """
    body = json.dumps({
        "prompt": formatted_prompt,
        "max_tokens": 4096,
        "temperature": 0.5,
        "top_p": 0.9,
    })

    try:
        response = client.invoke_model(modelId=model_id, body=body)
        model_response = json.loads(response["body"].read())
        choices = model_response["choices"]
        for index, choice in enumerate(choices):
            # print(f"Choice {index + 1}\n----------")
            # print(f"Text:\n{choice['text']}\n")
            # print(f"Stop reason: {choice['stop_reason']}\n")
            content_out = choice['text']
            content_out = '```'+content_out.replace('</think>', '```\n')
            return content_out
    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        return None


if __name__ == '__main__':
    output = start_conversation_deepseek('who are you ?')
    print(output)









