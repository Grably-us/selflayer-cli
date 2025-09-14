# SelfLayer 🔍🧠

**AI-Powered Terminal Web Browser for Content Analysis and Research**

[![PyPI version](https://badge.fury.io/py/selflayer.svg)](https://badge.fury.io/py/selflayer)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

SelfLayer is a modern, intelligent terminal-based web browser that combines web scraping, AI-powered content analysis, and beautiful terminal formatting to provide an efficient research and content exploration experience directly from your command line.

## ✨ Features

### 🔍 **Smart Web Search & Analysis**
- **Unified Search & Analysis**: `/find` command searches and analyzes multiple results automatically
- **Step-by-step Analysis**: Traditional `/search` + `/open` workflow for detailed control
- **DuckDuckGo Integration**: Privacy-focused web search
- **Configurable Depth**: Analyze 1-10 search results at once

### 🧠 **AI-Powered Content Analysis**
- **Google Gemini Integration**: State-of-the-art AI analysis using Pydantic AI
- **Structured Output**: WebCards with summaries, key facts, dates, and links
- **Confidence Scoring**: AI provides confidence ratings for each analysis
- **Streaming Support**: Real-time analysis progress updates

### 🎨 **Beautiful Terminal Interface**
- **Rich Formatting**: Colorful, responsive terminal UI using Rich library
- **ASCII Art Branding**: Eye-catching SelfLayer logo
- **Progress Indicators**: Visual feedback for all operations
- **Error Handling**: Graceful error display and recovery

### ⚡ **Performance & Usability**
- **Async Operations**: Non-blocking web requests and AI processing
- **Smart Caching**: Search result and analysis caching
- **Command Aliases**: Short commands (`/f`, `/s`, `/k`, etc.) for power users
- **Persistent Config**: API keys saved locally for seamless usage

## 🚀 Installation

### From PyPI (Recommended)
```bash
pip install selflayer
```

### From Source
```bash
git clone https://github.com/antonvice/selflayer.git
cd selflayer
pip install -e .
```

## 🔧 Setup

1. **Get a Google Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a free API key
   - Copy the key for the next step

2. **Configure SelfLayer**
   ```bash
   selflayer
   # On first run, set your API key:
   /key YOUR_API_KEY_HERE
   ```

Your API key will be securely saved to `~/.selflayer/api_key.txt` for future sessions.

## 📖 Usage

SelfLayer provides two interfaces:

- **`selflayer`**: Interactive Terminal User Interface (TUI) with commands like `/find`, `/search`, `/key`
- **`sl`**: Command Line Interface (CLI) for direct command execution with arguments

### Launch SelfLayer

**Interactive TUI (Recommended)**
```bash
selflayer
```

**Command Line Interface**
```bash
# For direct command execution
sl search "your query" --max-results 3
sl analyze https://example.com
```

### Basic Commands

#### 🔍 **Find & Analyze** (Recommended)
```bash
# Search and analyze top 5 results automatically
/find python machine learning tutorials

# Analyze specific number of results (1-10)
/find quantum computing 3

# Short alias
/f artificial intelligence trends 2024
```

#### 🔎 **Traditional Search**
```bash
# Search only (no analysis)
/search web scraping python
/s data science tools

# Then analyze specific results
/open 1    # Analyze first result
/o 3       # Analyze third result
```

#### 🌐 **Direct URL Analysis**
```bash
# Analyze any webpage directly
/url https://docs.python.org/3/tutorial/
/u https://github.com/trending
```

#### ⚙️ **Configuration**
```bash
# Set API key
/key YOUR_NEW_API_KEY
/k YOUR_NEW_API_KEY

# Clear API key
/key clear

# Check status
/status

# Clear screen
/clear
/c

# Get help
/help
/h

# Quit
/quit
/q
```

### Command Aliases
| Full Command | Alias | Description |
|-------------|-------|-------------|
| `/find` | `/f` | Search and analyze multiple results |
| `/search` | `/s` | Search only (no analysis) |
| `/open` | `/o` | Analyze search result by number |
| `/url` | `/u` | Analyze URL directly |
| `/key` | `/k` | Set/clear API key |
| `/clear` | `/c` | Clear screen |
| `/help` | `/h` | Show help |
| `/quit` | `/q` | Exit SelfLayer |

## 🎯 Use Cases

### 📚 **Research & Learning**
- Quickly analyze multiple sources on a topic
- Get structured summaries of complex articles
- Extract key facts and dates from content
- Discover related links and resources

### 💼 **Professional Analysis**
- Market research and trend analysis
- Competitive intelligence gathering
- Technical documentation review
- News and industry monitoring

### 🔬 **Academic Work**
- Literature review and source analysis
- Fact-checking and verification
- Research paper preparation
- Educational content exploration

## 🏗️ Architecture

SelfLayer is built with modern Python practices:

- **Pydantic AI**: Structured AI outputs with Google Gemini
- **Rich**: Beautiful terminal formatting and progress indicators
- **httpx**: Modern async HTTP client for web requests
- **BeautifulSoup**: HTML parsing and content extraction
- **ddgs**: Privacy-focused DuckDuckGo search

### Project Structure
```
selflayer/
├── __init__.py          # Package initialization and exceptions
├── __main__.py          # Entry point and logging setup
├── ai.py               # Pydantic AI integration with Gemini
├── config.py           # Configuration management
├── models.py           # Pydantic data models
├── search.py           # DuckDuckGo search functionality
├── tui.py             # Rich-powered terminal interface
└── web.py             # Web scraping and content extraction
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the Repository**
   ```bash
   git clone https://github.com/antonvice/selflayer.git
   cd selflayer
   ```

2. **Set Up Development Environment**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Run Tests**
   ```bash
   pytest
   mypy selflayer/
   ruff check selflayer/
   ```

4. **Submit Pull Request**

### Development Tools
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Type Checking**: mypy
- **Linting**: ruff
- **Formatting**: ruff format

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Anton Vice** - CTO, SelfLayer
📧 [anton@selflayer.com](mailto:anton@selflayer.com)
🐙 [GitHub](https://github.com/antonvice)
🔗 [LinkedIn](https://linkedin.com/in/antonvice)

## 🙏 Acknowledgments

- [Pydantic AI](https://github.com/pydantic/pydantic-ai) for structured AI outputs
- [Rich](https://github.com/Textualize/rich) for beautiful terminal formatting
- [DuckDuckGo](https://duckduckgo.com) for privacy-focused search
- [Google Gemini](https://developers.generativeai.google/) for powerful AI analysis

## 📊 Changelog

### v0.1.0 (2024-09-14)
- 🎉 Initial release
- ✨ Unified `/find` command for search + analysis
- 🧠 Google Gemini AI integration
- 🎨 Rich terminal interface
- ⚡ Async operations and caching
- 🔧 Command aliases and persistent config

---

**Made with ❤️ for researchers, developers, and curious minds everywhere.**

*SelfLayer - Because the web deserves intelligent exploration.*
