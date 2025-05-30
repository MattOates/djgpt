#!/usr/bin/env python3
"""DJ GPT CLI

Handle setting up a CLI and running the interactive DJ session
"""

import time
from os import getenv
from sys import exit
from typing import List

import openai
import typer
from dotenv import find_dotenv, load_dotenv
from typer import Option
from typing_extensions import Annotated

from djgpt import spotify
from djgpt.prompt import IntGPTPromptSystem, SelfTestJSONGPTPromptSystem

# Use the cross-platform speech module that works on all operating systems
from djgpt.speech import listen, say
from djgpt.spotify import Track, play_on_spotify, wait_for_spotify
from djgpt.utils import CONSOLE

load_dotenv(find_dotenv(usecwd=True))

app = typer.Typer()


class DJGPTPromptSystem(SelfTestJSONGPTPromptSystem):
    prompt_part = """You are DJGPT4 a master of music knowledge and recommendation engine, return all responses as an 
    array of {num_tracks} music track recommendation objects with fields: 'artist', 'trackname', 'genre', 'reason' and 
    'quality'. Where reason should be a concise reason why you think this track is relevant. Where quality is how well 
    you think the track fits the user request ranging between 0 and 1 in increments of 0.1."""

    def ask(self, user_prompt: str) -> List[Track]:
        """
        We are getting JSON via SelfTestJSONGPTPromptSystem, but we really want Spotify Track objects.
        """
        djgpt_json = super().ask(user_prompt)

        try:
            tracks = [Track(**track) for track in djgpt_json]
        except Exception:
            CONSOLE.log(
                f"GPT failed to find any tracks, or we failed to understand GPT. {djgpt_json}"
            )
            tracks = []

        return tracks


@app.command()
def djgpt(
    spotify_client_id: Annotated[str, Option(prompt=True, envvar="SPOTIPY_CLIENT_ID")] = getenv(
        "SPOTIPY_CLIENT_ID"
    ),
    spotify_client_secret: Annotated[
        str, Option(prompt=True, envvar="SPOTIPY_CLIENT_SECRET")
    ] = getenv("SPOTIPY_CLIENT_SECRET"),
    openai_api_key: Annotated[str, Option(prompt=True, envvar="OPENAI_API_KEY")] = getenv(
        "OPENAI_API_KEY"
    ),
    num_tracks: int = 5,
):
    spotify.S_CLIENT_ID = spotify_client_id
    spotify.S_SECRET_ID = spotify_client_secret
    openai.api_key = openai_api_key

    djgpt = DJGPTPromptSystem(num_tracks=num_tracks)
    intgpt = IntGPTPromptSystem()

    while wait_for_spotify():
        try:
            say("What kind of thing do you want to listen to?")
            speech_text = listen()

            # Check if speech_text is None (microphone/recognition failed)
            if speech_text is None:
                say("Sorry, I couldn't hear you. Please try again.", wait=True)
                continue

            if "stop" in speech_text.lower():
                say("Goodbye!", wait=True)
                exit()
            say("Asking DJ GPT about: " + speech_text)

            recommended_tracks = djgpt.ask(speech_text)
            if len(recommended_tracks) == 0:
                continue

            say("GPT recommended the following tracks found in Spotify:")
            for idx, track in enumerate(recommended_tracks):
                if track.spotify is None:
                    # If we can't find something in Spotify it's probably GPT4 halucinating its tits off so just ignore
                    continue
                say(f"{idx + 1}. {track.trackname} by {track.artist}")
                CONSOLE.print(f"\t{track.genre}; {track.reason}")
                CONSOLE.print(f"\t{track.spotify.url}")

            say("Which would you like to play?")
            selected = listen()
            if "all" in selected.lower():
                play_on_spotify([t for t in recommended_tracks if t.spotify])
            elif "none" in selected.lower():
                continue
            else:
                selected = intgpt.ask(selected)
                if selected is None:
                    CONSOLE.log("[bold red] Failed to understand choice. Lets go again.")
                    continue
                selected_track = recommended_tracks[selected - 1]
                say(f"{selected_track.trackname} was recommended because: {selected_track.reason}")
                # Use this if the OAuth scope doesn't work webbrowser.open(selected_track["url"])
                play_on_spotify([selected_track])

            time.sleep(2)

        except KeyboardInterrupt as e:
            CONSOLE.log("The Program is terminated manually!")
            # Might need some clean up here given all the crazed binaries we are using in the background
            raise SystemExit from e


def main():
    app()


if __name__ == "__main__":
    main()
