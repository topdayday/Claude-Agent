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
            contents = content_out.split('</think>')
            if len(contents) > 1:
                content_out = contents[0]
                reason_out = contents[1]
                return content_out, reason_out
            else:
                return content_out, None
    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        return None,  None


if __name__ == '__main__':
    output1,  output2 = start_conversation_deepseek('你知道大熊猫吗？')
    print(output2)
    print(output1)









