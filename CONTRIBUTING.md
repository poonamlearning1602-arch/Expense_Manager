# Contributing to Expense Manager

Thank you for your interest in contributing to the Expense Manager project! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Virtual environment support

### Local Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Expense_Manager.git
   cd Expense_Manager
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov black flake8
   ```

5. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

## Development Workflow

### Creating a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### Code Style
- Follow PEP 8 standards
- Use `black` for code formatting
- Use `flake8` for linting
- Maintain a maximum line length of 88 characters

### Running Tests
```bash
pytest
pytest --cov=src  # With coverage
```

### Making Commits
- Write clear, descriptive commit messages
- Reference issues when applicable: `Fixes #123`
- Use the format: `type: description`
  - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Submitting Pull Requests
1. Push your branch to your fork
2. Create a Pull Request to the `main` branch
3. Provide a clear description of changes
4. Ensure all tests pass
5. Request review from maintainers

## Code Guidelines

### Python Code
- Use type hints where possible
- Write docstrings for all public functions
- Keep functions small and focused
- Use meaningful variable names

### Git Commits
- One feature per commit
- Keep commits atomic and logical
- Avoid large, monolithic commits

## Reporting Issues

When reporting bugs, please include:
- A clear description of the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- Python version and OS
- Any relevant error messages

## Questions?

Feel free to open an issue or contact the maintainers for questions about contributing.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
