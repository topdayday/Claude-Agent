# gcloud auth application-default login
import vertexai
from vertexai.preview.generative_models import GenerativeModel

def gemini_content(content_in, previous_content_in):
    config = {
        "max_output_tokens": 2048,
        "temperature": 0.5,
        "top_p": 1
    }
    vertexai.init(project='{your_project_id}', location='us-west1')
    model = GenerativeModel("gemini-pro")
    chat = model.start_chat()
    if previous_content_in:
        chat.send_message(previous_content_in, generation_config=config)
    message_out = chat.send_message(content_in, generation_config=config)
    message_out_txt = message_out.candidates[0].content.parts[0].text
    print('message_out_txt:'+message_out_txt)
    return message_out_txt


