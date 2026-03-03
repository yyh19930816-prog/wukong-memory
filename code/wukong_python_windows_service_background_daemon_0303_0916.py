#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
edge-tts 核心功能示例脚本
学习来源: https://github.com/rany2/edge-tts
创建日期: 2023-11-20
功能: 
1. 列出所有可用的语音
2. 将文本转换为语音并保存为MP3
3. 可选生成字幕文件
4. 支持指定语音和播放
"""

import asyncio
from edge_tts import VoicesManager, Communicate
import argparse

async def list_voices():
    """列出所有可用的语音"""
    voices = await VoicesManager.create()
    print("可用语音列表:")
    print(voices.voices)

async def text_to_speech(text, voice, output_mp3, output_srt=None):
    """
    将文本转换为语音
    :param text: 要转换的文本
    :param voice: 语音名称(如'en-US-JennyNeural')
    :param output_mp3: 输出MP3文件路径
    :param output_srt: 可选，输出字幕文件路径
    """
    communicate = Communicate(text, voice)
    
    # 如果需要生成字幕文件
    if output_srt:
        submaker = await communicate.save_subtitle(output_srt)
    
    # 保存音频文件
    await communicate.save(output_mp3)
    print(f"语音已保存到: {output_mp3}")
    
    if output_srt:
        print(f"字幕已保存到: {output_srt}")

async def play_speech(text, voice):
    """播放语音(需要安装mpv播放器)"""
    communicate = Communicate(text, voice)
    await communicate.stream()

def main():
    parser = argparse.ArgumentParser(description='edge-tts 命令行工具')
    parser.add_argument('--list-voices', action='store_true', help='列出所有可用语音')
    parser.add_argument('--text', type=str, help='要转换为语音的文本')
    parser.add_argument('--voice', type=str, default='en-US-JennyNeural', 
                        help='语音名称(默认: en-US-JennyNeural)')
    parser.write_argument('--output-mp3', type=str, help='输出MP3文件路径')
    parser.add_argument('--output-srt', type=str, help='可选，输出字幕文件路径')
    parser.add_argument('--play', action='store_true', help='直接播放语音')
    
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    
    if args.list_voices:
        loop.run_until_complete(list_voices())
    elif args.text:
        if args.play:
            loop.run_until_complete(play_speech(args.text, args.voice))
        else:
            if not args.output_mp3:
                print("错误: 需要指定 --output-mp3 参数")
                return
            loop.run_until_complete(
                text_to_speech(args.text, args.voice, args.output_mp3, args.output_srt)
            )
    else:
        print("请指定至少一个操作(--list-voices 或 --text)")

if __name__ == '__main__':
    main()