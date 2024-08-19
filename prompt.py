from langchain.prompts import PromptTemplate


DEFAULT_STYLE = "minimalist, simple, clean and abstract background image, and do not contain many patterns, logos, or letters."


def get_translate_llm_prompt(request: str):
    PROMPT = """You are an Assistant for translation. Always change the contents in <request> to English without any explanation and tag.
                
                <request>
                {request}
                </request>
                """

    return PromptTemplate(
                template=PROMPT,
                input_variables=["request"]
            ).format(request=request)


def get_llm_image_prompt(request: str, style: str):
    PROMPT = """You are an Assistant that creates prompts for generate background image by image generator model. The image that Human wants is written in <request>.
                Follow style guide in <style> and write a image creating prompts as detail as possible keeping it to 500 characters or less. Use this fomat without further explanation:
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
    PROMPT = """You are an Assistant that creates prompts for generate background image by image generator model. The image that Human wants is written in <request>.
                Write a images creation prompts as detail as possible keeping it to 500 characters or less to maintain the style of a given image. Use this fomat without further explanation:
                <prompt>prompt</prompt>

                <request>
                {request}
                </request>
                """

    return PromptTemplate(
                template=PROMPT,
                input_variables=["request"]
            ).format(request=request)


def get_image_tags_prompt():
    return """Look at this image and create an image tag. Answer only a list of strings"""