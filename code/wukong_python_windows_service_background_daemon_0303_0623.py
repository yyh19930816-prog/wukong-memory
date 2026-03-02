#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# edge_tts_demo.py
# 
# Learn from GitHub repo: rany2/edge-tts (https://github.com/rany2/edge-tts)
# Created: 2023-10-20
# Description: Python script demonstrating core features of edge-tts library
# Features: Text-to-speech conversion with voice selection, saving audio/subtitles

import asyncio
import edge_tts
from edge_tts import VoicesManager, Communicate

async def list_available_voices():
    """List all available TTS voices"""
    voices = await VoicesManager.create()
    print("Available Voices:")
    for idx, (name, voice) in enumerate(voices.items(), 1):
        print(f"{idx}. {name}")
        print(f"   Gender: {voice['Gender']}")
        print(f"   Locale: {voice['Locale']}")
        print(f"   ShortName: {voice['ShortName']}\n")

async def text_to_speech(text, output_file, voice=None, subtitles=False):
    """
    Convert text to speech using Edge TTS API
    
    Args:
        text: Input text to convert
        output_file: Path to save audio file (.mp3)
        voice: Voice short name (e.g. 'en-US-AnaNeural')
        subtitles: Whether to generate subtitles file (.srt)
    """
    # If no voice specified, use default
    if voice is None:
        communicate = Communicate(text)
    else:
        communicate = Communicate(text, voice=voice)
    
    # Prepare subtitle file path if enabled
    subtitle_file = None
    if subtitles:
        subtitle_file = output_file.replace('.mp3', '.srt')
    
    print(f"Generating speech for: '{text}'")
    if voice:
        print(f"Using voice: {voice}")
    
    # Save audio and optionally subtitles
    await communicate.save(output_file, subtitle_file)
    print(f"Audio saved to: {output_file}")
    if subtitles:
        print(f"Subtitles saved to: {subtitle_file}")

async def main():
    """Main demo function"""
    print("\n=== Edge TTS Demo ===\n")
    
    # List available voices
    await list_available_voices()
    
    # Example 1: Basic text to speech
    await text_to_speech(
        text="Hello, this is Microsoft Edge text-to-speech service.",
        output_file="output_basic.mp3",
        subtitles=True
    )
    
    # Example 2: Using specific voice
    await text_to_speech(
        text="Bonjour, ceci est une démonstration de synthèse vocale.",
        output_file="output_french.mp3",
        voice="fr-FR-HenriNeural",
        subtitles=True
    )
    
    # Example 3: Non-English text
    await text_to_speech(
        text="こんにちは、これはMicrosoft Edgeのテキスト読み上げサービスです",
        output_file="output_japanese.mp3",
        voice="ja-JP-NanamiNeural",
        subtitles=True
    )

if __name__ == "__main__":
    asyncio.run(main())