#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
edge-tts Python API示例
学习来源: GitHub仓库 rany2/edge-tts (https://github.com/rany2/edge-tts)
创建日期: 2023-11-15
功能描述: 演示edge-tts库的基本用法，包括文本转语音、语音播放、音色选择和字幕生成
"""

import asyncio
import argparse
from edge_tts import Communicate, list_voices
from edge_tts.exceptions import NoAudioReceived
from pathlib import Path

async def text_to_speech(text, voice, output_audio=None, output_subtitle=None):
    """
    将文本转换为语音并保存为文件
    
    Args:
        text: 要转换的文本
        voice: 音色名称
        output_audio: 音频输出路径(.mp3)
        output_subtitle: 字幕输出路径(.srt)
    """
    try:
        # 创建通信对象
        communicate = Communicate(text, voice)
        
        # 如果需要保存音频和字幕
        if output_audio or output_subtitle:
            # 确保输出目录存在
            if output_audio:
                Path(output_audio).parent.mkdir(parents=True, exist_ok=True)
            if output_subtitle:
                Path(output_subtitle).parent.mkdir(parents=True, exist_ok=True)
                
            # 保存文件和字幕
            await communicate.save(output_audio if output_audio else None, 
                                  output_subtitle if output_subtitle else None)
            print(f"成功生成文件: {output_audio if output_audio else ''} {output_subtitle if output_subtitle else ''}")
        
        # 否则直接播放音频
        else:
            print(f"正在播放语音(音色: {voice})...")
            player = asyncio.create_task(communicate.stream())
            await player
    
    except NoAudioReceived:
        print("错误: 未接收到音频数据")
    except Exception as e:
        print(f"发生错误: {str(e)}")

async def list_all_voices():
    """列出所有可用的语音音色"""
    voices = await list_voices()
    print("\n可用语音音色:")
    print("{:<30} {:<8} {:<20} {:<20}".format("名称", "性别", "内容类别", "音色特点"))
    print("-" * 80)
    for voice in voices:
        print("{:<30} {:<8} {:<20} {:<20}".format(
            voice["Name"], 
            voice["Gender"], 
            ",".join(voice["Locale"]),
            ",".join(voice["VoicePersonalities"])
        ))

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='edge-tts命令行工具')
    parser.add_argument('--text', help='要转换为语音的文本')
    parser.add_argument('--voice', default='zh-CN-YunxiNeural', help='语音音色(默认: zh-CN-YunxiNeural)')
    parser.add_argument('--output-audio', help='音频输出文件路径(.mp3)')
    parser.add_argument('--output-subtitle', help='字幕输出文件路径(.srt)')
    parser.add_argument('--list-voices', action='store_true', help='列出所有可用音色')
    
    args = parser.parse_args()
    
    # 执行相应操作
    loop = asyncio.get_event_loop()
    try:
        if args.list_voices:
            loop.run_until_complete(list_all_voices())
        elif args.text:
            loop.run_until_complete