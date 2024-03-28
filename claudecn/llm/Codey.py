from vertexai.language_models import CodeGenerationModel

model_data =[
    {
        "model_id": "code-bison",
    },
    {
        "model_id": "code-bison-32k",
    },
    {
        "model_id": "code-bison-32k@002",
    },
    {
        "model_id": "code-gecko@001",
    },
]


def start_conversation_codey(content_in, previous_content_in):
    parameters = {
        "candidate_count": 1,
        "max_output_tokens": 2024,
        "temperature": 0.9
    }
    output_content = ''
    try:
        model = CodeGenerationModel.from_pretrained(model_data[1]['model_id'])
        response = model.predict(
            prefix=content_in,
            **parameters
        )
        output_content = response.text
    except BaseException as e:
        print(e.args)
    return output_content


if __name__ == '__main__':
    output = start_conversation_codey('what is your name ?', None)
    print(output)


