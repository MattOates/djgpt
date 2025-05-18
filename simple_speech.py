"""Simple speech module for DJGPT that only uses NSSpeechSynthesizer."""
import time
from typing import Optional

from speech_recognition import (
    Recognizer,
    Microphone,
    UnknownValueError,
    RequestError,
    WaitTimeoutError
)

from AppKit import NSSpeechSynthesizer
from utils import CONSOLE, retry

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

def get_sr():
    """Get a fresh recognizer and microphone instance."""
    recognizer = Recognizer()
    mic = Microphone()
    return recognizer, mic

@retry
def listen() -> Optional[str]:
    """Use multiple speech recognition engines with fallback."""
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
