#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
edge-tts 文字转语音示例脚本
学习来源: GitHub仓库 rany2/edge-tts (https://github.com/rany2/edge-tts)
创建日期: 2023-10-15
功能描述: 
    1. 列出可用的语音列表
    2. 使用指定语音将文本转为语音并保存为MP3
    3. 同时生成字幕文件(SRT格式)
    4. 支持直接播放语音(Windows系统)
"""

import asyncio
from edge_tts import Communicate, list_voices

async def list_available_voices():
    """列出所有可用的语音"""
    voices = await list_voices()
    
    print("可用的语音列表:")
    print("Name".ljust(35), "Gender".ljust(10), "Locale".ljust(10))
    print("-" * 60)
    
    for voice in voices:
        print(
            voice["Name"].ljust(35),
            voice["Gender"].ljust(10),
            voice["Locale"].ljust(10)
        )

async def text_to_speech(text, voice, output_mp3, output_srt):
    """
    将文本转为语音并保存
    
    Args:
        text: 要转换的文本
        voice: 语音名称(如'zh-CN-YunxiNeural')
        output_mp3: 输出的MP3文件路径
        output_srt: 输出的SRT字幕文件路径
    """
    print(f"正在生成语音文件: {output_mp3}")
    
    communicate = Communicate(text, voice)
    submaker = None
    
    # 同时生成音频和字幕
    with open(output_mp3, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                if submaker is None:
                    from edge_tts import SubMaker
                    submaker = SubMaker()
                submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])
    
    if submaker is not None:
        with open(output_srt, "w", encoding="utf-8") as subtitle_file:
            subtitle_file.write(submaker.generate_subs())

async def main():
    """主函数"""
    # 1. 列出所有可用语音
    await list_available_voices()
    
    # 2. 使用中文语音生成语音文件
    text = "你好，世界！这是一个edge-tts的文字转语音示例。"
    voice = "zh-CN-YunxiNeural"  # 中文男声
    output_mp3 = "output.mp3"
    output_srt = "output.srt"
    
    await text_to_speech(text, voice, output_mp3, output_srt)
    print(f"已生成语音文件: {output_mp3}")
    print(f"已生成字幕文件: {output_srt}")
    
    # 3. windows系统可以直接播放
    import platform
    if platform.system() == "Windows":
        import os
        os.startfile(output_mp3)

if __name__ == "__main__":
    asyncio.run(main())