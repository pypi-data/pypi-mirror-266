#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
from novita_client import NovitaClient, Img2ImgV3ControlNetUnit, Samplers, Img2V3ImgLoRA, Img2ImgV3Embedding
from novita_client.utils import base64_to_image, input_image_to_pil
from PIL import Image


def make_image_grid(images, rows: int, cols: int, resize: int = None):
    """
    Prepares a single grid of images. Useful for visualization purposes.
    """
    assert len(images) == rows * cols

    if resize is not None:
        images = [img.resize((resize, resize)) for img in images]

    w, h = images[0].size
    grid = Image.new("RGB", size=(cols * w, rows * h))

    for i, img in enumerate(images):
        grid.paste(img, box=(i % cols * w, i // cols * h))
    return grid


client = NovitaClient(os.getenv('NOVITA_API_KEY'), os.getenv('NOVITA_API_URI', None))
input_image = input_image_to_pil("https://img.freepik.com/premium-photo/close-up-dogs-face-with-big-smile-generative-ai_900101-62851.jpg")

res = client.img2img_v3(
    input_image=input_image,
    model_name="sd_xl_base_1.0.safetensors",
    prompt="a cute dog, cricle logo, colorful, masterpiece, best quality",
    sampler_name=Samplers.EULER_A,
    width=1024,
    height=1024,
    steps=20,
    strength=1.0,
    embeddings=[
        Img2ImgV3Embedding(
            model_name="boring_sdxl_v1_267593"
        )
    ],
    loras=[
        Img2V3ImgLoRA(
            model_name="LogoRedmondV2-Logo-LogoRedmAF_135681.safetensors",
            strength=1.0
        )
    ],
    controlnet_units=[
        Img2ImgV3ControlNetUnit(
            image_base64=input_image,
            model_name="controlnet-softedge-sdxl-1.0",
            preprocessor=None,
            guidance_start=0.0,
            guidance_end=0.5,
            strength=0.8,
        )
    ],
    seed=1024,
)


# base64_to_image(res.images_encoded[0]).save("./img2img-logo.png")
make_image_grid([input_image, base64_to_image(res.images_encoded[0])], 1, 2, resize=512).save("./img2img-logo.png")
