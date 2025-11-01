# Advanced Python Project

A modern Python project demonstrating internationalization, template-based text generation, and robust configuration management. Built with comprehensive test coverage and following best development practices.

## Features

- **Multi-language Support**: 
  - Support for English, Spanish, French, German, and Japanese
  - Language-specific translations for messages and errors
  - Easy addition of new languages

- **Template System**:
  - Multiple greeting templates (formal, casual, funny, business)
  - Template categorization and tagging
  - Template metadata with descriptions
  - Search templates by category or tags

- **Configuration Management**:
  - JSON-based configuration files
  - Environment-specific settings
  - Validation with proper error handling
  - Debug and logging configuration
  - Timezone and rate limiting settings

- **CLI Interface**:
  - Rich command-line interface with subcommands
  - Support for sync and async operations
  - Multiple output template styles
  - Debug mode with enhanced logging
  - Configuration file management

## Project Structure

```
.
├── src/
│   ├── main.py              # CLI and core functionality
│   └── config/
│       ├── i18n.py          # Internationalization
│       ├── settings.py      # Configuration handling
│       ├── templates.py     # Template management
│       └── validation.py    # Config validation
├── tests/                   # Test files
├── .github/                 # GitHub workflows
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Usage

### Basic Greeting

```bash
# English greeting
python -m src.main greet "World"

# Spanish greeting
python -m src.main greet "World" --language es

# Formal style in French
python -m src.main greet "World" --language fr --style formal

# Custom message in Japanese
python -m src.main greet "World" --language ja --message "おはようございます"
```

### Template Management

```bash
# List all templates
python -m src.main templates

# List formal templates
python -m src.main templates --category formal

# Search by tags
python -m src.main templates --tags "business,polite"
```

### Configuration

```bash
# View current config
python -m src.main config view

# Validate config file
python -m src.main config validate --file config.json

# Save current settings
python -m src.main greet "World" --debug --style formal --save-config config.json
```

## Development

This project uses modern Python development tools for quality and consistency:

- **Type Hints**: All code is type-annotated and checked with mypy
- **Documentation**: Google-style docstrings
- **Testing**: pytest with async support and coverage reporting
- **Code Quality**: 
  - black for formatting
  - isort for import sorting
  - flake8 for linting
  - mypy for type checking
  - pre-commit hooks for consistent style

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=xml
```

### Code Quality

```bash
# Format code
black .
isort .

# Run linting
flake8 .
mypy src tests
```

## CI/CD

The project uses GitHub Actions for continuous integration with:

- Multi-Python version testing (3.8-3.11)
- Code formatting verification
- Type checking
- Linting
- Test coverage reporting
- Automatic coverage upload to Codecov

The workflow runs on:
- Push to main branch
- Pull request to main branch

## Project Conventions

1. Type hints on all functions and classes
2. Google-style docstrings for public APIs
3. Test coverage for new functionality
4. Black code formatting
5. Pre-commit hooks for code quality

## Requirements

- Python 3.8 or higher
- Dependencies listed in pyproject.toml
- Development tools in optional-dependencies.dev