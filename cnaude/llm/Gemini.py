from vertexai.generative_models._generative_models import ResponseBlockedError
from vertexai.preview.generative_models import GenerativeModel

model_data = [
    {
        "model_id": "gemini-1.0-pro-001",
    },
    {
        "model_id": "gemini-pro",
    },
]


def start_conversation_gemini(content_in):
    config = {
        "max_output_tokens": 2048,
        "temperature": 0.9,
        "top_p": 0.6,
    }
    output_content = ''
    model = GenerativeModel(model_data[0]['model_id'])
    chat = model.start_chat()
    try:
        message_out = chat.send_message(content_in, generation_config=config)
        output_content = message_out.candidates[0].content.parts[0].text
    except ResponseBlockedError as e:
        print(e.args)
    return output_content


if __name__ == '__main__':
    output = start_conversation_gemini('what is your name ?')
    print(output)