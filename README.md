# 🌟 Ollie CLI

<div align="center">

**A Retro-Themed Terminal Chat Interface with Ollama Integration**

*CRT-style aesthetics meet modern LLM capabilities*

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## ✨ Features

### Core Capabilities
- 🤖 **Local LLM Integration** - Chat with models via Ollama
- 💬 **Context-Aware Conversations** - Embed and reference context across sessions
- 📜 **Transcript Management** - Save, load, and export chat sessions
- 🔄 **Online/Offline Modes** - Switch between LLM-powered and offline modes
- 🎨 **Retro CRT Aesthetics** - Neon colors and terminal glow effects

### Developer Utilities
- 📊 **Diff Viewer** - Compare files with syntax highlighting
- 🏗️ **Project Scaffolding** - Quick-start templates for Python, Node.js, Web, and Go
- 📝 **Session Logs** - Export conversations to JSON
- 🔍 **Context Embedding** - Load file contents or text as conversation context

### Quality of Life
- 📥 **Model Management** - Download and list Ollama models
- 💾 **Auto-save Sessions** - Automatic session backup on exit
- 🎯 **Minimal Dependencies** - Built primarily with Python standard library
- 🖥️ **Cross-Platform** - Works on Linux, macOS, and Windows

---

## 📦 Installation

### Prerequisites
- **Python 3.6+** - [Download Python](https://www.python.org/downloads/)
- **Ollama** (optional) - [Install Ollama](https://ollama.ai) for LLM features

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/HaydenDev3/ollie_cli.git
   cd ollie_cli
   ```

2. **Run the installer**
   ```bash
   python3 install.py install
   ```

3. **Start Ollie CLI**
   ```bash
   python3 ollie.py
   ```

   Or use the convenience wrapper (after installation):
   ```bash
   ./ollie          # Linux/macOS
   ollie.bat        # Windows
   ```

---

## 🚀 Usage

### Starting Ollie CLI

```bash
python3 ollie.py [options]

Options:
  --model, -m MODEL      Specify model to use (default: llama2)
  --offline              Start in offline mode
  --load-session PATH    Load a previous session
  --help                 Show help message
```

### Chat Commands

Once in Ollie CLI, use these commands:

#### Basic Commands
- `/help` - Show help message
- `/quit` or `/exit` - Exit (auto-saves session)
- `/mode` - Toggle online/offline mode
- `/clear` - Clear conversation history

#### Session Management
- `/new` - Start a new session
- `/export [path]` - Export current session to JSON
- `/load <path>` - Load a previous session

#### Model Management
- `/models` - List available Ollama models
- `/download <model>` - Download a new model (e.g., `/download llama2`)

#### Context Management
- `/embed <text>` - Embed text as context
- `/embedfile <path>` - Embed file contents as context
- `/context` - Show current context embeddings

#### Developer Utilities
- `/diff <file1> <file2>` - Show diff between two files
- `/scaffold <type>` - Create project scaffold
  - Types: `python`, `node`, `web`, `go`

### Example Session

```
┃ You ▸ Hello! What can you help me with?
┃ Ollie ▸ I'm Ollie, your AI assistant! I can help you with...

┃ You ▸ /embedfile mycode.py
✓ Context embedded from mycode.py

┃ You ▸ Can you explain this code?
┃ Ollie ▸ Based on the code you've shared...

┃ You ▸ /diff old_version.py mycode.py
@@ Diff: old_version.py ↔ mycode.py @@
+ def new_function():
-     old_implementation()

┃ You ▸ /export my_session.json
✓ Session exported to: ~/.ollie/sessions/session_20241110_120000.json

┃ You ▸ /quit
✓ Goodbye! ✨
```

---

## 🏗️ Architecture

### File Structure (6 Files)

```
ollie_cli/
├── ollie.py      # Main application - Chat & LLM integration
├── ui.py         # Retro CRT-style UI components
├── config.py     # Configuration management
├── utils.py      # Developer utilities (diff, scaffold)
├── install.py    # Universal install/run script
└── README.md     # Documentation (this file)
```

### Design Philosophy

1. **Minimal Dependencies** - Uses only Python standard library (no pip install required)
2. **Modular Architecture** - Clean separation of concerns
3. **Extensible Design** - Easy to add new commands and features
4. **User-Friendly** - Well-documented code for easy understanding

---

## 🎨 Retro Theme

Ollie CLI features a distinctive retro CRT terminal aesthetic:

- 🟢 **Neon Green** - User input
- 🔵 **Neon Cyan** - AI responses and headers
- 🟣 **Neon Pink** - Important messages
- 🟡 **Neon Yellow** - Warnings
- 🔴 **Red** - Errors
- ⚪ **White/Gray** - Code and context

Special characters and Unicode box-drawing create the authentic terminal feel.

---

## 🔧 Configuration

Config file location: `~/.ollie/config.json`

Default configuration:
```json
{
  "default_model": "llama2",
  "max_context_length": 4096,
  "temperature": 0.7,
  "sessions_dir": "~/.ollie/sessions",
  "config_dir": "~/.ollie",
  "theme": "retro",
  "auto_save_sessions": true,
  "show_timestamps": true
}
```

Edit the config file directly or use the API:
```python
from config import Config
config = Config()
config.set('default_model', 'mistral')
```

---

## 📚 Advanced Features

### Context Embedding

Embed context to give the AI awareness of your files, documentation, or previous conversations:

```bash
# Embed a file
/embedfile ./docs/api_reference.md

# Embed direct text
/embed This project uses FastAPI for the backend

# View embedded contexts
/context
```

### Session Management

Sessions are automatically saved when you exit. Restore them later:

```bash
# Export current session
/export my_important_chat.json

# Load a session
python3 ollie.py --load-session ~/.ollie/sessions/session_20241110_120000.json

# Or within Ollie
/load ~/.ollie/sessions/session_20241110_120000.json
```

### Project Scaffolding

Quick-start new projects with templates:

```bash
/scaffold python    # Create Python project
/scaffold node      # Create Node.js project
/scaffold web       # Create HTML/CSS/JS project
/scaffold go        # Create Go project
```

### Diff Viewer

Compare files with color-coded diff output:

```bash
/diff original.py modified.py
```

---

## 🔌 Extensibility

Ollie CLI is designed to be extensible. Here's how to add new features:

### Adding Custom Commands

Edit `ollie.py` and add to the `handle_command` method:

```python
elif cmd == '/mycommand':
    if args:
        self.my_custom_function(args)
    else:
        self.ui.print_error("Usage: /mycommand <args>")
```

### Adding Scaffold Templates

Edit `utils.py` and add to `SCAFFOLD_TEMPLATES`:

```python
'mytype': {
    'files': {
        'main.ext': 'file content here',
        'README.md': '# My Template\n',
    }
}
```

### Custom UI Themes

Modify `ui.py` COLORS dictionary to change the theme:

```python
COLORS = {
    'neon_green': '\033[38;5;46m',
    'neon_pink': '\033[38;5;201m',
    # Add your custom colors
}
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report bugs** - Open an issue with details
2. **Suggest features** - Describe your use case
3. **Submit PRs** - Follow the existing code style
4. **Improve docs** - Help others understand Ollie

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **Ollama** - For providing excellent local LLM capabilities
- **Python** - For the robust standard library
- **Open Source Community** - For inspiration and support

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/HaydenDev3/ollie_cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/HaydenDev3/ollie_cli/discussions)

---

<div align="center">

**Made with ❤️ and ⚡ by the Ollie CLI community**

*"Where retro aesthetics meet modern AI"*

</div>