# DJGPT Cross-Platform Enhancements

## Overview
This document provides an overview of the changes made to make DJGPT compatible with all platforms instead of being macOS-specific.

## Changes Made

### 1. Cross-Platform Speech Module
We created a new module `cross_platform_speech.py` that intelligently detects the operating system and uses the appropriate text-to-speech engine:
- For macOS: Uses NSSpeechSynthesizer
- For other platforms: Uses pyttsx3, a cross-platform TTS library

### 2. Keyboard Fallback
The speech module includes a robust keyboard input fallback method that works on all platforms, ensuring users can still interact with DJGPT even if speech recognition isn't available or working properly.

### 3. Makefile Updates
Added a new target `setup-cross-platform` to help users set up the necessary dependencies for cross-platform speech support.

### 4. CLI Updates
Modified `cli.py` to use our new cross-platform speech module instead of the macOS-specific implementation.

### 5. OpenAI API Compatibility
Fixed compatibility issues with the OpenAI API by:
- Downgrading to OpenAI v0.28 in pixi.toml
- Adding a setup-openai Makefile target to ensure the correct version is installed

## How to Use

### Setting Up
1. Clone the repository
2. Run `make setup` to initialize the environment
3. Run `make setup-openai` to install the correct OpenAI API version
4. Run `make setup-cross-platform` to install cross-platform speech support

### Running the Application
```bash
make run
```

### Using DJGPT
- The application will prompt you to type your music preferences
- GPT will recommend tracks based on your input
- You can select tracks to play on Spotify

## Platform Support
- macOS: Full support with native text-to-speech
- Windows: Supported via pyttsx3 for text-to-speech
- Linux: Supported via pyttsx3 for text-to-speech

## Future Improvements
- Implement cross-platform speech recognition (currently using keyboard input)
- Add configuration options for speech settings
- Optimize speech performance on different platforms
