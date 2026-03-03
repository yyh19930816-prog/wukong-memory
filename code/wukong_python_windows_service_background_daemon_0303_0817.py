#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
edge-tts Python脚本示例
学习来源: GitHub仓库 rany2/edge-tts (https://github.com/rany2/edge-tts)
创建日期: 2023-10-20
功能描述: 
    - 使用Microsoft Edge的文本转语音服务
    - 支持语音选择、文本转语音并保存为MP3
    - 生成同步字幕文件(SRT格式)
"""

import asyncio
from edge_tts import Communicate, VoicesManager
import argparse
import os
import sys

async def list_voices():
    """列出所有可用的语音选项"""
    voices = await VoicesManager.create()
    voice_list = voices.voices
    print("可用语音列表:")
    print(f"{'Name':<35} {'Gender':<8} {'Locale':<10}")
    print("-" * 60)
    for voice in voice_list:
        print(f"{voice['Name']:<35} {voice['Gender']:<8} {voice['Locale']:<10}")

async def text_to_speech(text, voice, output_mp3, output_srt):
    """
    将文本转换为语音并保存文件
    
    参数:
        text (str): 要转换的文本
        voice (str): 语音名称(如'zh-CN-YunxiNeural')
        output_mp3 (str): 输出的MP3文件路径
        output_srt (str): 输出的SRT字幕文件路径
    """
    communicate = Communicate(text, voice)
    await communicate.save(output_mp3)
    if output_srt:
        submaker = communicate.submaker
        with open(output_srt, "w", encoding="utf-8") as file:
            file.write(submaker.generate_subs())

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Edge TTS 文本转语音工具")
    parser.add_argument("--text", help="要转换为语音的文本内容", required=False)
    parser.add_argument("--voice", help="语音名称(如'zh-CN-YunxiNeural')", default="zh-CN-YunxiNeural")
    parser.add_argument("--output", help="输出的MP3文件路径", default="output.mp3")
    parser.add_argument("--subtitles", help="输出的SRT字幕文件路径", default="output.srt")
    parser.add_argument("--list-voices", help="列出所有可用语音", action="store_true")
    return parser.parse_args()

async def main():
    """主函数"""
    args = parse_args()
    
    if args.list_voices:
        await list_voices()
        return
    
    if not args.text:
        print("错误: 必须使用--text参数提供文本内容")
        sys.exit(1)
    
    print(f"正在转换文本: '{args.text}'")
    print(f"使用语音: {args.voice}")
    
    await text_to_speech(args.text, args.voice, args.output, args.subtitles)
    
    print(f"语音已保存到: {args.output}")
    if args.subtitles:
        print(f"字幕已保存到: {args.subtitles}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"发生错误: {str(e)}")