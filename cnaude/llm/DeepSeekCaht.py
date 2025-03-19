# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Shows how to use the Converse API with DeepSeek-R1 (on demand).
"""

import logging
import boto3

from botocore.client import Config
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

temperature = 0.9
max_tokens = 4096
system_prompts = [{"text": "你是DeepSeek-R1大语言模型，你需求竭尽全力专为人类提供帮助。"}]
model_id = "us.deepseek.r1-v1:0"
custom_config = Config(connect_timeout=840, read_timeout=840, region_name="us-west-2")
bedrock_client = boto3.client(service_name='bedrock-runtime', config=custom_config)


def translate_conversation_his_deep_seek(contents):
    chats_history = []
    for content in contents:
        content_out = ''
        if content.content_out and len(content.content_out.strip()) > 0:
            content_out = content.content_out
        elif content.reason_out and len(content.reason_out.strip()) > 0:
            content_out = content.reason_out
        if len(content_out.strip()) > 0:
            chat_history = format_chat_history(content.content_in, content_out)
            chats_history.extend(chat_history)
    return chats_history


def format_chat_history(content_in, content_out):
    message_in = {
        "role": "user",
        "content": [{"text": content_in}]
    }
    message_out = {"role": "assistant",
                   "content": [{"text": content_out}]}
    return [message_in, message_out]


def generate_conversation(bedrock_client,
                          model_id,
                          system_prompts,
                          messages):
    inference_config = {
        "temperature": temperature,
        "maxTokens": max_tokens,
    }
    # Send the message.
    response = bedrock_client.converse(
        modelId=model_id,
        messages=messages,
        system=system_prompts,
        inferenceConfig=inference_config,
    )

    # Log token usage.
    # token_usage = response['usage']
    # logger.info("Input tokens: %s", token_usage['inputTokens'])
    # logger.info("Output tokens: %s", token_usage['outputTokens'])
    # logger.info("Total tokens: %s", token_usage['totalTokens'])
    # logger.info("Stop reason: %s", response['stopReason'])

    return response


def start_conversation_deep_seek_chat(content_in, previous_chat_history=[]):
    content_out = None
    reason_out = None
    try:
        message = []
        if previous_chat_history:
            message.extend(previous_chat_history)
        message.append(
            {
                "role": "user",
                "content": [{"text": content_in}]
            }
        )
        response = generate_conversation(
            bedrock_client, model_id, system_prompts, message)
        output_message = response['output']['message']
        for content in output_message["content"]:
            if not content:
                continue
            reasoning_content = content.get("reasoningContent")
            if reasoning_content:
                reason_out = reasoning_content['reasoningText']['text']
            else:
                content_out = content['text']
    except ClientError as err:
        message = err.response['Error']['Message']
        logger.error("A client error occurred: %s", message)
        # print(f"A client error occured: {message}")
    else:
        print(
            f"Finished generating text with model {model_id}.")
    return content_out, reason_out

