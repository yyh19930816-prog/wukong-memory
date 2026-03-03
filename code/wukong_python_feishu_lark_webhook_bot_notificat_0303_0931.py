#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feishu-Stablediffusion 集成脚本
学习来源: GitHub仓库 ConnectAI-E/Feishu-Stablediffusion
日期: 2023-10-15
功能: 通过飞书机器人调用Stable Diffusion API实现文生图、图生图、图生文功能
"""

import requests
import json
from typing import Optional
from PIL import Image
import io
import base64
import argparse

class StableDiffusionClient:
    """Stable Diffusion API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:7860"):
        """
        初始化SD客户端
        :param base_url: Stable Diffusion WebUI的API地址，默认本地7860端口
        """
        self.base_url = base_url.rstrip('/')
        
    def txt2img(self, 
               prompt: str, 
               negative_prompt: str = "",
               steps: int = 20,
               width: int = 512,
               height: int = 512,
               seed: int = -1) -> Image.Image:
        """
        文本生成图片
        :param prompt: 正向提示词
        :param negative_prompt: 反向提示词
        :param steps: 迭代步数
        :param width: 图片宽度
        :param height: 图片高度
        :param seed: 随机种子
        :return: PIL图片对象
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
            f"{self.base_url}/sdapi/v1/txt2img",
            json=payload
        )
        response.raise_for_status()
        
        # 解码base64图片数据
        image_data = base64.b64decode(response.json()['images'][0])
        return Image.open(io.BytesIO(image_data))
    
    def img2img(self,
               init_image: Image.Image,
               prompt: str,
               negative_prompt: str = "",
               steps: int = 20,
               denoising_strength: float = 0.75,
               seed: int = -1) -> Image.Image:
        """
        图片生成图片
        :param init_image: 初始图片(PIL对象)
        :param prompt: 正向提示词
        :param negative_prompt: 反向提示词
        :param steps: 迭代步数
        :param denoising_strength: 去噪强度(0-1)
        :param seed: 随机种子
        :return: PIL图片对象
        """
        # 将PIL图片转为base64
        buffered = io.BytesIO()
        init_image.save(buffered, format="PNG")
        init_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        payload = {
            "init_images": [init_image_base64],
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": steps,
            "denoising_strength": denoising_strength,
            "seed": seed
        }
        
        response = requests.post(
            f"{self.base_url}/sdapi/v1/img2img",
            json=payload
        )
        response.raise_for_status()
        
        # 解码base64图片数据
        image_data = base64.b64decode(response.json()['images'][0])
        return Image.open(io.BytesIO(image_data))
    
    def img2txt(self, image: