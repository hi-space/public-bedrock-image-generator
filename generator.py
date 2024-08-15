import boto3
import re
import json

from typing import List, Optional
from aws.claude import BedrockClaude
from prompt import get_llm_image_prompt
from utils import display_image
from config import config


def gen_image_prompt(request: str,
                     style: str,
                     temperature: Optional[float] = None,
                     top_p: Optional[float] = None,
                     top_k: Optional[int] = None) -> List[str]:
    prompt = get_llm_image_prompt(request=request, style=style)

    model_kwargs = {}
    if temperature is not None:
        model_kwargs['temperature'] = temperature
    if top_p is not None:
        model_kwargs['top_p'] = top_p
    if top_k is not None:
        model_kwargs['top_k'] = top_k

    claude = BedrockClaude(**model_kwargs)
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

