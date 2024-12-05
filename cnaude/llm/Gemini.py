from vertexai.generative_models._generative_models import ResponseBlockedError
from vertexai.preview.generative_models import GenerativeModel

# temperature
# 温度取值范围【0-2】
# 温度可以控制词元选择的随机性。较低的温度适合希望获得真实或正确回复的提示，
# 而较高的温度可能会引发更加多样化或意想不到的结果。
# 如果温度为 0，系统始终会选择概率最高的词元。

# max_output_tokens
# 输出词元取值范围
# 输出词元限制决定了一条提示的最大文本输出量。
# 一个词元约为 4 个字符。
models_data = [
    {
        "model_id": "gemini-1.5-pro-002",
        "max_output_tokens": 8192,
        "temperature": 1.0,
        "top_p": 1,
        "description": "2M content window",
        "type": "multiplex",
    },
    {
        "model_id": "gemini-1.5-pro-preview-0409",
        "max_output_tokens": 8192,
        "temperature": 1.0,
        "top_p": 1,
        "description": "1M content window",
        "type": "multiplex",
    },
    {
        "model_id": "gemini-1.0-pro-vision-001",
        "max_output_tokens": 2048,
        "temperature": 1.0,
        "top_p": 1,
        "description": "针对视觉进行了优化,稳定",
        "type": "multiplex",
    },
    {
        "model_id": "gemini-1.0-pro-001",
        "max_output_tokens": 8192,
        "temperature": 1.0,
        "top_p": 1,
        "description": "性能稳定优化版",
        "type": "text",
    },
    {
        "model_id": "gemini-1.0-pro-002",
        "max_output_tokens": 8192,
        "temperature": 1.0,
        "top_p": 1,
        "description": "性能稳定优化版",
        "type": "text",
    },
    {
        "model_id": "gemini-pro",
        "max_output_tokens": 2048,
        "temperature": 1.0,
        "top_p": 1,
        "description": "早期版本",
        "type": "text",
    },
]


def start_conversation_gemini(content_in, model_index=0):
    model_data = models_data[model_index]
    config = {
        "max_output_tokens": model_data['max_output_tokens'],
        "temperature":  model_data['temperature'],
        "top_p": model_data['top_p'],
    }
    output_content = ''
    model = GenerativeModel(model_data['model_id'])
    chat = model.start_chat()
    try:
        message_out = chat.send_message(content_in, generation_config=config)
        output_content = message_out.candidates[0].content.parts[0].text
    except ResponseBlockedError as e:

        print(e.args)
    return output_content


if __name__ == '__main__':
    output = start_conversation_gemini('what is your name ?')
    print('===>  ' + output)
    # for model_idx in range(5):
    #     output = start_conversation_gemini('what is your name ?', model_idx)
    #     print(models_data[model_idx]['model_id'] + '===>  ' + output)
