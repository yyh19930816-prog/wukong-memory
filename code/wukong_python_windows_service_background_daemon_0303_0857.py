#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
edge-tts Python脚本实现
学习来源: GitHub仓库 rany2/edge-tts (https://github.com/rany2/edge-tts)
创建日期: 2023-11-15
功能描述: 通过Python代码使用Microsoft Edge的TTS服务，支持语音合成、语音播放和字幕生成
"""

import asyncio
from edge_tts import Communicate, VoicesManager

async def list_voices():
    """列出所有可用的语音"""
    voices = await VoicesManager.create()
    print("Available voices:")
    print("Name".ljust(30), "Gender".ljust(10), "Locale".ljust(10))
    for voice in voices:
        print(voice["Name"].ljust(30), voice["Gender"].ljust(10), voice["Locale"].ljust(10))

async def text_to_speech(text, voice="en-US-AriaNeural", output_file="output.mp3", subtitle_file=None):
    """
    将文本转换为语音并保存为音频文件
    
    Args:
        text (str): 要转换的文本
        voice (str): 语音名称(默认:en-US-AriaNeural)
        output_file (str): 输出音频文件路径
        subtitle_file (str): 输出字幕文件路径(可选)
    """
    try:
        # 创建通信对象
        communicate = Communicate(text, voice)
        
        # 同时保存音频和字幕
        if subtitle_file:
            submaker = await communicate.save(output_file, subtitle_file)
            print(f"Audio saved to {output_file}")
            print(f"Subtitles saved to {subtitle_file}")
        else:
            await communicate.save(output_file)
            print(f"Audio saved to {output_file}")
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")

async def playback_text(text, voice="en-US-AriaNeural"):
    """
    直接播放转换的语音
    
    Args:
        text (str): 要播放的文本
        voice (str): 语音名称
    """
    try:
        communicate = Communicate(text, voice)
        await communicate.stream()
    except Exception as e:
        print(f"Error occurred: {str(e)}")

async def main():
    """主函数演示所有功能"""
    print("== Testing edge-tts functionalities ==")
    
    # 1. 列出可用语音(前5个)
    print("\n1. Listing first 5 available voices...")
    voices = await VoicesManager.create()
    for i, voice in enumerate(voices[:5]):
        print(f"{i+1}. {voice['Name']} ({voice['Gender']}, {voice['Locale']})")
    
    # 2. 文本转语音并保存
    print("\n2. Converting text to speech and saving...")
    test_text = "Hello, this is a test of Microsoft Edge's text-to-speech service."
    await text_to_speech(
        text=test_text,
        voice="en-US-AriaNeural",
        output_file="hello.mp3",
        subtitle_file="hello.srt"
    )
    
    # 3. 直接播放语音
    print("\n3. Playing back text directly...")
    await playback_text(text="This text is played directly.", voice="en-US-GuyNeural")

    print("\nAll tests completed!")

if __name__ == "__main__":
    asyncio.run(main())