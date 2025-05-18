# DJGPT Makefile
#
# This Makefile provides shortcuts for common operations in the DJGPT project.

.PHONY: setup run clean ui-dev ui-build ui-install lint test help setup-audio setup-openai setup-cross-platform

# Default target
help:
	@echo "DJGPT Makefile Help"
	@echo "------------------"
	@echo "Available commands:"
	@echo "  make setup       - Initialize the pixi environment"
	@echo "  make setup-audio - Fix audio dependencies for macOS"
	@echo "  make setup-openai - Fix OpenAI API compatibility issues"
	@echo "  make setup-cross-platform - Setup cross-platform speech support"
	@echo "  make run         - Run the DJGPT CLI application"
	@echo "  make clean       - Clean up temporary files and caches"
	@echo "  make ui-install  - Install UI dependencies"
	@echo "  make ui-dev      - Run the UI development server"
	@echo "  make ui-build    - Build the UI for production"
	@echo "  make lint        - Run linters on the code"
	@echo "  make test        - Run tests"

# Setup the environment
setup:
	@echo "Setting up the DJGPT environment..."
	pixi install
	@echo "Environment setup complete."

# Fix audio dependencies for macOS
setup-audio:
	@echo "Setting up audio dependencies for macOS..."
	brew install portaudio || true
	pixi install
	pixi run -- pip install --force-reinstall pyaudio pyttsx3 pocketsphinx
	@echo "Audio setup complete. You may now run 'make run'."

# Fix OpenAI API compatibility issues
setup-openai:
	@echo "Fixing OpenAI API compatibility issues..."
	pixi install
	pixi run -- pip install --force-reinstall openai==0.28
	@echo "OpenAI API compatibility fixed. You may now run 'make run'."

# Setup cross-platform speech support
setup-cross-platform:
	@echo "Setting up cross-platform speech support..."
	pixi install
	pixi run -- pip install --force-reinstall pyttsx3
	@echo "Cross-platform speech support installed. You may now run 'make run'."

# Run the application
run:
	@echo "Starting DJGPT..."
	pixi run start

# Clean up temporary files and caches
clean:
	@echo "Cleaning up..."
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf *.log
	rm -rf djgpt-ui/build
	rm -rf djgpt-ui/node_modules/.cache
	rm -rf .pixi
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf .mypy_cache
	@echo "Cleanup complete."

# UI development commands
ui-install:
	@echo "Installing UI dependencies..."
	cd djgpt-ui && npm install

ui-dev:
	@echo "Starting UI development server..."
	cd djgpt-ui && npm start

ui-build:
	@echo "Building UI for production..."
	cd djgpt-ui && npm run build

# Code quality
lint:
	@echo "Running linters..."
	pixi run -c "pylint --recursive=y ."

# Tests
test:
	@echo "Running tests..."
	pixi run test
