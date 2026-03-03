#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stable Diffusion 飞书机器人核心功能实现
学习来源: GitHub仓库 ConnectAI-E/Feishu-Stablediffusion
日期: 2023-10-25
功能: 实现txt2img文生图、img2img图生图、img2txt图生文功能
"""

import requests
import base64
from PIL import Image
from io import BytesIO
from typing import Optional

class StableDiffusionBot:
    def __init__(self, base_url: str = "http://localhost:7860"):
        """
        初始化SD API客户端
        :param base_url: Stable Diffusion WebUI API地址，默认本地7860端口
        """
        self.base_url = base_url
        
    def txt2img(self, 
               prompt: str, 
               negative_prompt: str = "",
               width: int = 512,
               height: int = 512,
               steps: int = 20,
               seed: int = -1,
               model: str = "") -> Optional[Image.Image]:
        """
        文字生成图片（txt2img）
        :param prompt: 正面提示词（支持中文）
        :param negative_prompt: 负面提示词（支持中文）
        :param width: 图片宽度
        :param height: 图片高度
        :param steps: 迭代步数
        :param seed: 随机种子，-1表示随机
        :param model: 使用的模型名称
        :return: PIL Image对象或None
        """
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "seed": seed
        }
        if model:
            payload["override_settings"] = {"sd_model_checkpoint": model}
            
        try:
            response = requests.post(f"{self.base_url}/sdapi/v1/txt2img", json=payload)
            response.raise_for_status()
            image_data = base64.b64decode(response.json()["images"][0])
            return Image.open(BytesIO(image_data))
        except Exception as e:
            print(f"Txt2Img error: {e}")
            return None
            
    def img2img(self,
               init_image: Image.Image,
               prompt: str,
               negative_prompt: str = "",
               denoising_strength: float = 0.7,
               steps: int = 20,
               seed: int = -1) -> Optional[Image.Image]:
        """
        图片生成图片（img2img）
        :param init_image: 初始PIL Image对象
        :param prompt: 提示词
        :param negative_prompt: 负面提示词
        :param denoising_strength: 去噪强度(0-1)
        :param steps: 迭代步数
        :param seed: 随机种子，-1表示随机
        :return: PIL Image对象或None
        """
        buffered = BytesIO()
        init_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        payload = {
            "init_images": [img_base64],
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "denoising_strength": denoising_strength,
            "steps": steps,
            "seed": seed
        }
        
        try:
            response = requests.post(f"{self.base_url}/sdapi/v1/img2img", json=payload)
            response.raise_for_status()
            image_data = base64