from langchain.prompts import PromptTemplate


DEFAULT_STYLE = "minimalist, simple, clean and abstract background image, and do not contain many patterns, logos, or letters."

def get_llm_image_prompt(request: str, style: str):
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

    return PromptTemplate(
                template=PROMPT,
                input_variables=["style", "request"]
            ).format(style=style,
                     request=request)


def get_mm_llm_image_prompt(request: str):
    PROMPT = """You are an Assistant that creates prompts for generate image by image generator model. The image that Human wants is written in <request>.
                Write three image creation prompts to maintain the style of a given image. Use this fomat without further explanation:
                <prompt>prompt</prompt>

                <request>
                {request}
                </request>
                """

    return PromptTemplate(
                template=PROMPT,
                input_variables=["request"]
            ).format(request=request)