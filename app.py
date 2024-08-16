import streamlit as st
import random
import base64
from io import BytesIO
from generator import gen_image, gen_image_prompt
from prompt import DEFAULT_STYLE
from params import ImageParams, ImageSize


def initialize_session_state():
    if 'image_prompts' not in st.session_state:
        st.session_state.image_prompts = []
    if 'selected_colors' not in st.session_state:
        st.session_state.selected_colors = []
    if 'use_colors' not in st.session_state:
        st.session_state.use_colors = False

def render_prompt_section(is_llm_prompt):
    st.subheader("Prompt")
    is_llm_prompt = st.checkbox("Using LLM Prompt", value=True)

    if is_llm_prompt:
        style_text = st.text_area(
            "Style:",
            value=DEFAULT_STYLE,
            disabled=not is_llm_prompt
        )
        keyword_text = st.text_area("Keyword:", disabled=not is_llm_prompt)
    else:
        prompt_text = st.text_area("Prompt:", disabled=is_llm_prompt)

    llm_config = {}
    with st.expander("LLM Configuration", expanded=False):
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="모델의 창의성을 조절합니다. 값이 높을수록 더 다양하고 예측 불가능한 응답을 생성합니다."
        )
        top_p = st.slider(
            "Top P",
            min_value=0.0,
            max_value=1.0,
            value=0.9,
            step=0.1,
            help="응답에서 선택할 단어의 집합을 확률적으로 제한합니다. 값이 낮을수록 더 확실한 단어들이 선택됩니다."
        )
        top_k = st.slider(
            "Top K",
            min_value=0,
            max_value=500,
            value=250,
            step=5,
            help="응답에서 선택할 단어의 수를 제한합니다. 작은 값은 더 집중된 결과를, 큰 값은 더 다양한 결과를 제공합니다."
        )

        llm_config['temperature'] = temperature
        llm_config['top_p'] = top_p
        llm_config['top_k'] = top_k

    if st.button("Generate Prompt", type="secondary"):
        if is_llm_prompt:
            st.session_state.image_prompts = gen_image_prompt(
                request=keyword_text,
                style=style_text,
                **llm_config
            )
        else:
            st.session_state.image_prompts = [prompt_text]

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
    st.subheader("Image Generation")
    with st.spinner("Generating..."):
        img_params = ImageParams(seed=seed)
        img_params.set_configuration(count=num_images, size=selected_size, cfg=cfg_scale)
    
        for image_prompt in selected_prompts:
            if st.session_state.use_colors:
                body = img_params.color_guide(text=image_prompt, colors=st.session_state.selected_colors)
            else:
                body = img_params.text_to_image(text=image_prompt)
            imgs = gen_image(body=body)
            st.info(image_prompt)
            cols = st.columns(len(imgs))
            for idx, img in enumerate(imgs):
                with cols[idx]:
                    st.image(BytesIO(base64.b64decode(img)))

def main():
    title = "Image Generator with LLM"
    st.set_page_config(page_title=title, layout="wide")    
    st.title(title)

    initialize_session_state()

    col1, col2, col3 = st.columns(3)

    with col1:
        render_prompt_section(True)

    with col2:
        selected_prompts = render_image_prompt_section()

    with col3:
        num_images, cfg_scale, seed, selected_size, generate_images_button = render_configuration_section()

    if generate_images_button:
        generate_images(selected_prompts, num_images, cfg_scale, seed, selected_size)


if __name__ == "__main__":
    main()
