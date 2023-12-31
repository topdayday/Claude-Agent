from vertexai.generative_models._generative_models import ResponseBlockedError
from vertexai.preview.generative_models import GenerativeModel


def gemini_content(content_in, previous_content_in):
    config = {
        "max_output_tokens": 2048,
        "temperature": 0.8,
        "top_p": 0.8
    }
    message_out_txt = ''
    model = GenerativeModel("gemini-pro")
    chat = model.start_chat()
    try:
        if previous_content_in:
            chat.send_message(previous_content_in, generation_config=config)
        message_out = chat.send_message(content_in, generation_config=config)
        message_out_txt = message_out.candidates[0].content.parts[0].text
    except ResponseBlockedError as e:
        print(e.args)
    return message_out_txt


