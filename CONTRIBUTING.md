# Contributing to Seraphina PDF Audiobook Studio

First off, thank you for considering contributing! 🎉

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues. When you create a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **System info**: Windows version, Python version
- **PDF sample** (if applicable)

### Suggesting Features

Feature requests are welcome! Please provide:

- **Clear use case**
- **Why current solution doesn't work**
- **How it benefits ADHD/neurodivergent users**

### Pull Requests

1. Fork the repo
2. Create a branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly
5. Commit with clear messages
6. Push and open a PR

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/seraphina-pdf-audiobook-studio.git

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If we add dev dependencies

# Run tests
python -m pytest tests/  # If we add tests
```

## Code Style

- Follow PEP 8
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic (especially text cleaning algorithms)

## Areas We Need Help

🚀 **High Priority:**
- OCR integration (Tesseract/pytesseract)
- Better PDF layout detection
- Audio post-processing (normalization)
- Windows installer (Inno Setup/NSIS)

💡 **Nice to Have:**
- GUI tests (PyAutoGUI)
- More SSML features
- Additional language support
- Dark mode theme

## Questions?

Open an issue with the `question` label!

Thank you! 🎙️