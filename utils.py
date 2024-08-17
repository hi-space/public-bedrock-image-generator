import base64
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime
from IPython.display import display, HTML


def encode_image_bytes(image):
    image = Image.open(image)

    max_size = (1000, 1000)
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    buffer = BytesIO()
    image.convert("RGB").save(buffer, format="JPEG")
    resized_image_data = buffer.getvalue()

    encoded_image = base64.b64encode(resized_image_data)
    decoded_image = encoded_image.decode('utf8')
    return decoded_image


def encode_image_base64(img_url):
    try:
        response = requests.get(img_url)
        image_data = response.content
        return encode_image_bytes(BytesIO(image_data))
    except Exception as e:
        print(e)
    return None


def encode_image_base64_from_file(file_path):
    try:
        with open(file_path, 'rb') as img_file:
            image_data = img_file.read()
        return encode_image_bytes(BytesIO(image_data))
    except Exception as e:
        print(e)
    return None


def display_image(utf8):
    if isinstance(utf8, str):
        html = f'<img src="data:image/png;base64,{utf8}" height="300"/>'
        display(HTML(html))
    elif isinstance(utf8, list):
        for img_str in utf8:
            html = f'<img src="data:image/png;base64,{img_str}" height="300"/>'
            display(HTML(html))

def get_current_time():
    return datetime.now().strftime('%y-%m-%d %H:%M:%S')