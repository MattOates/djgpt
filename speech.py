"""Cross-platform speech module for text-to-speech and speech-to-text functionality."""
import time
from functools import cache
from typing import Optional
import logging

from speech_recognition import (
    Recognizer,
    Microphone,
    UnknownValueError,
    RequestError,
    WaitTimeoutError
)

from utils import CONSOLE, retry

# Initialize text-to-speech engines
USE_PYTTSX3 = False
try:
    import pyttsx3
    tts_engine = pyttsx3.init()
    USE_PYTTSX3 = True
    print("Using pyttsx3 for speech synthesis")
except Exception as e:
    print(f"Error initializing pyttsx3: {str(e)}")
    print("Falling back to NSSpeechSynthesizer...")
    from AppKit import NSSpeechSynthesizer
    TTS = NSSpeechSynthesizer.alloc().init()

def _wait_for_speech_to_finish():
    """Wait for text-to-speech to finish"""
    if USE_PYTTSX3:
        if hasattr(tts_engine, '_inLoop') and tts_engine._inLoop:
            tts_engine.endLoop()
    else:
        while TTS.isSpeaking():  # loop until it finish speaking
            time.sleep(0.5)

def say(text: str, wait: bool = False):
    """Cross-platform text-to-speech"""
    CONSOLE.print(text)
    
    if USE_PYTTSX3:
        tts_engine.say(text)
        if wait:
            tts_engine.runAndWait()
    else:
        # Use NSSpeechSynthesizer implementation as fallback
        # Don't interrupt previous startSpeaking as it cancels to the most recent
        _wait_for_speech_to_finish()
        TTS.startSpeakingString_(text)
        
        # Be a blocking call instead of OS level asynchronous
        if wait:
            _wait_for_speech_to_finish()

@cache
def get_sr():
    """Get the cached recognizer instance."""
    recognizer = Recognizer()
    mic = Microphone()
    return recognizer, mic

@retry
def listen() -> Optional[str]:
    """Use multiple speech recognition engines with fallback options."""
    # Wait for speech to finish first
    _wait_for_speech_to_finish()
    
    with CONSOLE.status("[bold green]Listening...") as status:
        try:
            recognizer, mic = get_sr()
            
            with mic as source:
                # Adjust for ambient noise
                try:
                    recognizer.adjust_for_ambient_noise(source)
                except Exception as e:
                    CONSOLE.log(f"[bold yellow]Ambient noise error: {str(e)}")
                
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                except WaitTimeoutError:
                    CONSOLE.log("[bold red]No speech detected")
                    return None
                except Exception as e:
                    CONSOLE.log(f"[bold red]Microphone error: {str(e)}")
                    return None
            
            status.update("[bold yellow]Recognizing...")
            
            # Try Whisper first
            try:
                speech_text = recognizer.recognize_whisper(audio, language="english", model="base.en")
                CONSOLE.log(f"[bold green]Whisper heard: {speech_text}")
                return speech_text
            except (UnknownValueError, RequestError) as e:
                CONSOLE.log(f"[bold yellow]Whisper failed: {str(e)}, trying Google...")
            
            # Try Google Speech Recognition
            try:
                speech_text = recognizer.recognize_google(audio)
                CONSOLE.log(f"[bold green]Google heard: {speech_text}")
                return speech_text
            except (UnknownValueError, RequestError) as e:
                CONSOLE.log(f"[bold yellow]Google failed: {str(e)}, trying Sphinx...")
            
            # Finally, try Sphinx
            try:
                speech_text = recognizer.recognize_sphinx(audio)
                CONSOLE.log(f"[bold green]Sphinx heard: {speech_text}")
                return speech_text
            except (UnknownValueError, RequestError) as e:
                CONSOLE.log(f"[bold red]All speech recognition attempts failed")
                return None
                
        except Exception as e:
            CONSOLE.log(f"[bold red]Unexpected error in listen(): {str(e)}")
            return None
