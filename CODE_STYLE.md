
# Project Coding Standards and Principles

This project contains both Python (backend/data pipeline) and JavaScript/Vue (frontend) code. All contributors and AI tools must follow the standards below for the appropriate part of the codebase.

---

## Python (graffiti_data_pipeline/)

### 1. PEP8 — Style Guide for Python Code
- Use consistent indentation (4 spaces per level)
- Limit lines to 79 characters
- Use meaningful, descriptive variable names — never single-letter variables
- Add whitespace for readability
- Organize imports alphabetically within groups (standard, third-party, local)

### 2. PEP20 — The Zen of Python
- Explicit is better than implicit
- Simple is better than complex
- Readability counts
- Errors should never pass silently.
- (See `import this` for the full list)

### 3. SOLID Principles (for OOP)
- **S**ingle Responsibility: Each class/function does one thing
- **O**pen/Closed: Open for extension, closed for modification
- **L**iskov Substitution: Subtypes are substitutable for base types
- **I**nterface Segregation: Prefer small, specific interfaces
- **D**ependency Inversion: Depend on abstractions, not concretions. Use constructor injection to accept collaborators (callables, services) rather than hard-coding dependencies inside a class.

### 4. Functional Programming Best Practices
- Use pure functions where possible
- Avoid side effects; when mutation is necessary, document it clearly with a warning in the docstring
- Never bury a side effect inside an `if` condition — separate the action from the decision
- Prefer immutability
- Use comprehensions and higher-order functions (map, filter, etc.)

### 5. Clean Code Practices
- Write self-documenting code
- Use docstrings for modules, classes, and functions where they add value. For small, obvious, or internal files/functions, docstrings may be omitted if the code is clear and well-named.
- Use type hints for public APIs, complex functions, and where types aren't obvious. For simple or internal code, type hints can be omitted if they reduce readability.
- Use NamedTuples or dataclasses when structured data would benefit from named fields; plain dicts and tuples are fine for simple, local, or transient data
- Pre-compile regular expressions at module level when they are used repeatedly
- Provide `__repr__` on classes to aid debugging
- Write tests for all new code
- Refactor and simplify when possible
- Avoid code duplication

### 6. Naming Conventions
- Name classmethods that construct instances after their purpose, not their implementation (e.g. `from_config` not `nominatim`)
- Use descriptive names that reveal intent — method names like `_resolve` over vague names like `_fetch`
- Never use single-letter variable names
- Prefer f-strings for all string formatting, including logging calls

### 7. Testing Best Practices
- When practical, design classes to accept collaborators so tests can supply simple fakes — but `patch` and `Mock` are perfectly fine when injection would over-complicate the design
- Prefer `patch` over `Mock` when test doubles are needed — patch at the boundary, not deep inside implementation
- Use `pytest.fail("should not call")` as a callable to assert a code path is never reached
- Keep tests focused: one behavior per test method
- Group related tests in classes (`TestGeocoder`, `TestGeocodeServiceRequests`)

### 8. General Guidelines
- All code must be maintainable and testable
- Follow idiomatic Python
- Prioritize clarity over cleverness
- Use your judgment: practicality beats purity. Consistency and clarity are more important than strict adherence to every rule.
- Review and update this document as the project evolves

---

## JavaScript & Vue (src/)

### 1. JavaScript Best Practices
- Use ES6+ features (let/const, arrow functions, destructuring, etc.)
- Prefer const for variables that are not reassigned
- Use strict equality (=== and !==)
- Avoid global variables
- Use template literals for string interpolation
- Prefer array methods (map, filter, reduce) over loops when appropriate
- Handle errors with try/catch or .catch for promises
- Modularize code (use imports/exports)
- Use meaningful, descriptive names for variables and functions

### 2. Vue Best Practices
- Use the Composition API or script setup for new components
- Organize components in a logical folder structure
- Use single-file components (.vue) with <template>, <script>, and <style> sections
- Keep components small and focused (single responsibility)
- Use props and emits for parent-child communication
- Use v-model for two-way binding
- Use computed properties and watchers appropriately
- Avoid mutating props directly
- Use scoped styles or CSS modules to avoid style leakage
- Register global components sparingly; prefer local registration

### 3. Clean Code Practices (JavaScript & Vue)
- Write self-documenting code and use comments where necessary
- Use JSDoc or TypeScript for type annotations when possible
- Write unit tests for all components and functions
- Refactor and simplify code regularly
- Avoid code duplication
- Keep functions and components small and focused
- Remove unused code and dependencies

### 4. Community Standards
- Follow the official Vue Style Guide: https://vuejs.org/style-guide/
- Follow Airbnb JavaScript Style Guide or StandardJS for general JS: https://github.com/airbnb/javascript
- Use Prettier and ESLint for code formatting and linting
- Document any deviations from these standards in this file

---


## Astro (src/)

### 1. Astro Best Practices
- Use .astro files for page and layout components; prefer .js/.ts for logic-heavy utilities.
- Keep components small, focused, and reusable.
- Use Astro’s built-in components and directives (e.g., set:html, set:visible) for clarity and performance.
- Prefer partial hydration (islands architecture) for interactive components; keep most content static when possible.
- Use slots for flexible layouts and content injection.
- Organize components and pages in a logical folder structure.
- Use environment variables and Astro.config for configuration, not hardcoded values.
- Avoid direct DOM manipulation; use framework components (Vue, React, Svelte, etc.) for interactivity.
- Use Markdown/MDX for content when appropriate.
- Follow official Astro Style Guide: https://docs.astro.build/en/guides/project-structure/

---

For questions or clarifications, please contact the project maintainers.
