"""DJ GPT CLI

Module to deal with all the speech-to-text and text-to-speech functionality.
"""
import time
from typing import Optional

from speech_recognition import Recognizer, Microphone, UnknownValueError, RequestError

# All gross stuff to get the Siri voice on macOS going... extremely brittle
from AppKit import NSSpeechSynthesizer

from utils import CONSOLE, retry

TTS = NSSpeechSynthesizer.alloc().init()


def _wait_for_siri_to_shutup():
    """She does love to drone on, we don't want Whisper listening to her"""
    while TTS.isSpeaking():  # loop until it finish speaking
        time.sleep(1)  # TODO: see if this can be reduced


def say(text: str, wait: bool = False):
    """Super hacky NSSpeechSynthesizer "blocking" call... for text-to-speech
    """
    # Don't interrupt previous startSpeaking as it cancels to the most recent
    _wait_for_siri_to_shutup()
    CONSOLE.print(text)
    TTS.startSpeakingString_(text)

    # Be a blocking call instead of OS level asynchronous
    if wait:
        _wait_for_siri_to_shutup()


@retry
def listen() -> Optional[str]:
    """Use OpenAI whisper model installed locally to do speech-to-text

    This needs pyaudio installed to deal with the mic input
    First time you ever use this it will download the medium.en model to ~/.cache/whisper its a bit chonky
    """
    # Wait for Siri's voice otherwise we listen to ourselves!
    _wait_for_siri_to_shutup()
    
    try:
        with CONSOLE.status("[bold green]Listening...") as status:
            # Get fresh instances each time
            recognizer = Recognizer()
            
            try:
                # Try to initialize the microphone
                mic = Microphone()
            except Exception as e:
                CONSOLE.log(f"[bold red]Microphone error: {str(e)}")
                CONSOLE.log("[bold yellow]Try running 'make setup-audio' to fix audio dependencies")
                return None
                
            try:
                with mic as source:
                    # Adjust for ambient noise here, within the context manager
                    try:
                        recognizer.adjust_for_ambient_noise(source)
                    except Exception as e:
                        CONSOLE.log(f"[bold red]Ambient noise adjustment error: {str(e)}")
                    
                    # Listen for audio
                    audio = recognizer.listen(source, phrase_time_limit=5)
            except Exception as e:
                CONSOLE.log(f"[bold red]Listening error: {str(e)}")
                return None

            status.update("[bold yellow]Recognizing...")
            # Recognize the audio
            try:
                speech_text = recognizer.recognize_whisper(audio, language="english", model="base.en")
                CONSOLE.log(f"[bold green]Heard: {speech_text}")
                return speech_text
            except UnknownValueError:
                CONSOLE.log("[bold red]Whisper could not understand audio")
                return None
            except RequestError:
                CONSOLE.log("[bold red]Could not request results from Whisper")
                return None
    except Exception as e:
        CONSOLE.log(f"[bold red]Unexpected error in listen(): {str(e)}")
        return None


def listen_command(recognizer, audio):
    """Dead code. 2023-05-04

    Callback whilst waiting and not actively listening but background idle.
    Hangover from background listening, keeping for later
    """

    # recognizer, mic = get_sr()
    # stop_listening = recognizer.listen_in_background(mic, listen_command)

    CONSOLE.log("[bold yellow]Recognizing...")
    try:
        speech_text = recognizer.recognize_whisper(audio, language="english", model="base.en")
    except UnknownValueError:
        CONSOLE.log("[bold red]Whisper could not understand audio")
        return
    except RequestError:
        CONSOLE.log("[bold red]Could not request results from Whisper")
        return
    CONSOLE.log(f"[bold red]Heard: {speech_text}")
    if "stop" in speech_text.lower():
        if S_DEVICE_ID:
            get_spotify().pause_playback(S_DEVICE_ID)
