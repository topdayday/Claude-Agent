from vertexai.language_models import TextGenerationModel

def start_conversation_palm2(content_in):
    parameters = {
        "candidate_count": 1,
        "max_output_tokens": 2024,
        "temperature": 0.9,
        "top_p": 0.6
    }
    output_content = ''
    try:
        model = TextGenerationModel.from_pretrained("text-bison")
        response = model.predict(content_in, **parameters)
        result = response.text
    except BaseException as e:
        print(e.args)
    return output_content


if __name__ == '__main__':
    output = start_conversation_palm2('what is your name ?')
    print(output)


