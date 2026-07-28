# Contributing to LeetCode Profile Generator

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/gufran21/leetcode-profile-generator.git
cd leetcode-profile-generator

# Install in development mode
pip install -e .

# Install dev dependencies
pip install pytest pytest-asyncio ruff mypy
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_cards.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

## Linting & Type Checking

```bash
ruff check src/ tests/
mypy src/ --ignore-missing-imports
```

## Adding a New Theme

1. Open `src/render/themes.py`
2. Create a new `Theme` instance following the existing patterns
3. Add it to the `_THEMES` registry dict
4. Add tests in `tests/test_themes.py`
5. Update the README theme gallery

### Theme Color Guide

| Field | Purpose |
|-------|---------|
| `bg_color` | Card background |
| `bg_gradient` | Optional gradient (tuple of 2 hex colors) |
| `title_color` | Card titles and headers |
| `text_color` | Primary text |
| `text_secondary` | Muted/secondary text |
| `easy_color` | Easy difficulty (green family) |
| `medium_color` | Medium difficulty (yellow/amber family) |
| `hard_color` | Hard difficulty (red family) |
| `accent_color` | Charts, highlights, interactive elements |
| `heatmap_empty` - `heatmap_l4` | 5 heatmap intensity levels |

## Adding a New Card

1. Create `src/cards/your_card.py` with a `generate_your_card(data, theme) -> str` function
2. Register it in `src/cards/__init__.py`
3. Add a CLI flag in `src/cli.py`
4. Add an input in `action.yml`
5. Add tests in `tests/test_cards.py`
6. Update the README

## Code Style

- Use type hints everywhere
- Follow existing patterns for consistency
- Keep functions focused and well-documented
- All public functions need docstrings
- Use `ruff` for formatting

## Pull Request Guidelines

1. Create a feature branch from `main`
2. Add/update tests for your changes
3. Ensure all tests pass
4. Update documentation if needed
5. Write a clear PR description

## Reporting Issues

- Use the issue templates in `.github/ISSUE_TEMPLATE/`
- Include your Python version and OS
- Include the full error message/traceback
- If it's a visual bug, attach the generated SVG
