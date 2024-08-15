from langchain.prompts import PromptTemplate


PROMPT = """You are an Assistant that creates prompts for generate image by image generator model. The image that Human wants is written in <request>.
Follow style guide in <style> and write three image creating prompts. Use this fomat without further explanation: 
<prompt>prompt</prompt>

<request>
{request}
</request>

<style>
{style}
</style>
"""

DEFAULT_STYLE = "minimalist, simple, clean and abstract background image, and do not contain many patterns, logos, or letters."


def get_llm_image_prompt(request, style):
    return PromptTemplate(
                template=PROMPT,
                input_variables=["style", "request"]
            ).format(style=style,
                     request=request)