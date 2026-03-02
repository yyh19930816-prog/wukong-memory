#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Learning from: https://github.com/rany2/edge-tts
# Date: 2023-10-20
# Description: Python script using edge-tts to convert text to speech with various options

import asyncio
import argparse
from edge_tts import Communicate, VoicesManager

async def list_voices():
    """List all available voices from Microsoft Edge TTS service"""
    voices = await VoicesManager.create()
    for voice in voices:
        print(f"{voice['Name']:<35} {voice['Gender']:<8} {voice['ShortName']}")

async def text_to_speech(text, voice, output_file, subtitle_file=None, play=False):
    """
    Convert text to speech using Edge TTS
    
    Args:
        text: Input text to convert
        voice: Voice to use (e.g. 'en-US-JennyNeural')
        output_file: Path to save audio file (MP3)
        subtitle_file: Path to save subtitles file (SRT), None to skip
        play: Whether to play audio immediately
    """
    communicate = Communicate(text, voice)
    
    if output_file:
        submaker = None
        if subtitle_file:
            submaker = communicate.save_subtitles_to_file(subtitle_file)
        
        await communicate.save(output_file)
        if submaker:
            await submaker
        print(f"Audio saved to {output_file}")
        if subtitle_file:
            print(f"Subtitles saved to {subtitle_file}")
    
    if play:
        # Play audio directly if requested
        print("Playing audio...")
        await communicate.stream()

def main():
    parser = argparse.ArgumentParser(description="Microsoft Edge Text-to-Speech CLI")
    parser.add_argument("--text", help="Text to convert to speech")
    parser.add_argument("--voice", default="en-US-JennyNeural", 
                       help="Voice to use (default: en-US-JennyNeural)")
    parser.add_argument("--output", help="Output audio file path (MP3)")
    parser.add_argument("--subtitle", help="Output subtitle file path (SRT)")
    parser.add_argument("--play", action="store_true", 
                       help="Play audio immediately")
    parser.add_argument("--list-voices", action="store_true", 
                       help="List all available voices")

    args = parser.parse_args()

    if args.list_voices:
        asyncio.run(list_voices())
    elif args.text:
        asyncio.run(text_to_speech(
            args.text, 
            args.voice, 
            args.output, 
            args.subtitle, 
            args.play
        ))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()