import random
import json
from typing import List, Optional
from enum import Enum


class ImageSize(Enum):
    SIZE_512x512 = (512, 512)       # 1:1
    SIZE_1024x1024 = (1024, 1024)   # 1:1
    SIZE_768x768 = (768, 768)       # 1:1
    SIZE_768x1152 = (768, 1152)     # 2:3
    SIZE_384x576 = (384, 576)       # 2:3
    SIZE_1152x768 = (1152, 768)     # 3:2
    SIZE_576x384 = (576, 384)       # 3:2
    SIZE_768x1280 = (768, 1280)     # 3:5
    SIZE_384x640 = (384, 640)       # 3:5
    SIZE_1280x768 = (1280, 768)     # 5:3
    SIZE_640x384 = (640, 384)       # 5:3
    SIZE_896x1152 = (896, 1152)     # 7:9
    SIZE_448x576 = (448, 576)       # 7:9
    SIZE_1152x896 = (1152, 896)     # 9:7
    SIZE_576x448 = (576, 448)       # 9:7
    SIZE_768x1408 = (768, 1408)     # 6:11
    SIZE_384x704 = (384, 704)       # 6:11
    SIZE_1408x768 = (1408, 768)     # 11:6
    SIZE_704x384 = (704, 384)       # 11:6
    SIZE_640x1408 = (640, 1408)     # 5:11
    SIZE_320x704 = (320, 704)       # 5:11
    SIZE_1408x640 = (1408, 640)     # 11:5
    SIZE_704x320 = (704, 320)       # 11:5
    SIZE_1152x640 = (1152, 640)     # 9:5
    SIZE_1173x640 = (1173, 640)     # 16:9

    def __init__(self, width, height):
        self.width = width
        self.height = height


class ControlMode(Enum):
    CANNY_EDGE = "CANNY_EDGE"
    SEGMENTATION = "SEGMENTATION"


class ImageParams:
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed if seed is not None else random.randint(0, 2147483646)
        self._config = self._default_configuration()

    '''
    Image Configuration
    '''
    def _default_configuration(self, count: int = 1, size: ImageSize = ImageSize.SIZE_512x512, cfg: float = 8.0) -> dict:
        return {
            "imageGenerationConfig": {
                "numberOfImages": count,  # [1, 5]
                "width": size.width,
                "height": size.height,
                "cfgScale": cfg,  # [1.0, 10.0]
                "seed": self.seed
            }
        }
    
    def get_configuration(self):
        return self._config

    def set_configuration(self, count: int = 1, size: ImageSize = ImageSize.SIZE_512x512, cfg: float = 8.0):
        self._config = self._default_configuration(count, size, cfg)

    def _prepare_body(self, task_type: str, params: dict) -> str:
        body = {
            "taskType": task_type,
            **params
        }
        body.update(self._config)
        return json.dumps(body)


    '''
    Text To Image (with image conditioning)
    '''
    def text_to_image(self,
                      text: str,
                      negative_text: Optional[str] = None,
                      condition_image: Optional[str] = None,
                      control_mode: ControlMode = ControlMode.CANNY_EDGE,
                      control_strength: float = 0.7) -> str:
        params = {
            "textToImageParams": {
                "text": text,
            }
        }

        if negative_text is not None:
            params["textToImageParams"]["negativeText"] = negative_text

        if condition_image is not None:
            params["textToImageParams"].update({
                "conditionImage": condition_image,
                "controlMode": control_mode.value,
                "controlStrength": control_strength
            })

        return self._prepare_body("TEXT_IMAGE", params)
    

    '''
    INPAINTING
    '''
    def inpainting(self,
                   image: str,
                   text: str,
                   mask_prompt: str,                   
                   negative_text: Optional[str] = None) -> str:
        params = {
            "inPaintingParams": {
                "text": text,
                "image": image,
                "maskPrompt": mask_prompt,
                "returnMask": False,
            }
        }

        if negative_text is not None:
            params["inPaintingParams"]["negativeText"] = negative_text

        return self._prepare_body("INPAINTING", params)


    '''
    OUTPAINTING
    '''
    def outpainting(self,
                    image: str,
                    text: str,
                    mask_prompt: str,
                    negative_text: Optional[str] = None) -> str:
        params = {
            "outPaintingParams": {
                "text": text,
                "image": image,
                "maskPrompt": mask_prompt,
                "returnMask": False,
                "outPaintingMode": "DEFAULT",  # ["DEFAULT" | "PRECISE"]
            }
        }

        if negative_text is not None:
            params["outPaintingParams"]["negativeText"] = negative_text

        return self._prepare_body("OUTPAINTING", params)


    '''
    IMAGE_VARIATION
    '''
    def image_variant(self,
                      images: List[str],
                      text: Optional[str] = None,
                      negative_text: Optional[str] = None,
                      similarity: float = 0.7) -> str:
        params = {
            "imageVariationParams": {
                "images": images,
                "similarityStrength": similarity,  # [0.2, 1.0]
            }
        }

        if text is not None:
            params["imageVariationParams"]["text"] = text

        if negative_text is not None:
            params["imageVariationParams"]["negativeText"] = negative_text

        return self._prepare_body("IMAGE_VARIATION", params)


    '''
    COLOR_GUIDED_GENERATION
    '''
    def color_guide(self,
                    text: str,
                    colors: List[str],
                    negative_text: Optional[str] = None,
                    reference_image: Optional[str] = None) -> str:
        params = {
            "colorGuidedGenerationParams": {
                "text": text,
                "colors": colors,
            }
        }

        if negative_text is not None:
            params["colorGuidedGenerationParams"]["negativeText"] = negative_text

        if reference_image is not None:
            params["colorGuidedGenerationParams"]["referenceImage"] = reference_image

        return self._prepare_body("COLOR_GUIDED_GENERATION", params)


    '''
    BACKGROUND_REMOVAL
    '''
    def background_removal(self, image: str) -> str:
        params = {
            "backgroundRemovalParams": {
                "image": image,
            }
        }
        return self._prepare_body("BACKGROUND_REMOVAL", params)
