#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feishu-StableDiffusion 集成脚本
学习来源: https://github.com/ConnectAI-E/Feishu-Stablediffusion
日期: 2023-10-15
功能描述: 通过Python实现Stable Diffusion WebUI的API调用，支持文生图(txt2img)、图生图(img2img)和图生文(img2txt)三种模式
"""

import requests
import base64
from io import BytesIO
from PIL import Image
import json

class StableDiffusionFeishuBot:
    def __init__(self, api_url="http://127.0.0.1:7860"):
        """
        初始化Stable Diffusion API客户端
        :param api_url: Stable Diffusion WebUI的API地址
        """
        self.api_url = api_url.rstrip('/')
        self.headers = {'Content-Type': 'application/json'}
        
    def txt2img(self, prompt, negative_prompt="", steps=20, width=512, height=512, seed=-1):
        """
        文生图功能 - 通过文本提示生成图片
        :param prompt: 正面提示词(支持中文)
        :param negative_prompt: 负面提示词(可选)
        :param steps: 迭代步数(默认20)
        :param width: 图片宽度(默认512)
        :param height: 图片高度(默认512)
        :param seed: 随机种子(默认-1表示随机)
        :return: PIL.Image对象
        """
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": steps,
            "width": width,
            "height": height,
            "seed": seed
        }
        
        response = requests.post(
            f"{self.api_url}/sdapi/v1/txt2img", 
            headers=self.headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            img_data = base64.b64decode(response.json()['images'][0])
            return Image.open(BytesIO(img_data))
        else:
            raise Exception(f"生成失败: {response.text}")
    
    def img2img(self, image, prompt, negative_prompt="", steps=20, denoising_strength=0.7):
        """
        图生图功能 - 基于输入图片生成新图片
        :param image: PIL.Image对象
        :param prompt: 正面提示词
        :param negative_prompt: 负面提示词(可选)
        :param steps: 迭代步数(默认20)
        :param denoising_strength: 降噪强度(0-1,默认0.7)
        :return: PIL.Image对象
        """
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        payload = {
            "init_images": [img_base64],
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": steps,
            "denoising_strength": denoising_strength
        }
        
        response = requests.post(
            f"{self.api_url}/sdapihealth_check/img2img", 
            headers=self.headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            img_data = base64.b64decode(response.json()['images'][0])
            return Image.open(BytesIO(img_data))
        else:
            raise Exception(f"图生图失败: {response.text}")
    
    def