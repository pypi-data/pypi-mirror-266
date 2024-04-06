#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
from novita_client import NovitaClient, Txt2ImgV3LoRA, Samplers, Txt2ImgV3HiresFix, Txt2ImgV3Embedding
from novita_client.utils import base64_to_image


client = NovitaClient(os.getenv('NOVITA_API_KEY'))

res = client.txt2img_v3(
    prompt="cute dog",
    negative_prompt="bad quality",
    image_num=1,
    guidance_scale=1,
    sampler_name=Samplers.DPMPP_SDE_KARRAS,
    model_name="sdxlTurbo_sdxlTurboPruned_187934.safetensors",
    height=512,
    width=512,
    steps=4,
    seed=-1,
    # hires_fix=Txt2ImgV3HiresFix(
    #     upscaler="RealESRGAN_x4plus_anime_6B",  # RealESRGAN_x4plus_anime_6B, RealESRNet_x4plus
    #     target_height=1280,
    #     target_width=1280,
    #     strength=0.3
    # ),
    # sd_vae="vae-ft-mse-840000-ema-pruned.safetensors",
    # loras=[
    #     Txt2ImgV3LoRA(
    #         model_name="more_details_59655",
    #         strength=0.5,
    #     )
    # ],
    # embeddings=[
    #     Txt2ImgV3Embedding(
    #         model_name="BadDream_53202",
    #     )
    # ],
    download_images=True
)

# print(res.get_image_urls())
base64_to_image(res.images_encoded[0]).save("image1.jpg")  # if download_images=True
