#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
edge-tts Python API 使用示例
学习来源: GitHub rany2/edge-tts 仓库
日期: 2023-11-01
功能: 通过Microsoft Edge的文本转语音服务生成语音文件，并可选生成字幕
"""

import asyncio
from edge_tts import Communicate, VoicesManager

async def text_to_speech(
    text: str,
    output_file: str = "output.mp3",
    subtitle_file: str = None,
    voice_name: str = "en-US-AriaNeural",
    rate: str = "+0%",
    volume: str = "+0%",
) -> None:
    """
    使用Edge TTS将文本转换为语音
    
    参数:
        text: 要转换为语音的文本内容
        output_file: 输出的语音文件路径
        subtitle_file: 输出的字幕文件路径(可选)
        voice_name: 要使用的语音名称
        rate: 语速调整(+10%表示加快10%)
        volume: 音量调整(+10%表示增大10%)
    """
    # 创建Communicate对象配置语音参数
    communicate = Communicate(
        text=text,
        voice=voice_name,
        rate=rate, 
        volume=volume,
    )
    
    # 同时写入音频和字幕文件
    if subtitle_file:
        submaker = await communicate.save(output_file)
        with open(subtitle_file, "w", encoding="utf-8") as file:
            file.write(submaker.generate_subs())
    # 只写入音频文件
    else:
        await communicate.save(output_file)

async def list_available_voices(locale: str = None) -> None:
    """
    列出所有可用的语音选项
    
    参数:
        locale: 可选的语言区域过滤器(如"zh-CN")
    """
    # 获取语音管理器并列出所有语音
    voices = await VoicesManager.create()
    voices_list = voices.voices
    
    # 如果指定了语言区域则进行过滤
    if locale:
        voices_list = [v for v in voices_list if v["Locale"].lower() == locale.lower()]
    
    # 打印语音信息
    print(f"{'Name':<30} {'Gender':<8} {'Locale':<8} {'FriendlyName']")
    print("-" * 70)
    for voice in voices_list:
        print(
            f"{voice['ShortName']:<30} {voice['Gender']:<8} "
            f"{voice['Locale']:<8} {voice['FriendlyName']}"
        )

async def main():
    """主函数演示各种用法"""
    
    # 示例1: 列出所有中文语音
    print("\n可用的中文语音:")
    await list_available_voices("zh-CN")
    
    # 示例2: 生成英文语音文件
    print("\n生成英文语音文件中...")
    await text_to_speech(
        text="Hello, this is a demo of edge-tts Python module.",
 output_file="english.mp3",
        subtitle_file="english.srt",
        voice_name="en-US-AriaNeural",
        rate="+10%",
    )
    
    # 示例3: 生成中文语音文件
    print("\n生成中文语音文件中...")
    await text_to_speech(
        text="你好，这是一个edge-tts模块的演示示例。",
        output_file="chinese.mp3",
        voice_name="zh-CN-YunxiNeural",
        volume="+20%",
    )

if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main())