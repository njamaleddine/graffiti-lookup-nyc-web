# AI Coding Guidelines for Graffiti Lookup NYC Web

## General Principles
- Follow SOLID principles for maintainable, extensible, and testable code.
- Adhere to Python best practices and PEP20 (The Zen of Python).
- Write explicit, readable, and clean code.
- Prefer clarity over cleverness.

## Test Writing Rules
- All imports must be at the top of the file. Never import modules in the middle of tests.
- Use pytest.raises for exception testing, not side_effect or manual try/except unless necessary.
- Always separate function calls and assert statements with a blank line for readability.
- Mock external dependencies and side effects (e.g., file I/O, network calls).
- Ensure tests are robust, covering edge cases, malformed input, empty input, exceptions, and all logical branches.
- Use parameterization and fixtures for repeated patterns.
- Never duplicate code unnecessarily; use helper functions or fixtures.
- Use descriptive test names and docstrings.

## Code Style
- Follow PEP8 for formatting and linting.
- Use meaningful variable, function, and class names.
- Keep functions small and focused; prefer composition over inheritance.
- Handle errors explicitly and gracefully.
- Avoid magic values; use constants and configuration.
- Document public functions and classes with docstrings.
- Prefer explicit over implicit, simple over complex, and flat over nested.
- Avoid side effects in functions unless necessary.
- Use type hints where appropriate.

## Repository Practices
- Keep instructions and guidelines up to date in this file.
- Review and refactor code regularly for clarity and maintainability.
- Ensure all new code and tests follow these rules before merging.

---

_This file is intended for all AI and human contributors to ensure consistent, high-quality code and tests in the Graffiti Lookup NYC Web repository._
