# SelfLayer TUI v2.0

> **AI-Powered Terminal User Interface for Knowledge Management**

A beautiful, modern terminal interface that connects to the SelfLayer API for comprehensive knowledge management, document processing, note-taking, and AI-powered search and analysis.

![SelfLayer TUI](https://via.placeholder.com/800x400/1a1a1a/00ff00?text=SelfLayer+TUI+v2.0)

## ✨ Features

### 🤖 AI Assistant
- **Streaming conversations** with real-time response display
- **Contextual answers** from your personal knowledge base
- **Follow-up suggestions** and proposed actions
- Natural language queries about your data

### 🔍 Intelligent Search
- **Multi-source search** across documents, notes, and knowledge graph
- **Entity extraction** and relationship mapping
- **Document summaries** with relevant snippets
- **Source attribution** for all results

### 📄 Document Management
- **Upload and process** any document type
- **Automatic summarization** and content extraction
- **Status tracking** for processing pipeline
- **Rich metadata** display with file details

### 📝 Note Taking
- **Quick note creation** with title and content
- **Edit and update** existing notes
- **Tag organization** and categorization
- **Rich text preview** in terminal cards

### 🔗 Integrations
- **Connect external services** (Gmail, Google Calendar, Drive, etc.)
- **OAuth flow management** with redirect handling
- **Connection status monitoring**
- **Easy disconnect** with confirmation

### 📢 Notifications
- **Real-time updates** on processing, integrations, etc.
- **Unread count tracking**
- **Batch operations** (mark all as read)
- **Type-based filtering** and display

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/antonvice/SelfTUI
cd SelfTUI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Configuration

1. **Set up your environment variables:**

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your SelfLayer API key
export SELFLAYER_API_KEY=sl_live_your_api_key_here
```

2. **Get your SelfLayer API key:**
   - Visit your SelfLayer dashboard
   - Go to API Settings
   - Generate a new API key
   - Copy the key (starts with `sl_live_`)

### Running the TUI

```bash
# Run directly
python -m selflayer

# Or if installed
selflayer
```

## 📖 Usage Guide

### 🎯 Command Overview

| Command | Shortcut | Description |
|---------|----------|-------------|
| `/ask <question>` | `/a` | Chat with AI assistant |
| `/search <query>` | `/s` | Search knowledge base |
| `/documents` | `/d` | Manage documents |
| `/notes` | `/n` | Manage notes |
| `/integrations` | `/i` | Manage connections |
| `/notifications` | | View notifications |
| `/rms` | `/r` | Random memory surfacing |
| `/help` | `/h` | Show help |
| `/clear` | `/c` | Clear screen |
| `/quit` | `/q` | Exit application |

### 🤖 AI Assistant

```bash
# Ask questions about your data
/ask What are my recent project notes?
/ask Summarize today's important emails
/ask What documents mention machine learning?

# The AI will provide contextual answers with:
# - Streaming real-time responses
# - Suggested follow-up questions
# - Proposed actions
```

### 🔍 Search

```bash
# Search across all your data
/search machine learning projects
/search meeting notes from last week
/search documents about API integration

# Results include:
# - Knowledge graph entities
# - Document summaries
# - Source chunks with context
```

### 📄 Document Management

```bash
# List all documents
/documents
/d

# Upload new document
/d new /path/to/document.pdf
/d new ~/Documents/report.docx

# View document details
/d 1  # View document #1
/d 2  # View document #2

# Delete document (with confirmation)
/d delete 1
```

### 📝 Note Management

```bash
# List all notes
/notes
/n

# Create new note
/n new "Meeting Notes" "Discussed project timeline and deliverables"
/n new "Ideas" "Revolutionary AI-powered terminal interface"

# View note details
/n 1  # View note #1

# Edit note content
/n edit 1 "Updated content here"

# Delete note (with confirmation)
/n delete 1
```

### 🔗 Integration Management

```bash
# List all integrations
/integrations
/i

# Connect new integration
/i connect gmail
/i connect google_calendar
/i connect google_drive

# Disconnect integration
/i disconnect 1  # Disconnect integration #1
```

### 📢 Notifications

```bash
# View all notifications
/notifications

# Mark specific notification as read
/notifications read 1

# Mark all notifications as read
/notifications clear
```

## 🎨 Beautiful Terminal UI

### Rich Cards and Tables
- **Profile cards** with user information and usage stats
- **Document tables** with status, size, and processing info
- **Note cards** with previews and tag information
- **Search results** with categorized sections
- **Integration tables** with provider status
- **Notification lists** with read/unread states

### Color-Coded Status
- 🟢 **Green**: Success, completed, connected
- 🟡 **Yellow**: Processing, pending, warnings
- 🔴 **Red**: Errors, failed, disconnected
- 🔵 **Blue**: Information, details
- 🟣 **Purple**: Headers, titles

### Interactive Elements
- **Progress bars** for uploads and processing
- **Streaming text** for AI responses
- **Confirmation dialogs** for destructive actions
- **Rich formatting** with emojis and styling

## 🛠️ Development

### Project Structure

```
SelfTUI/
├── selflayer/           # Main package
│   ├── __init__.py     # Package initialization
│   ├── client.py       # SelfLayer API client
│   ├── models.py       # Pydantic data models
│   ├── renderers.py    # Rich rendering functions
│   ├── tui.py          # Main TUI application
│   └── styles.css      # TUI styling (if needed)
├── tests/              # Test suite
├── requirements.txt    # Dependencies
├── pyproject.toml     # Project configuration
├── .env.example       # Environment template
└── README.md          # This file
```

### Key Components

1. **API Client** (`client.py`): Comprehensive async HTTP client with error handling, streaming support, and all SelfLayer endpoints
2. **Models** (`models.py`): Pydantic models for all API responses with display helpers
3. **Renderers** (`renderers.py`): Beautiful Rich formatting for all data types
4. **TUI** (`tui.py`): Main terminal interface with command routing and state management

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=selflayer --cov-report=html

# Run specific test file
pytest tests/test_client.py -v

# Run tests with output
pytest -s
```

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run linting
ruff check selflayer/

# Run formatting
ruff format selflayer/

# Type checking
mypy selflayer/
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------||
| `SELFLAYER_API_KEY` | ✅ Yes | Your SelfLayer API key | None |
| `SELFLAYER_BASE_URL` | ❌ No | API base URL | `https://api.selflayer.com/api/v1` |
| `SELFLAYER_LOG_LEVEL` | ❌ No | Logging level | `INFO` |

### API Key Format

SelfLayer API keys follow the format: `sl_live_` followed by 64 random characters.

Example: `sl_live_1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef`

## 🚨 Troubleshooting

### Common Issues

**API Key Not Found**
```bash
# Error: SelfLayer API key required
export SELFLAYER_API_KEY=your_key_here
# or add to .env file
```

**Connection Errors**
```bash
# Check your internet connection
ping api.selflayer.com

# Verify API key is valid
curl -H "Authorization: Bearer $SELFLAYER_API_KEY" https://api.selflayer.com/api/v1/profile
```

**Permission Errors**
```bash
# Your API key might not have sufficient permissions
# Check your SelfLayer dashboard for API key settings
```

### Debugging

Enable debug logging:
```bash
export SELFLAYER_LOG_LEVEL=DEBUG
```

View logs:
```bash
# Logs are written to ~/.selflayer/logs/selflayer_tui.log
tail -f ~/.selflayer/logs/selflayer_tui.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- **Type Annotations**: All functions must have complete type annotations
- **Documentation**: All public functions require comprehensive docstrings
- **Testing**: Write tests for all new functionality
- **Formatting**: Use `ruff format` for code formatting
- **Linting**: Use `ruff check` for linting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [SelfLayer API Guide](v07/SELFLAYER_TUI_API_GUIDE.md)
- **Issues**: Open an issue on GitHub
- **Email**: Contact anton@selflayer.com
- **Discord**: Join our community server

## 🎉 Acknowledgments

- **Rich**: For beautiful terminal formatting
- **httpx**: For modern async HTTP client
- **Pydantic**: For robust data validation
- **SelfLayer Team**: For the amazing API

---

**Made with ❤️ by the SelfLayer team**

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
