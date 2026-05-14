# Contributing to GameAnnotator

Thank you for your interest in contributing!

## Setting Up for Development

1. Fork and clone the repository, then follow the [installation steps](README.md#setup).

2. Install test dependencies:
   ```bash
   pip install -r requirements.txt coverage
   ```

3. Run the test suite to confirm everything passes before making changes:
   ```bash
   python manage.py test annotator
   ```

## Making Changes

- **Bug fix** — open an issue first describing the bug, then submit a PR referencing it.
- **New feature** — open an issue to discuss the idea before writing code.
- Keep pull requests focused: one fix or feature per PR.

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/).
- All Python functions and classes must have Google-style docstrings.
- Do not commit `db.sqlite3`, media files, or `.env`.

## Tests

Every change must include tests. Run the full suite and check coverage before submitting:

```bash
coverage run manage.py test annotator
coverage report
```

The project targets ≥ 80% coverage. PRs that drop coverage significantly will be asked to add tests.

## Submitting a Pull Request

1. Create a branch: `git checkout -b fix/short-description`
2. Commit your changes with a clear message.
3. Push and open a pull request against `main`.
4. The CI pipeline (tests + docs build) must pass before merging.

## Reporting Issues

Use [GitHub Issues](../../issues). Include:
- Steps to reproduce
- Expected vs actual behaviour
- Python and Django versions (`python --version`, `python -m django --version`)
