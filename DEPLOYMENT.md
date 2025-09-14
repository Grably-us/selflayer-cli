# SelfLayer Deployment Guide

## Overview

This guide covers the complete deployment process for SelfLayer, including PyPI setup, version management, and automated release workflow.

## Prerequisites

### 1. PyPI Account Setup

1. **Create PyPI Account**: Go to [https://pypi.org/account/register/](https://pypi.org/account/register/)
2. **Verify Email**: Check your email and verify your account
3. **Enable 2FA**: Highly recommended for security
4. **Create API Token**: Go to [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
   - Select "Entire account (all projects)"
   - Name it something like "SelfLayer-deployment"
   - Copy the token (starts with `pypi-`)

### 2. Configure PyPI Credentials

Create a `.pypirc` file in your home directory:

```bash
# Create .pypirc file
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-YOUR_API_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_API_TOKEN_HERE
EOF

# Secure the file
chmod 600 ~/.pypirc
```

**Note**: Replace `pypi-YOUR_API_TOKEN_HERE` with your actual PyPI API token.

### 3. TestPyPI Setup (Optional but Recommended)

For testing releases, also create a TestPyPI account:
1. Go to [https://test.pypi.org/account/register/](https://test.pypi.org/account/register/)
2. Create an API token similar to above
3. Add it to your `.pypirc` file

## Version Management

The project uses semantic versioning (MAJOR.MINOR.PATCH). Current version is managed in:
- `selflayer/__init__.py`
- `pyproject.toml`

## Release Commands

### Using the Release Script

The `./release` script automates the entire release process:

```bash
# Patch release (0.1.0 -> 0.1.1)
./release patch

# Minor release (0.1.0 -> 0.2.0)
./release minor

# Major release (0.1.0 -> 1.0.0)
./release major

# Specific version
./release version 1.2.3
```

### What the Release Script Does

1. **Code Formatting**: Runs `black` and `isort` on the codebase
2. **Version Update**: Updates version in `__init__.py` and `pyproject.toml`
3. **Package Building**: Creates both source and wheel distributions
4. **Local Testing**: Installs and tests the wheel locally
5. **TestPyPI Upload**: Optionally uploads to TestPyPI for testing
6. **PyPI Upload**: Uploads to the real PyPI
7. **Git Tagging**: Creates and pushes a git tag for the release

## Manual Deployment Steps

If you prefer to run steps manually:

### 1. Format Code
```bash
isort selflayer/
# Note: black currently has issues with Python 3.12.5, skip for now
```

### 2. Update Version
```bash
# Edit selflayer/__init__.py and pyproject.toml manually
# Or use the release script for just the version bump:
python release version 0.1.1  # Just updates version, doesn't deploy
```

### 3. Build Package
```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build package
python -m build
```

### 4. Test Local Installation
```bash
# Install the wheel locally
pip install dist/selflayer-*.whl --force-reinstall

# Test the command
selflayer --version
```

### 5. Upload to PyPI
```bash
# Upload to TestPyPI first (recommended)
python -m twine upload --repository testpypi dist/*

# If test upload works, upload to PyPI
python -m twine upload dist/*
```

### 6. Create Git Tag
```bash
git add .
git commit -m "Release v0.1.1"
git tag v0.1.1
git push
git push --tags
```

## Environment Variables

Make sure you have the required environment variables set:

```bash
# Required for functionality
export GEMINI_API_KEY="your_api_key_here"

# Optional for development
export SELFLAYER_LOG_LEVEL="INFO"
```

## Pre-commit Hooks

Pre-commit hooks are installed and will run automatically on commits:

```bash
# Manually run pre-commit on all files
pre-commit run --all-files

# Skip pre-commit for a specific commit
git commit -m "message" --no-verify
```

## Development Workflow

### 1. Daily Development
```bash
# Work on your changes
git add .
git commit -m "Your changes"
git push
```

### 2. When Ready to Release
```bash
# Use the release script for patch updates
./release patch

# Or for specific versions
./release version 0.2.0
```

## Troubleshooting

### Common Issues

1. **PyPI Upload Fails**
   - Check your API token in `~/.pypirc`
   - Ensure the version number hasn't been used before
   - Try uploading to TestPyPI first

2. **Package Build Fails**
   - Check for syntax errors: `python -m py_compile selflayer/*.py`
   - Verify all dependencies are listed in `pyproject.toml`

3. **CLI Commands Don't Work**
   - Check entry points in `pyproject.toml`
   - Reinstall in development mode: `pip install -e .`

4. **Version Conflicts**
   - Make sure version is bumped in both `__init__.py` and `pyproject.toml`
   - Check PyPI to see what versions already exist

### Useful Commands

```bash
# Check package info
python -m pip show selflayer

# List installed entry points
pip show -f selflayer | grep -A 10 entry_points

# Test import
python -c "import selflayer; print(selflayer.__version__)"

# Validate package metadata
python -m build --check

# Check what files would be included in distribution
python setup.py check --metadata
```

## Security Notes

- Never commit API tokens to git
- Use API tokens instead of username/password for PyPI
- Keep your `.pypirc` file permissions at 600
- Enable 2FA on your PyPI account
- The `.env` file is gitignored to protect your Gemini API key

## Release Checklist

Before releasing:

- [ ] All tests pass (or skip if no tests)
- [ ] Code is formatted with isort
- [ ] Version is bumped appropriately
- [ ] CHANGELOG.md is updated (if you create one)
- [ ] README.md is current
- [ ] Dependencies are up to date
- [ ] API key is working in `.env` file

## Next Steps

1. **Set up your PyPI credentials** using the instructions above
2. **Test the release process** using `./release patch`
3. **Create your first release** to PyPI
4. **Share the package** - it will be installable via `pip install selflayer`

The package is now ready for deployment! Users will be able to install it with:

```bash
pip install selflayer
```

And then use it with:

```bash
selflayer --help
sl analyze https://example.com
sl search "AI news"
```
