import requests
import subprocess
import json
from json import JSONDecodeError
# 配置参数
ENDPOINT = "ENDPOINT"
REGION = "REGION"
PROJECT_ID = "PROJECT_ID"
URL = f"https://{ENDPOINT}/v1beta1/projects/{PROJECT_ID}/locations/{REGION}/endpoints/openapi/chat/completions"
request_token = None


# 构造请求数据
def get_token():
    return subprocess.check_output("gcloud auth print-access-token", shell=True).decode().strip()



# 发送请求并处理流式响应
def stream_chat(content_in):
    try:
        token = get_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        request_data = {
            "model": "meta/llama-3.1-405b-instruct-maas",
            "stream": True,
            "max_tokens": 2048,
            "temperature": 0.9,
            "top_p": 0.95,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": content_in
                        }
                    ]
                }
            ]
        }
        out_put = ''
        with requests.post(URL, headers=headers, json=request_data, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        json_str = decoded_line[6:].strip()
                        # 过滤结束信号或空数据
                        if json_str in ('', '[DONE]'):
                            continue
                        try:
                            json_data = json.loads(json_str)
                            # 严格检查数据结构
                            if "choices" in json_data and json_data["choices"]:
                                choice = json_data["choices"][0]
                                delta = choice.get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    # print(content, end='', flush=True)
                                    out_put += content
                        except JSONDecodeError as e:
                            print(f"JSON解析失败: {json_str}, 错误: {e}")
                        except KeyError as e:
                            print(f"数据结构异常: {json_str}, 错误: {e}")
            return out_put
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        return ''


def start_conversation_vertex_third(content_in):
    out = stream_chat(content_in)
    return out


if __name__ == "__main__":
    content_out = start_conversation_vertex_third('who are you ?')
    print(content_out)
