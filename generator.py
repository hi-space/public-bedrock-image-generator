import boto3
import re
import json

from typing import List
from aws.claude import BedrockClaude
from utils import display_image
from config import config


def gen_image_prompt(prompt: str) -> List[str]:
    claude = BedrockClaude()
    res = claude.invoke_llm_response(prompt)

    pattern = r'<prompt>(.*?)</prompt>'
    image_prompts = re.findall(pattern, res)
    return image_prompts


def gen_image(body: str, debug: bool = True):
    bedrock = boto3.client(service_name='bedrock-runtime',
                           region_name = config.BEDROCK_REGION)
    response = bedrock.invoke_model(
        body=body,
        modelId=config.IMAGE_GEN_MODEL_ID,
        accept="application/json",
        contentType="application/json"
    )
    response_body = json.loads(response.get("body").read())
    image = response_body.get("images")

    if debug:
        display_image(image)
    return image

