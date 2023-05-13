"""DJ GPT CLI

Module to deal with all the Spotify API interactions and functionality
"""
import time
from dataclasses import dataclass
from functools import cache
from typing import NamedTuple, Dict, Optional, List

import spotipy
from spotipy import SpotifyException

from utils import debug, retry, CONSOLE

# Spotify globals
S_DEVICE_ID = S_CLIENT_ID = S_SECRET_ID = None


class Spotify(NamedTuple):
    """Store spotify API data.

    Tuple of what we care about the URI/URLs and stash the rest just incase
    """
    url: str
    uri: str
    stash: Dict


@dataclass
class Track:
    """Store track data.

    Simple data class to deal with tracks from GPT and spotify queries.
    """
    artist: str
    trackname: str
    genre: Optional[str] = None
    reason: Optional[str] = None
    quality: Optional[float] = None
    error: Optional[str] = None

    @property
    def spotify(self) -> Optional[Spotify]:
        return search_spotify(self.artist, self.trackname)


@cache
def get_spotify():
    """Get the cached spotify API caller.

    On first ever use you will be asked to authorize the app use against your Spotify account (say yes in the browser)
    you wont get asked ever again.
    """
    # TODO: work out if we can avoid these globals in a nice way with Typer
    global S_CLIENT_ID, S_SECRET_ID
    oauth = spotipy.SpotifyOAuth(
        client_id=S_CLIENT_ID,
        client_secret=S_SECRET_ID,
        redirect_uri="https://localhost:8888/callback",
        scope="user-read-playback-state user-modify-playback-state",
        show_dialog=True,
    )
    # Create/get cached token for a session with the API
    token = oauth.get_access_token(as_dict=False)

    return spotipy.Spotify(auth=token)


def wait_for_spotify():
    spotify = get_spotify()
    track_name = artist_name = None
    with CONSOLE.status("[bold green]Waiting for Spotify...") as status:
        while(True):
            playback = spotify.current_playback()
            if playback is None:
                break
            is_playing = playback["is_playing"]
            if is_playing:
                track_name = playback["item"]["name"]
                artist_name = playback["item"]["artists"][0]["name"]
            else:
                break
            status.update(f"[bold green]Waiting for Spotify to finish, listening to {track_name} by {artist_name}")
            time.sleep(30)
        CONSOLE.log("[bold red]Ready to DJ!")
    return Track(trackname=track_name, artist=artist_name)


def search_spotify(artist: str, trackname: str) -> Optional[Spotify]:
    """Search Spotify using an artist and track name, get back an exteranl URL"""
    try:
        search_results = get_spotify().search(
            f"artist:{artist} track:{trackname}",
            limit=1,
            offset=0,
            type='track'
        )
        if not search_results:
            return None

        track = search_results['tracks']['items'][0]
        url = track['external_urls']['spotify']
        uri = track['uri']

        return Spotify(url, uri, search_results)

    except Exception as e:
        debug(e)
        return None


@retry(
    exception_class=SpotifyException,
    prompt="Try again with Spotify? (If the error is 'No active device found' just press play/pause in Spotify)",
    none_is_fail=False
)
def play_on_spotify(tracks: List[Track]):
    get_spotify().start_playback(uris=[t.spotify.uri for t in tracks if t.spotify])