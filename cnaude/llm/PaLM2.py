from vertexai.language_models import ChatModel, TextGenerationModel
# temperature
# 温度取值范围【0-1】
# 温度可以控制词元选择的随机性。较低的温度适合希望获得真实或正确回复的提示，
# 而较高的温度可能会引发更加多样化或意想不到的结果。
# 如果温度为 0，系统始终会选择概率最高的词元。

# max_output_tokens
# 输出词元取值范围
# 输出词元限制决定了一条提示的最大文本输出量。
# 一个词元约为 4 个字符。

models_data = [
    {
        "model_id": "chat-bison",
        "max_output_tokens": 2048,
        "temperature": 0.5,
        "type": "text",
    },
    {
        "model_id": "chat-bison-32k",
        "max_output_tokens": 8192,
        "temperature": 0.5,
        "type": "text",
    },
]


def start_conversation_palm2(content_in='', previous_chat_history=[], model_index=0):
    model_data = models_data[model_index]
    config = {
        "max_output_tokens": model_data['max_output_tokens'],
        "temperature":  model_data['temperature'],
    }
    chat_model = ChatModel.from_pretrained(model_data['model_id'])
    input_content = []
    output_content = ''
    input_content_obj = {"role": "user", "content": content_in}
    if previous_chat_history:
        input_content.extend(previous_chat_history)
    input_content.append(input_content_obj)
    output_content_str = "\n".join([f"{m['role']}: {m['content']}" for m in input_content])
    chat = chat_model.start_chat()
    try:
        message_out = chat.send_message(message=output_content_str, temperature=config['temperature'],
                                        max_output_tokens=config['max_output_tokens'])
        output_content = message_out.text
    except BaseException as e:
        print(e.args)
    return output_content


def start_conversation_palm2_text(content_in, model_index=0):
    model_data = models_data[model_index]
    parameters = {
        "candidate_count": 1,
        "max_output_tokens": model_data['max_output_tokens'],
        "temperature":  model_data['temperature'],
        "top_p": 1
    }
    output_content = ''
    try:
        model = TextGenerationModel.from_pretrained(model_data['model_id'])
        response = model.predict(content_in, **parameters)
        output_content = response.text
    except BaseException as e:
        print(e.args)
    return output_content


if __name__ == '__main__':
    for model_idx in range(1):
        output = start_conversation_palm2('what is your name ?', model_idx)
        print(models_data[model_idx]['model_id'] + '===>  ' + output)


