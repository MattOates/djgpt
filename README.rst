===============================
DJGPT - Your AI Music Assistant
===============================

.. image:: https://raw.githubusercontent.com/MattOates/djgpt/main/screenshot.png

.. image:: https://github.com/MattOates/djgpt/workflows/DJGPT%20CI/badge.svg
    :target: https://github.com/MattOates/djgpt/actions
    :alt: CI Status

Introduction
------------

DJGPT is an interactive AI music assistant that uses OpenAI's GPT-4 to recommend music on Spotify based on natural language requests. Simply tell DJGPT what you're in the mood for, and it will suggest and play tracks that match your request, creating a personalized DJ experience right from your command line.

With DJGPT, you can:

* Request music using natural language (e.g., "Play me something that feels like a summer road trip")
* Get contextual music recommendations with explanations of why each track was selected
* Control playback through voice commands
* Discover new music tailored to your specific preferences or mood

How It Works
-----------

DJGPT combines several powerful technologies to create a seamless music discovery experience:

1. Uses OpenAI's GPT-4 to understand your music requests and generate contextually relevant recommendations
2. Integrates with Spotify to search for and play the recommended tracks
3. Provides a voice interface using speech recognition and text-to-speech for hands-free interaction
4. Offers a rich CLI experience with Typer and Rich libraries

Quick Start Guide
----------------

Prerequisites
~~~~~~~~~~~~

* Python 3.11+
* Spotify Premium account
* OpenAI API key
* macOS, Linux, or Windows (best experience on macOS)

Installation
~~~~~~~~~~~

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/MattOates/djgpt.git
      cd djgpt

2. Set up the environment using pixi (recommended) or conda:

   **Using pixi:**

   .. code-block:: bash

      pixi install
   
   **Using conda:**

   .. code-block:: bash

      conda env create --file=environment.yml -n djgpt
      conda activate djgpt

3. Create a ``.env`` file in the project root with your API credentials:

   .. code-block:: ini

      SPOTIPY_CLIENT_ID=your_spotify_client_id
      SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
      OPENAI_API_KEY=your_openai_api_key

   To obtain these credentials:
   
   * **Spotify**: Create an app in the `Spotify Developer Dashboard <https://developer.spotify.com/dashboard/>`_ and copy the Client ID and Client Secret
   * **OpenAI**: Generate an API key at `OpenAI API Keys <https://platform.openai.com/account/api-keys>`_

Running DJGPT
~~~~~~~~~~~~

Start the application:

.. code-block:: bash

   # If using pixi
   pixi run start
   
   # If using conda
   python -m djgpt

On first run, you'll be prompted to authorize the application with Spotify in your browser.

Usage
~~~~~

Once running, DJGPT will:

1. Ask what kind of music you want to listen to
2. Wait for your voice response (or you can type if speech recognition fails)
3. Process your request through GPT-4
4. Present a list of recommended tracks with explanations
5. Ask which track(s) you'd like to play
6. Play your selection on your active Spotify device

Voice Commands:
  * Say "all" to play all recommended tracks
  * Say "none" to skip and make a new request
  * Say "stop" to exit the application

Developer Guide
--------------

Project Structure
~~~~~~~~~~~~~~~

.. code-block:: text

   djgpt/
   ├── src/djgpt/           # Main package
   │   ├── __main__.py      # Entry point
   │   ├── cli.py           # CLI interface
   │   ├── prompt.py        # GPT prompt handling
   │   ├── speech.py        # Speech recognition and synthesis
   │   ├── spotify.py       # Spotify API integration
   │   └── utils.py         # Utility functions
   ├── tests/               # Unit tests
   ├── environment.yml      # Conda environment definition
   └── pyproject.toml       # Project metadata and task definitions

Key Components
~~~~~~~~~~~~~

* **CLI Module** (`cli.py`): Handles the command-line interface and user interaction flow
* **Prompt Module** (`prompt.py`): Manages OpenAI GPT interactions with custom prompt engineering
* **Speech Module** (`speech.py`): Provides cross-platform speech recognition and text-to-speech
* **Spotify Module** (`spotify.py`): Handles Spotify API integration for search and playback

Development Tasks
~~~~~~~~~~~~~~~

The project uses pixi for task management and includes a Makefile for common operations:

.. code-block:: bash

   # Run the application
   pixi run start
   # or
   make run
   
   # Run tests
   pixi run test
   # or
   make test
   
   # Check test coverage
   pixi run coverage
   
   # Run linters
   make lint
   
   # Setup environment
   make setup

Continuous Integration
~~~~~~~~~~~~~~~~~~~~

This project uses GitHub Actions for continuous integration. The CI pipeline:

- Runs on both Ubuntu and macOS environments
- Sets up Python 3.11 and pixi
- Installs system dependencies
- Configures the cross-platform speech support
- Runs linters and tests

You can see the build status in the badge at the top of this README.

Platform Compatibility
~~~~~~~~~~~~~~~~~~~~

DJGPT is designed to work across platforms, with fallbacks for different text-to-speech engines:

* **macOS**: Uses the native NSSpeechSynthesizer for optimal performance
* **Windows/Linux**: Falls back to pyttsx3 for text-to-speech functionality

Adding New Features
~~~~~~~~~~~~~~~~~

1. Fork the repository and create a feature branch
2. Implement your changes with appropriate tests
3. Run the test suite to ensure compatibility
4. Submit a pull request with a description of your changes

Technologies
-----------

DJGPT integrates several powerful technologies:

* **OpenAI GPT-4**: Powers the music recommendation engine with sophisticated prompt engineering
* **Spotipy**: Python client for the Spotify Web API (`documentation <https://spotipy.readthedocs.io/>`_)
* **OpenAI Whisper**: Provides speech recognition via SpeechRecognition
* **AppKit/pyttsx3**: Cross-platform text-to-speech capabilities
* **Typer/Rich**: Creates an elegant and interactive command-line interface

License
-------

This project is licensed under the terms of the included LICENSE file.

Acknowledgments
--------------

DJGPT was initially created as a hack-day project to explore the capabilities of GPT-4 in music recommendation contexts. Special thanks to all the open-source projects that made this possible.
