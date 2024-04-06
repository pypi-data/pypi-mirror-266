#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
from novita_client import NovitaClient, Txt2ImgV3LoRA, Samplers, Txt2ImgV3HiresFix, Txt2ImgV3Refiner
from novita_client.utils import base64_to_image


client = NovitaClient(os.getenv('NOVITA_API_KEY'), os.getenv('NOVITA_API_URI', None))
# client.set_extra_headers({
#     "X-Novita-Debug-Host": "http://7e30796b0529afb6c59fceecb9099a01-8860.npipe.internal.omniinfer.io:8080"
# })

res = client.txt2img_v3(
    prompt="cinematic still A young woman with long brown hair and blue eyes stands gracefully in a beautiful garden. She wears a flowing pink dress and holds a bouquet of colorful flowers. Sunlight filters through the trees, casting a warm glow. Butterflies flutter around her, adding to the enchanting atmosphere. . emotional, harmonious, vignette, highly detailed, high budget, bokeh, cinemascope, moody, epic, gorgeous, film grain, grainy, masterpiece, best quality",
    negative_prompt="anime, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, worst quality, low quality, jpeg artifacts, watermark, blurry, artist name, wrong",
    image_num=1,
    guidance_scale=7.0,
    sampler_name=Samplers.DPMPP_M_KARRAS,
    model_name="leosamsHelloworldSDXL_helloworldSDXL50_268813.safetensors",
    height=1024,
    width=1024,
    seed=10000,
    loras=[
        Txt2ImgV3LoRA(
            model_name="sdxl_wrong_lora",
            strength=0.8,
        )
    ],
    # hires_fix=Txt2ImgV3HiresFix(
    #     upscaler="RealESRNet_x4plus",
    #     target_height=2048,
    #     target_width=2048,
    #     strength=0.5
    # ),
    # refiner=Txt2ImgV3Refiner(
    #     switch_at=0.75
    # ),
)

base64_to_image(res.images_encoded[0]).save("image1.jpg")
# base64_to_image(res.images_encoded[1]).save("image2.jpg")
