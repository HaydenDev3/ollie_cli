# Ollie CLI

A powerful, modular terminal interface for managing and chatting with local LLMs via Ollama. Built with Python, designed for developers, and optimized for both interactive and command-line workflows.

## 🌟 Features

### Core Functionality
- **Interactive UI**: Clean, curses-based terminal interface for model management
- **Chat Interface**: Direct chat with local LLM models through Ollama
- **Model Management**: List, pull, and delete Ollama models
- **Transcript Management**: Automatic session logging with context embedding support
- **Online/Offline Modes**: Toggle between online (with model pulling) and offline modes

### Developer Tools
- **Diff Viewer**: Compare files or chat session transcripts with unified diff view
- **Project Scaffolding**: Quick-start templates for Python, Node.js, web, and API projects
- **Session Export**: Export chat transcripts in txt, json, or markdown formats
- **Comprehensive Logging**: All operations logged to `~/.ollie/ollie.log`

### Universal Compatibility
- **Cross-Platform**: Works on Linux, MacOS, and Windows
- **Universal Run Script**: Single `run.py` handles setup and execution across all platforms
- **Modular Design**: Clean separation of concerns in ≤ 6 core files

## 📋 Prerequisites

1. **Python 3.7+** - Required to run Ollie CLI
2. **Ollama** - Must be installed and in your PATH
   - Download from: https://ollama.ai/
   - Verify: `ollama --version`

3. **Windows Users Only**:
   - Install `windows-curses`: `pip install windows-curses`
   - OR use WSL (Windows Subsystem for Linux)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/HaydenDev3/ollie_cli.git
cd ollie_cli

# Run the universal setup script
python run.py
```

The `run.py` script will automatically:
- Check Python version
- Verify Ollama installation
- Install platform-specific dependencies
- Launch Ollie CLI

### Basic Usage

#### Interactive UI Mode (Recommended)
```bash
python run.py
# Or directly:
python ollie.py
```

**Keyboard Controls:**
- `↑/↓`: Navigate through models
- `ENTER`: Start chat with selected model
- `P`: Pull a new model
- `D`: Delete selected model
- `R`: Refresh model list
- `M`: Toggle online/offline mode
- `Q`: Quit application

#### Command-Line Mode

```bash
# List available models
python ollie.py list

# Pull a model
python ollie.py pull llama2

# Start chat session
python ollie.py chat llama2

# Delete a model
python ollie.py delete llama2 --force

# Export a chat transcript
python ollie.py export <session-id> --output chat.txt --format txt

# Switch modes
python ollie.py mode --set offline
```

### Developer Commands

#### Diff Viewer
```bash
# Compare two files
python ollie.py diff --files file1.txt file2.txt

# Compare two chat sessions
python ollie.py diff --sessions abc123 def456 --context 5
```

#### Project Scaffolding
```bash
# Scaffold a Python project
python ollie.py scaffold python --name my_project

# Scaffold a Node.js project
python ollie.py scaffold node --name my_app --output ./projects

# Scaffold a web project
python ollie.py scaffold web --name my_website

# Scaffold an API project
python ollie.py scaffold api --name my_api
```

## 📁 File Structure

The project follows a modular design with ≤ 6 core files:

```
ollie_cli/
├── run.py              # Universal install/run script
├── ollie.py            # Main application and CLI entry point
├── ollama_client.py    # Ollama CLI wrapper and API client
├── transcript.py       # Transcript and context management
├── dev_utils.py        # Developer utilities (diff, scaffold)
├── ui.py               # Curses-based terminal UI
└── README.md           # This file
```

### Data Storage

Ollie CLI stores data in `~/.ollie/`:
- `~/.ollie/ollie.log` - Application logs
- `~/.ollie/transcripts/` - Chat session transcripts

## 🔧 Configuration

### Environment Variables

- `OLLAMA_HOST` - Override Ollama API host (default: localhost)

### Logging

All operations are logged to `~/.ollie/ollie.log`. Adjust log level in `ollie.py`:

```python
logging.basicConfig(level=logging.INFO)  # Change to DEBUG for verbose logs
```

## 💡 Examples

### Example 1: Quick Chat Session

```bash
# Pull a model if needed
python ollie.py pull llama2

# Start chatting
python ollie.py chat llama2
```

In chat:
```
You: What is Python?
Assistant: Python is a high-level programming language...

You: /save
Save to file: my_chat.txt
Saved to my_chat.txt

You: /exit
```

### Example 2: Scaffold a Full Project

```bash
# Create a new Python project
python ollie.py scaffold python --name awesome_project

# Navigate and explore
cd awesome_project
ls -la

# Structure created:
# awesome_project/
# ├── awesome_project/
# │   ├── __init__.py
# │   └── main.py
# ├── tests/
# ├── requirements.txt
# ├── README.md
# └── .gitignore
```

### Example 3: Compare Session Transcripts

```bash
# List available sessions
ls ~/.ollie/transcripts/

# Compare two sessions
python ollie.py diff --sessions abc123 def456
```

## 🌐 Platform-Specific Notes

### Linux/MacOS
- Works out of the box
- Curses support built into Python

### Windows
- Requires `windows-curses` package
- Install with: `pip install windows-curses`
- Alternative: Use WSL or Git Bash
- The `run.py` script will prompt for installation

## 🛠️ Development

### Adding New Features

The modular design makes it easy to extend Ollie CLI:

1. **New Commands**: Add to `ollie.py` in the `_cmd_*` methods
2. **UI Features**: Modify `ui.py` to add new keyboard shortcuts
3. **Ollama Operations**: Extend `ollama_client.py`
4. **Developer Tools**: Add to `dev_utils.py`

### Code Organization

- **ollie.py**: Main application logic and argument parsing
- **ollama_client.py**: Ollama API wrapper with error handling
- **transcript.py**: Session management and export functionality
- **dev_utils.py**: Developer utilities (diff, scaffold)
- **ui.py**: Curses-based interactive interface
- **run.py**: Universal cross-platform launcher

## 🐛 Troubleshooting

### "Ollama CLI not found"

```bash
# Check if Ollama is installed
ollama --version

# If not installed, download from https://ollama.ai/

# Ensure it's in your PATH
which ollama  # Linux/Mac
where ollama  # Windows
```

### "Curses not available" on Windows

```bash
# Install windows-curses
pip install windows-curses

# Or use command-line mode
python ollie.py chat llama2
```

### "Permission denied" on run.py

```bash
# Make it executable (Linux/Mac)
chmod +x run.py
./run.py

# Or run with python
python run.py
```

### Model Pull Issues

```bash
# Check Ollama service is running
ollama list

# Try pulling directly
ollama pull llama2

# Check logs
tail -f ~/.ollie/ollie.log
```

## 📝 License

MIT License - Feel free to use and modify for your needs.

## 🤝 Contributing

Contributions are welcome! This project follows open-source best practices:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 🔗 Links

- **Ollama**: https://ollama.ai/
- **Project Repository**: https://github.com/HaydenDev3/ollie_cli

## 📚 Documentation

### Architecture

Ollie CLI follows a modular architecture:

```
User Input
    ↓
ollie.py (Router)
    ↓
├── UI Mode → ui.py → ollama_client.py
├── Chat → ollama_client.py + transcript.py
├── Dev Tools → dev_utils.py
└── Model Mgmt → ollama_client.py
```

### Session Management

Chat sessions are automatically saved to `~/.ollie/transcripts/` with:
- Unique session ID
- Model information
- Message history
- Context embeddings (future enhancement)
- Timestamps

### Offline Mode

Offline mode prevents:
- Model pulling
- Online model queries
- Only allows chat with locally available models

Useful for:
- Air-gapped systems
- Bandwidth conservation
- Stable model versions

---

**Built with ❤️ for developers who love terminal interfaces and local LLMs.**
