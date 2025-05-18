# Continuous Integration

This document describes the continuous integration setup for the DJGPT project.

## GitHub Actions Workflow

The project uses GitHub Actions to run automated tests and checks on each push to `main` and on each pull request.

### Workflow Configuration

The workflow is defined in `.github/workflows/ci.yml` and:

- Runs on both Ubuntu and macOS environments
- Tests with Python 3.11
- Uses pixi for dependency management
- Formats code with ruff
- Runs linters with ruff
- Runs tests

### Environment Variables

The CI pipeline uses dummy environment variables for testing:

```
SPOTIPY_CLIENT_ID=dummy_spotify_id
SPOTIPY_CLIENT_SECRET=dummy_spotify_secret
OPENAI_API_KEY=dummy_openai_key
```

In the actual testing, these values are replaced with dummy strings that allow the tests to run without requiring actual API access.

## Setting Up Local Development Environment

To set up a local development environment that matches the CI environment:

1. Install pixi (if not already installed):
   ```bash
   curl -fsSL https://pixi.sh/install.sh | sh
   ```

2. Set up the environment:
   ```bash
   make setup
   ```

3. Set up cross-platform speech support:
   ```bash
   make setup-cross-platform
   ```

4. Run tests locally:
   ```bash
   make test
   ```

5. Run linters:
   ```bash
   make lint
   ```

6. Format code:
   ```bash
   make format
   ```

## Troubleshooting CI Issues

If you encounter issues with the CI pipeline:

1. Check if the tests pass locally
2. Make sure all dependencies are correctly specified in `pyproject.toml` and `environment.yml`
3. Review the workflow logs in GitHub Actions
4. For OS-specific issues, check the corresponding job in the matrix

## Adding New Tests

When adding new features, please add corresponding tests to ensure they're covered by the CI:

1. Add test files in the `tests/` directory
2. Follow the existing test patterns
3. Make sure tests don't require actual API credentials
4. Use mocks or fixtures for external dependencies

## CI Pipeline Improvements

Planned improvements for the CI pipeline:

1. Add code coverage reporting
2. Implement dependency caching to speed up builds
3. Add automatic deployment for tagged releases
