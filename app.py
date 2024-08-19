import uuid
import json
import base64
from concurrent.futures import ThreadPoolExecutor
import streamlit as st
import pandas as pd
from enum import Enum
from io import BytesIO
from generator import (
    gen_image, gen_image_prompt, gen_mm_image_prompt, gen_tags, gen_english
)
from prompt import DEFAULT_STYLE
from params import ImageParams, ImageSize
from utils import encode_image_bytes, get_current_time
from aws.dynamodb import DynamoDB, _decimal_default
from aws.s3 import S3
from config import config


s3 = S3(bucket_name=config.S3_BUCKET)
db = DynamoDB(table_name=config.DYNAMODB_TABLE)

class PromptTab(Enum):
    BASIC_PROMPT = "Basic Prompt"
    LLM_PROMPT = "LLM Prompt"
    MM_LLM_PROMPT = "Multimodal LLM Prompt"


def initialize_session_state():
    if 'image_prompts' not in st.session_state:
        st.session_state.image_prompts = []
    if 'selected_colors' not in st.session_state:
        st.session_state.selected_colors = []
    if 'use_colors' not in st.session_state:
        st.session_state.use_colors = False


def render_prompt_section():
    st.subheader("Prompt")

    selected_option = st.selectbox(
        "Choose an option:", 
        [tab.value for tab in PromptTab]
    )

    if selected_option == PromptTab.BASIC_PROMPT.value:
        prompt_text = st.text_area("Enter your prompt:")

    elif selected_option == PromptTab.LLM_PROMPT.value:
        style_text = st.text_area("Enter the style:", value=DEFAULT_STYLE)
        keyword_text = st.text_area("Enter the keyword:")

    elif selected_option == PromptTab.MM_LLM_PROMPT.value:
        reference_image = st.file_uploader("Upload a reference image:")
        if reference_image is not None:
            with st.expander("Image Preview"):
                st.image(reference_image, caption="Uploaded Image", use_column_width=True)
        multimodal_keyword_text = st.text_area("Enter the multimodal keyword:")

    llm_config = {}
    with st.expander("LLM Configuration", expanded=False):
        temperature = st.slider(
            "Temperature",
            min_value=0.0, max_value=1.0, value=0.7, step=0.1,
            help="모델의 창의성을 조절합니다. 값이 높을수록 더 다양하고 예측 불가능한 응답을 생성합니다."
        )
        top_p = st.slider(
            "Top P",
            min_value=0.0, max_value=1.0, value=0.9, step=0.1,
            help="응답에서 선택할 단어의 집합을 확률적으로 제한합니다. 값이 낮을수록 더 확실한 단어들이 선택됩니다."
        )
        top_k = st.slider(
            "Top K",
            min_value=0, max_value=500, value=250, step=5,
            help="응답에서 선택할 단어의 수를 제한합니다. 작은 값은 더 집중된 결과를, 큰 값은 더 다양한 결과를 제공합니다."
        )

        llm_config['temperature'] = temperature
        llm_config['top_p'] = top_p
        llm_config['top_k'] = top_k

    if st.button("Generate Prompt", type="primary"):
        if selected_option == PromptTab.BASIC_PROMPT.value:
            st.session_state.image_prompts.extend([gen_english(request=prompt_text)])

        elif selected_option == PromptTab.LLM_PROMPT.value:
            st.session_state.image_prompts.extend(gen_image_prompt(
                request=keyword_text,
                style=style_text,
                **llm_config
            ))

        elif selected_option == PromptTab.MM_LLM_PROMPT.value:
            image = encode_image_bytes(reference_image)
            st.session_state.image_prompts.extend(gen_mm_image_prompt(
                request=multimodal_keyword_text,
                image=image,
                **llm_config
            ))


def render_image_prompt_section():
    st.subheader("Image Prompt")
    selected_prompts = st.multiselect(
        "Select Prompts to Generate Images",
        options=st.session_state.image_prompts,
        default=st.session_state.image_prompts,
    )
    
    for i, prompt in enumerate(selected_prompts):
        selected_prompts[i] = st.text_area(f"Prompt {i + 1}", value=prompt, key=f"selected_prompt_{i}", height=50)
    
    return selected_prompts


def render_configuration_section():
    st.subheader("Image Configurations")
    with st.expander("Image Configuration", expanded=True):
        num_images = st.slider("Number of Images", min_value=1, max_value=5, value=1, step=1)
        cfg_scale = st.slider("CFG Scale", min_value=1.0, max_value=10.0, value=8.0, step=0.5)
        seed = st.number_input("Seed", min_value=0, value=0, max_value=2147483646, step=1)
        size_options = {f"{size.value[0]} X {size.value[1]}": size for size in ImageSize}
        selected_size = st.selectbox("Image Size", options=list(size_options.keys()))
        
        st.session_state.use_colors = st.checkbox("Using color references", value=False)
        if st.session_state.use_colors:
            color_picker = st.color_picker("Pick a color")
            if color_picker and color_picker not in st.session_state.selected_colors and len(st.session_state.selected_colors) < 10:
                st.session_state.selected_colors.append(color_picker)
            
            st.session_state.selected_colors = st.multiselect(
                "Selected Colors",
                options=st.session_state.selected_colors,
                default=st.session_state.selected_colors,
                max_selections=10,
            )
            
            if st.session_state.selected_colors:
                color_html = "<div style='display: flex; flex-wrap: wrap;'>"
                for color in st.session_state.selected_colors:
                    color_html += f"""<div style='width: 24px; height: 24px; background-color: {color}; margin-left: 5px; margin-bottom: 8px; border-radius: 5px;'></div>"""
                color_html += "</div>"
                st.markdown(color_html, unsafe_allow_html=True)

    generate_images_button = st.button("Generate Images", type="primary")

    return num_images, cfg_scale, seed, size_options[selected_size], generate_images_button


def generate_images(selected_prompts, num_images, cfg_scale, seed, selected_size):
    def _generate_image_task(image_prompt, img_params, cfg, use_colors, selected_colors):
        if use_colors:
            body = img_params.color_guide(text=image_prompt, colors=selected_colors)
            cfg['colorGuide'] = selected_colors
        else:
            body = img_params.text_to_image(text=image_prompt)
        
        imgs = gen_image(body=body)

        return image_prompt, imgs, cfg
    
    def _show_and_upload_images(results = []):
        for image_prompt, imgs, cfg in results:
            st.info(image_prompt)
            cols = st.columns(len(imgs))
            for idx, img in enumerate(imgs):
                with cols[idx]:
                    image_data = BytesIO(base64.b64decode(img))

                    try:
                        tags = json.loads(gen_tags(img))
                    except:
                        tags = []

                    st.image(image_data)
                    st.write(tags)

                    with st.spinner("Upload..."):
                        upload_image(
                            image=image_data,
                            prompt=image_prompt,
                            cfg=cfg,
                            tags=tags
                        )
    
    st.divider()
    st.subheader("Image Generation")
    with st.status("Generating...", expanded=True):
        img_params = ImageParams(seed=seed)
        img_params.set_configuration(count=num_images, size=selected_size, cfg=cfg_scale)

        results = []
        with ThreadPoolExecutor() as executor:
            futures = []
            for image_prompt in selected_prompts:
                cfg = img_params.get_configuration()
                futures.append(executor.submit(_generate_image_task, image_prompt, img_params, cfg, st.session_state.use_colors, st.session_state.selected_colors))
            
            for future in futures:
                results.append(future.result())

        _show_and_upload_images(results)

def upload_image(image: bytes, prompt: str, cfg: dict, tags = []):
    image_id = f"{uuid.uuid4()}.png"
    s3.upload_object(key=image_id, bytes=image, extra_args={'ContentType': 'image/png'})
    db.put_item({
        "id": image_id,
        "url": f"{config.CDN_URL}/{image_id}",
        "prompt": prompt,
        "config": cfg,
        "tags": tags,
        "created": get_current_time()
    })


def render_gallery():
    items = db.scan_items({}).get("Items")
    
    df = pd.DataFrame(
        items,
        columns=["url", "prompt", "tags", "config", "created"],
    )
    df["config"] = df["config"].apply(lambda x: json.dumps(x, default=_decimal_default))
    df = df.sort_values(by="created", ascending=False)
    
    st.dataframe(
        df, 
        column_config={
            "url": st.column_config.ImageColumn(label="image"),
            "tags": st.column_config.ListColumn(label="tags")
        },
        hide_index=True,
        use_container_width=True
    ) 


def main():
    title = "🚀 MM-LLM Prompt-to-Image Generation"
    st.set_page_config(page_title=title, layout="wide")    
    st.title(title)

    initialize_session_state()
    
    tab1, tab2 = st.tabs(["🎨 Image Generator", "🖼️ Image Gallery"])
    
    with tab1:
        col1, col2, col3 = st.columns(3)

        with col1:
            render_prompt_section()

        with col2:
            selected_prompts = render_image_prompt_section()

        with col3:
            num_images, cfg_scale, seed, selected_size, generate_images_button = render_configuration_section()

        if generate_images_button:
            generate_images(selected_prompts, num_images, cfg_scale, seed, selected_size)

    with tab2:
        render_gallery()


if __name__ == "__main__":
    main()
