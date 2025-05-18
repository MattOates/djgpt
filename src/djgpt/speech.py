"""
Cross-platform speech module for DJGPT that works on all operating systems.
This module provides speech synthesis and recognition with fallbacks for different platforms.
"""

import platform
import time
from typing import Optional

from djgpt.utils import CONSOLE

# Import platform-specific text-to-speech modules
SYSTEM = platform.system().lower()

# Text-to-speech engine
TTS = None

# Initialize the appropriate TTS engine based on platform
if SYSTEM == "darwin":  # macOS
    try:
        from AppKit import NSSpeechSynthesizer

        TTS = NSSpeechSynthesizer.alloc().init()
        TTS_TYPE = "macos"
    except ImportError:
        CONSOLE.log("[bold yellow]Warning: AppKit not available, falling back to pyttsx3[/]")
        TTS_TYPE = "pyttsx3"
else:
    TTS_TYPE = "pyttsx3"

# Fall back to pyttsx3 for cross-platform support if needed
if TTS_TYPE == "pyttsx3":
    try:
        import pyttsx3

        TTS = pyttsx3.init()
        # Set a reasonable speaking rate
        TTS.setProperty("rate", 180)
    except Exception as e:
        CONSOLE.log(f"[bold red]Error initializing pyttsx3: {str(e)}[/]")
        CONSOLE.log(
            "[bold yellow]Text-to-speech functionality will be limited to text display only.[/]"
        )


def _wait_for_speech_to_finish():
    """Wait for text-to-speech to finish"""
    if TTS_TYPE == "macos" and TTS:
        while TTS.isSpeaking():
            time.sleep(0.1)
    elif TTS_TYPE == "pyttsx3" and TTS:
        # pyttsx3's runAndWait() is blocking already, so nothing to do here
        pass


def say(text: str, wait: bool = False):
    """
    Cross-platform text-to-speech function.
    Always prints the text and attempts to speak it if possible.
    """
    CONSOLE.print(text)

    if TTS is None:
        # No TTS engine available, just return after printing
        return

    if TTS_TYPE == "macos":
        # Don't interrupt previous startSpeaking as it cancels to the most recent
        _wait_for_speech_to_finish()
        TTS.startSpeakingString_(text)

        # Be a blocking call instead of OS level asynchronous
        if wait:
            _wait_for_speech_to_finish()
    elif TTS_TYPE == "pyttsx3":
        TTS.say(text)
        # runAndWait is blocking by nature
        TTS.runAndWait()


def listen() -> Optional[str]:
    """
    Get user input. Tries to use speech recognition if available,
    but falls back to keyboard input if speech recognition fails.
    """
    # First try to use speech recognition if it's available

    # Always fall back to keyboard input for now
    CONSOLE.print("[bold yellow]Microphone input disabled. Please type your request instead:[/]")
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


# If you want to extend this in the future to use speech recognition:
"""
def try_speech_recognition() -> Optional[str]:
    '''Attempt to use speech recognition based on available libraries.'''
    try:
        from speech_recognition import (
            Recognizer, Microphone, UnknownValueError, RequestError, WaitTimeoutError
        )
        
        recognizer = Recognizer()
        mic = Microphone()
        
        with CONSOLE.status("[bold green]Listening...") as status:
            with mic as source:
                try:
                    recognizer.adjust_for_ambient_noise(source)
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    
                    # Try different recognition engines
                    try:
                        text = recognizer.recognize_whisper(audio, language="english", model="base.en")
                        return text
                    except Exception:
                        pass
                    
                    try:
                        text = recognizer.recognize_google(audio)
                        return text
                    except Exception:
                        pass
                    
                    return None
                except Exception:
                    return None
    except ImportError:
        return None
    except Exception:
        return None
"""

if __name__ == "__main__":
    # Simple test
    say("Testing cross-platform speech synthesis.")
    user_input = listen()
    if user_input:
        say(f"You said: {user_input}")
