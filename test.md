# SelfLayer TUI Testing Guide

This guide explains how to properly test your SelfLayer TUI after making code changes.

## 🚨 Important: Why Changes Don't Show Up

When you run `python -m selflayer` manually, you might see the **old version** because:

1. **Package Installation**: If you previously installed the package with `pip install -e .`, Python may be using the installed version instead of your current working directory code
2. **Module Path Priority**: Python's module resolution might prioritize installed packages over local code
3. **Import Caching**: Python caches imported modules, so changes might not reflect immediately

## ✅ Proper Testing Workflow

### Method 1: Direct Module Execution (Recommended)
```bash
# Navigate to project root
cd /Users/antonvice/Documents/programming/SelfLayer/SelfTUI

# Run directly from source (bypasses any installed versions)
python -m selflayer.tui
```

### Method 2: Force Reload with Development Install
```bash
# Uninstall any existing version
pip uninstall selflayer -y

# Reinstall in development mode (editable)
pip install -e .

# Now run normally
python -m selflayer
```

### Method 3: Run Main Module Directly
```bash
# Navigate to project root
cd /Users/antonvice/Documents/programming/SelfLayer/SelfTUI

# Run the main TUI file directly
python selflayer/tui.py
```

### Method 4: PYTHONPATH Override
```bash
# Set PYTHONPATH to prioritize current directory
PYTHONPATH=/Users/antonvice/Documents/programming/SelfLayer/SelfTUI python -m selflayer
```

## 🔄 Development Workflow Steps

### 1. Make Your Changes
Edit any files in the `selflayer/` directory:
- `tui.py` - Main TUI application
- `renderers.py` - Display formatting
- `models.py` - Data models
- `client.py` - API client
- etc.

### 2. Test Your Changes
```bash
# Quick test (recommended for development)
cd /Users/antonvice/Documents/programming/SelfLayer/SelfTUI
python -m selflayer.tui

# OR if you want to test the full package
pip install -e . && python -m selflayer
```

### 3. Verify Changes Are Applied
Look for:
- Updated version messages
- New functionality working
- Bug fixes applied
- UI changes visible

### 4. Run Tests (if available)
```bash
# Run unit tests
pytest tests/ -v

# Run specific test file
pytest tests/test_tui.py -v

# Run with coverage
pytest --cov=selflayer --cov-report=html
```

## 🐛 Debugging Tips

### Check What Version Is Running
Add this to your code to verify which file is being executed:
```python
import os
print(f"Running from: {__file__}")
print(f"Current directory: {os.getcwd()}")
```

### Force Module Reload
If you're in an interactive Python session:
```python
import importlib
import selflayer.tui
importlib.reload(selflayer.tui)
```

### Check Python Module Path
```bash
python -c "import selflayer; print(selflayer.__file__)"
```

## 📝 What I Did in the Last Test

Here's exactly what I did to test the graph visualization changes:

1. **Made Code Changes**: Updated `selflayer/renderers.py` with new graph visualization functions
2. **Ran Direct Test**: Used `python -m selflayer` from the project root
3. **Executed Search**: Ran `/search anton` command to trigger the graph functionality
4. **Verified Output**: Confirmed the visual graph was generated and saved
5. **Opened Image**: Used `open` command to view the generated graph

The key was running from the project root directory where the changes were made.

## 🚀 Quick Test Commands

```bash
# Single command to test after changes (fish shell)
cd /Users/antonvice/Documents/programming/SelfLayer/SelfTUI && python -m selflayer

# Test specific functionality
cd /Users/antonvice/Documents/programming/SelfLayer/SelfTUI && echo "/search test" | python -m selflayer

# Check if imports work
python -c "from selflayer import tui; print('Import successful')"
```

## 🔧 Environment Setup

Make sure your environment is properly configured:

```bash
# Check Python version
python --version

# Check if in virtual environment
which python

# Verify dependencies
pip list | grep -E "(textual|rich|httpx|pydantic)"

# Install missing dependencies
pip install -r requirements.txt
```

## ✨ Pro Tips

1. **Always test from project root**: `cd /Users/antonvice/Documents/programming/SelfLayer/SelfTUI`
2. **Use development install**: `pip install -e .` for automatic change detection
3. **Clear Python cache**: Delete `__pycache__` directories if imports act strange
4. **Check file permissions**: Ensure your changes were actually saved
5. **Use version tags**: Add version prints to verify correct code is running

## 🎯 Testing Checklist

Before considering your changes complete:

- [ ] Code runs without errors
- [ ] New features work as expected
- [ ] Existing functionality still works
- [ ] UI displays correctly
- [ ] API calls succeed
- [ ] Error handling works
- [ ] Performance is acceptable
- [ ] Visual elements render properly

## 🚨 Common Issues

| Issue | Solution |
|-------|----------|
| Old code runs | Use `pip install -e .` or run `python -m selflayer.tui` |
| Import errors | Check `PYTHONPATH` and current directory |
| Changes not visible | Clear `__pycache__` and restart Python |
| Module not found | Verify you're in the correct directory |
| API errors | Check local server is running on `localhost:8001` |

---

**Remember**: Always test from the project root directory and use development installation for the smoothest development experience!
