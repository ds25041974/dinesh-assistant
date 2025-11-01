# AI Agent Instructions

## Project Overview
This is a modern Python project that follows best practices for project structure, testing, and code quality. The project uses type hints, docstrings, and includes comprehensive test coverage.

## Project Structure
- `src/`: Contains the main source code
  - `main.py`: Entry point with example functions
- `tests/`: Contains test files
  - `test_main.py`: Tests for main module
- `pyproject.toml`: Project configuration and dependencies
- `.github/`: GitHub-specific files
- `README.md`: Project documentation

## Development Workflow
1. Always work within the virtual environment (`.venv`)
2. Install dependencies with `pip install -e ".[dev]"`
3. Run tests with `pytest tests/`
4. Format code before committing:
   ```bash
   black .
   isort .
   flake8 .
   mypy src tests
   ```

## Project Conventions
1. **Type Hints**: All functions must include type hints
2. **Docstrings**: Use Google-style docstrings for all public functions/classes
3. **Tests**: Write tests for all new functionality
4. **Code Style**: Follow Black formatting standards

## Integration Points
- Python 3.8+ required
- pytest for testing
- black, isort, flake8, and mypy for code quality
- Dependencies managed through pyproject.toml

## Common Tasks
1. **Adding Dependencies**:
   - Add to `dependencies` in pyproject.toml
   - Dev dependencies go in `optional-dependencies.dev`

2. **Running Tests**:
   - All tests: `pytest tests/`
   - With coverage: `pytest --cov=src tests/`

3. **Code Quality**:
   - Format: `black .`
   - Sort imports: `isort .`
   - Lint: `flake8 .`
   - Type check: `mypy src tests`