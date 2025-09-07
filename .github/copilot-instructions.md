# Mode Python SDK - Copilot Instructions

## Project Overview

The Mode Python SDK is a client library for interacting with the Mode Trading API. It's a small, focused project with 8 Python files that provides:
- Market data fetching (historical data, quotes)
- Asset reference data retrieval
- Optional pandas/numpy integration for backtesting workflows
- Type-safe API interactions using Pydantic models

**Key Stats:** 8 Python files, ~500 lines of code, Python 3.12+ required, uses modern tooling (uv, pydantic, ruff)

## Build & Development Workflow

### Prerequisites
- Python 3.12+ (CI uses 3.13)
- `uv` package manager (install with `pip install uv`)

### Setup Commands (Always run in this exact order)
```bash
# 1. Create virtual environment (required)
uv venv

# 2. Activate virtual environment (required before any pip commands)
source .venv/bin/activate

# 3. Install dependencies - choose ONE of these:
uv pip install -e ".[dev]"           # For development (includes pytest, black, ruff, mypy)
uv pip install -e ".[dev,backtest]"  # For development + pandas/numpy extras
uv pip install -e ".[backtest]"      # For runtime + pandas/numpy extras only
```

### Validation Commands (run after any code changes)
```bash
# Run in this order - all commands must pass before committing:
pytest                    # Tests (16 tests, ~0.3 seconds, must all pass)
black --check .          # Code formatting check (must pass)
ruff check .             # Linting (must pass, configured in pyproject.toml)
mypy src                 # Type checking (must pass, checks src/ directory only)
```

### Common Issues & Solutions
- **Always activate venv first**: `source .venv/bin/activate` before any uv pip commands
- **Clean install**: If dependencies fail, delete `.venv/` and start over with `uv venv`
- **Test failures**: All 16 tests should pass - investigate any failures before proceeding
- **Import errors**: Ensure package is installed in editable mode with `-e` flag

## Project Architecture

### Directory Structure
```
├── src/mode_sdk/          # Main package code
│   ├── __init__.py       # Package initialization (empty)
│   ├── client.py         # ModeAPIClient main entry point
│   ├── resources.py      # AssetsResource, MarketDataResource API wrappers  
│   ├── models.py         # Pydantic data models (Asset, Quote, HistoricalData, etc.)
│   └── exceptions.py     # Custom exceptions (ModeAPIError, AuthenticationError, APIError)
├── tests/                # Test suite
│   ├── test_client.py    # Client authentication & initialization tests
│   └── test_models.py    # Model validation & serialization tests
├── pyproject.toml        # Project config, dependencies, tool settings
└── .github/workflows/    # CI/CD pipelines
    ├── tests.yml         # Runs pytest with dev and dev,backtest extras
    └── quality.yml       # Runs black, ruff, mypy validation
```

### Key Components
- **ModeAPIClient**: Main entry point in `client.py`, handles authentication and provides `market_data` and `assets` resources
- **Resources**: `MarketDataResource` (quotes, historical data), `AssetsResource` (reference data)
- **Models**: Pydantic-based with validation - `Asset`, `Quote`, `HistoricalDataResponse`, helper methods like `to_dataframe()`
- **Authentication**: JWT-based via email/password, supports env vars (`MODE_API_EMAIL`, `MODE_API_PASSWORD`, `MODE_API_BASE_URL`)

## CI/CD & Validation Pipeline

### GitHub Workflows
1. **tests.yml** (triggered on push to main, PRs):
   - Installs with both `[dev]` and `[dev,backtest]` extras
   - Runs `uv run pytest` 
   - Python 3.13 on ubuntu-latest

2. **quality.yml** (triggered on push to main, PRs):
   - Runs `uv run black --check .`
   - Runs `uv run ruff check .`  
   - Runs `uv run mypy src`
   - Python 3.13 on ubuntu-latest

### Validation Checklist
Before any code changes, ensure:
- [ ] Virtual environment activated
- [ ] All tests pass (`pytest`)
- [ ] Code is formatted (`black --check .`)
- [ ] No linting errors (`ruff check .`)
- [ ] No type errors (`mypy src`)
- [ ] If adding dependencies, test both `[dev]` and `[dev,backtest]` install combinations

## Configuration Files

### pyproject.toml Key Settings
- **Tool config**: `[tool.ruff]` line-length=120, target py313, ignores E501
- **Dependencies**: requests==2.32.5, pydantic==2.11.7, python-dotenv, types-requests
- **Dev extras**: pytest, pytest-mock, requests-mock, black, ruff, mypy
- **Backtest extras**: pandas>=2.3.2, numpy>=2.3.2

### Environment Variables
```bash
MODE_API_BASE_URL="http://localhost:8080"    # Optional, defaults to localhost:8080
MODE_API_EMAIL="your_email@example.com"      # Required for authentication
MODE_API_PASSWORD="your_secret_password"     # Required for authentication
```

## Common Modification Patterns

### Adding New API Endpoints
1. Add method to appropriate resource class in `resources.py`
2. Add corresponding Pydantic model in `models.py` if needed
3. Add tests in `tests/test_client.py` or `tests/test_models.py`
4. Run full validation suite

### Adding New Dependencies
1. Add to `dependencies` or `optional-dependencies` in `pyproject.toml`
2. Test installation with `uv pip install -e ".[dev,backtest]"`
3. Update imports and usage
4. Verify CI workflows still pass

### Modifying Data Models
1. Update Pydantic models in `models.py`
2. Ensure validation logic is correct
3. Update corresponding tests in `tests/test_models.py`
4. Test serialization/deserialization with real API responses

## Quick Reference

**Start development**: `uv venv && source .venv/bin/activate && uv pip install -e ".[dev]"`
**Run tests**: `pytest`
**Format code**: `black .`
**Check lint**: `ruff check .`
**Type check**: `mypy src`
**Install with extras**: `uv pip install -e ".[dev,backtest]"`

**Trust these instructions** - they are verified and current. Only search/explore if you encounter specific errors not covered here.