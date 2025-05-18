"""
Keyboard-based speech module for DJGPT when microphones aren't working.
This module replaces speech recognition with simple keyboard input.
"""
import time
from typing import Optional

from AppKit import NSSpeechSynthesizer
from utils import CONSOLE

# Initialize text-to-speech
TTS = NSSpeechSynthesizer.alloc().init()

def _wait_for_speech_to_finish():
    """Wait for text-to-speech to finish"""
    while TTS.isSpeaking():
        time.sleep(0.5)

def say(text: str, wait: bool = False):
    """Text-to-speech using NSSpeechSynthesizer"""
    CONSOLE.print(text)
    
    # Don't interrupt previous startSpeaking as it cancels to the most recent
    _wait_for_speech_to_finish()
    TTS.startSpeakingString_(text)
    
    # Be a blocking call instead of OS level asynchronous
    if wait:
        _wait_for_speech_to_finish()

def listen() -> Optional[str]:
    """
    Get user input via keyboard instead of microphone.
    This is a fallback for when speech recognition doesn't work.
    """
    CONSOLE.print("[bold yellow]Microphone not working. Please type your request instead:[/]")
    try:
        user_input = input("> ")
        if user_input.strip() == "":
            return None
        return user_input
    except KeyboardInterrupt:
        return None
    except Exception as e:
        CONSOLE.log(f"[bold red]Error getting keyboard input: {str(e)}")
        return None
