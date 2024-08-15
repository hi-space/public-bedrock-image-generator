import streamlit as st
import random
import base64
from io import BytesIO
from generator import gen_image, gen_image_prompt
from prompt import get_prompt, DEFAULT_STYLE
from params import ImageParams, ImageSize


def initialize_session_state():
    if 'image_prompts' not in st.session_state:
        st.session_state.image_prompts = []

def render_prompt_section(is_llm_prompt):
    st.subheader("Prompt")
    is_llm_prompt = st.checkbox("Using LLM Prompt", value=True)

    prompt_text = st.text_area("Prompt:", disabled=is_llm_prompt)
    style_text = st.text_area(
        "Style:",
        value=DEFAULT_STYLE,
        disabled=not is_llm_prompt
    )
    keyword_text = st.text_area("Keyword:", disabled=not is_llm_prompt)

    if st.button("Generate Prompt", type="secondary"):
        if is_llm_prompt:
            prompt = get_prompt(request=keyword_text, style=style_text)
            st.session_state.image_prompts = gen_image_prompt(prompt)
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
    st.subheader("Configurations")
    with st.expander("Image Configuration", expanded=True):
        num_images = st.slider("Number of Images", min_value=1, max_value=5, value=1, step=1)
        cfg_scale = st.slider("CFG Scale", min_value=1.0, max_value=10.0, value=8.0, step=0.5)
        random_seed = random.randint(0, 2147483646)
        seed = st.number_input("Seed", min_value=0, value=random_seed, max_value=2147483646, step=1)

        size_options = {f"{size.value[0]} X {size.value[1]}": size for size in ImageSize}
        selected_size = st.selectbox("Image Size", options=list(size_options.keys()))
        
        generate_images_button = st.button("Generate Images", type="primary")

    return num_images, cfg_scale, seed, size_options[selected_size], generate_images_button

def generate_images(selected_prompts, num_images, cfg_scale, seed, selected_size):
    st.subheader("Image Generation")
    with st.spinner("Generating..."):
        img_params = ImageParams(seed=seed)
        img_params.set_configuration(count=num_images, size=selected_size, cfg=cfg_scale)
    
        for image_prompt in selected_prompts:
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
