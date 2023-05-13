"""DJ GPT CLI

Module to deal with all the speech-to-text and text-to-speech functionality.
"""
import time
from functools import cache
from typing import Optional

from speech_recognition import Recognizer, Microphone, UnknownValueError, RequestError

# All gross stuff to get the Siri voice on macOS going... extremely brittle
from AppKit import NSSpeechSynthesizer

from utils import CONSOLE, retry

TTS = NSSpeechSynthesizer.alloc().init()


@cache
def get_sr():
    """Get the cached recognizer instance.

    Only need a single recognizer and audio device instance, also initialise for ambient noise.
    """
    recognizer = Recognizer()
    mic = Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)

    return recognizer, mic


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
    with CONSOLE.status("[bold green]Listening...") as status:
        recognizer, mic = get_sr()

        with mic as source:
            audio = recognizer.listen(source, phrase_time_limit=5)

        status.update("[bold yellow]Recognizing...")
        # received audio data, now we'll recognize it using Google Speech Recognition
        try:
            speech_text = recognizer.recognize_whisper(audio, language="english", model="base.en")
        except UnknownValueError:
            CONSOLE.log("[bold red]Whisper could not understand audio")
            speech_text = None
        except RequestError as e:
            CONSOLE.log("[bold red]Could not request results from Whisper")
            speech_text = None
        CONSOLE.log(f"[bold red]Heard: {speech_text}")
    return speech_text


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
    except RequestError as e:
        CONSOLE.log("[bold red]Could not request results from Whisper")
        return
    CONSOLE.log(f"[bold red]Heard: {speech_text}")
    if "stop" in speech_text.lower():
        if S_DEVICE_ID:
            get_spotify().pause_playback(S_DEVICE_ID)