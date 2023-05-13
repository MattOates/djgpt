===============================
djgpt
===============================

Introduction
------------
DJGPT lets you play some beats on Spotify recommended from the GPT4 LLM masquerading as a DJ.

One of my favourite hobbies is just sitting listening to new music, this lets you run an
interactive session so you dont have to fiddle around and search. Or think too coherently
about what you want! GPT will happily recommend for "what's on Superman's saving the world
playlist" as it will "play 90s tracks from the Epic music genre".

This all started with me wondering how much GPT really knows about music and I was surprised
at just how good it was given it's essentially only ever read about various artists and tracks.

Be as long winded as you like with the user prompts and I think you will be really surprised
with what this system can recommend to you. It's more like having a human friend recommend than
say Alexa or Google type assistants. Give your mood or surrounding or soft inspiration and GPT
comes back with some really great recommends. It tends to default to very popular music, but
just ask for something new or more obscure and it will oblige.

I have noticed the more weird the request the more likely there are to be halucinations,
or simply tracks not found in Spotify. Mostly this should just be a drop off in the number of
tracks found in Spotify. So you will see some weird numbering coming back.

At the moment we rely on some quirks of macOS for text-to-speech as pyttsx3 segfaulted
on Mac (which I had to work around with NSSpeechSynthesizer)...

Currently there are no tests as this was a quick clean up of a hack-day single py file project.
But you can take a look at prompt.py for how I'm planning on using GPT to test GPT prompts.

Environment
-----------

This script requires that a lot of horrible things are installed some demanding Conda.
You can use miniforge/miniconda with the environment.yml doing something like:
`conda env create --file=environment.yml -n djgpt`.

To make things easy and save on being prompted or needing command line argumens I would drop
a **.env** file into this module directory with the following::

    SPOTIPY_CLIENT_ID=
    SPOTIPY_CLIENT_SECRET=
    OPENAI_API_KEY=

To grab an OpenAI key and pay a few pennies for this service a day, go to https://platform.openai.com/account/api-keys
You will want to setup a little Spotify app against your account, and this will require Premium. https://developer.spotify.com/documentation/web-api/concepts/apps

Standing on Giants
------------------

This was really a quick hack to cobble other pieces of cool software together. The only thing in
here other than the main idea that's perhaps creatively of interest is how I manage prompts and
OpenAI API interactions. I will probably clean up prompt.py and split it off as its own thing.

The main pieces we've integrated together are:

* OpenAI GPT4 - star of the show with some prompt engineering for returning music recommendations
* Spotipy - for interacting with Spotify https://spotipy.readthedocs.io/en/2.22.1/
* OpenAI Whisper - care of SpeechRecognition for speech to text https://pypi.org/project/SpeechRecognition/
* AppKit - for the macOS system text to speech voice aka Siri (or whichever voice you have setup)
* Typer/Rich - special mention for making pretty and interactive CLIs easily