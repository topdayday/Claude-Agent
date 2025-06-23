import boto3
import json
from botocore.exceptions import ClientError
from botocore.client import Config

# 配置超时（单位：秒）
# 你可以根据你的需求调整这些值
timeout_config = Config(
    connect_timeout=60,  # 连接超时设置为60秒
    read_timeout=600,     # 读取超时设置为600秒 (Bedrock 模型响应可能需要一些时间)
    # 可选：配置重试次数
    retries={'max_attempts': 3, 'mode': 'standard'}
)
client = boto3.client(service_name="bedrock-runtime", region_name="us-west-2", config=timeout_config)
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

    token_usage = {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "model_name": "deepseek-r1"
    }

    try:
        response = client.invoke_model(modelId=model_id, body=body)
        model_response = json.loads(response["body"].read())
        choices = model_response["choices"]
        
        # 提取token使用信息
        if "usage" in model_response:
            usage = model_response["usage"]
            token_usage["input_tokens"] = usage.get("prompt_tokens", 0)
            token_usage["output_tokens"] = usage.get("completion_tokens", 0)
            token_usage["total_tokens"] = usage.get("total_tokens", token_usage["input_tokens"] + token_usage["output_tokens"])
        
        for index, choice in enumerate(choices):
            # print(f"Choice {index + 1}\n----------")
            # print(f"Text:\n{choice['text']}\n")
            # print(f"Stop reason: {choice['stop_reason']}\n")
            content_out = choice['text']
            contents = content_out.split('</think>')
            if len(contents) > 1:
                reason_out = contents[0]
                content_out = contents[1]
                return content_out, reason_out, token_usage
            else:
                return content_out, None, token_usage
    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        return None, None, token_usage


if __name__ == '__main__':
    output1, output2, usage = start_conversation_deepseek('who are you？')
    print(output2)
    print('==============================')
    print(output1)
    print('Token Usage:', usage)









