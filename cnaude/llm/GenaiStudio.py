import base64
import os
from google import genai
from google.genai import types

client = genai.Client(
    api_key='app-key',
)
model = "gemini-2.5-pro-exp-03-25"


def translate_conversation_his_genai(contents):
    chats_history = []
    for content in contents:
        chat_history = format_chat_history(content.content_in, content.content_out)
        chats_history.extend(chat_history)
    return chats_history


def format_chat_history(content_in, content_out):
    message_in = types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=content_in),
            ],
        )
    message_out = types.Content(
        role="model",
        parts=[
            types.Part.from_text(text=content_out),
        ],
    )
    return [message_in, message_out]


def start_conversation_genai(content_in, previous_chat_history=[], model_index=0):
    contents = []
    if previous_chat_history:
        contents.extend(previous_chat_history)
    contents.append(types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=content_in),
            ],
        ))
    generate_content_config = types.GenerateContentConfig(
        temperature=1.0,
        top_p=0.9,
        max_output_tokens=65535,
        response_mime_type="text/plain",
    )
    result = ''
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        # print(chunk.text, end="")
        result += chunk.text
    return result


if __name__ == "__main__":
    result = start_conversation_genai('who are you', [], 0)
    print(result)
