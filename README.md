# Ollie-CLI

A terminal-based interface for managing Ollama AI models locally. No browser, no cloud — just fast model control in a clean terminal interface.

## Features

- **Model Management**: List, pull, and delete Ollama models
- **Interactive Chat**: Chat with your models directly in the terminal
- **Curses-based UI**: Clean, keyboard-driven interface
- **Logging**: All operations logged to `ollie.log` for debugging
- **Cross-platform**: Works on Linux, macOS, and Windows (with setup)
- **Robust Error Handling**: Graceful handling of Ollama CLI issues

## Prerequisites

1. **Ollama**: Must be installed and available in your PATH
   - Download from: https://ollama.ai/
   - Verify installation: `ollama --version`

2. **Python 3.7+**: Required to run the application

3. **Windows Users**: Additional setup needed
   - Install `windows-curses`: `pip install windows-curses`
   - OR use WSL (Windows Subsystem for Linux)
   - OR use Git Bash or another Unix-like terminal

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/HaydenDev3/ollie_cli.git
   cd ollie_cli
   ```

2. (Optional) Install Windows support if on Windows:
   ```bash
   pip install windows-curses
   ```

## Usage

Run the application:
```bash
python main.py
```

### Keyboard Controls

- **↑/↓**: Navigate through models
- **ENTER**: Start chat with selected model
- **P**: Pull a new model
- **D**: Delete selected model
- **R**: Refresh model list
- **Q**: Quit application

### Logging

All operations are logged to `ollie.log` in the current directory. Check this file for:
- Startup information
- Model operations (list, pull, delete)
- Chat sessions
- Errors and exceptions

## Features in Detail

### Curses Suspend/Resume

The application properly suspends and resumes the curses interface when running interactive Ollama commands (chat, pull), ensuring a smooth user experience.

### Terminal Resize Handling

The UI automatically handles terminal resize events (KEY_RESIZE) and redraws the interface accordingly.

### Robust Ollama Wrapper

The `ollama.py` module provides:
- **ensure_available()**: Validates Ollama CLI presence and version
- **list_models()**: Lists models with fallback JSON parsing
- **pull_model()**: Pulls models with streaming output support
- **delete_model()**: Deletes models with descriptive error handling
- **run_chat()**: Launches interactive chat sessions

### Windows Compatibility

On Windows, the application:
- Detects the platform and shows compatibility guidance
- Recommends installing `windows-curses` or using WSL
- Allows users to continue if they have proper setup

## Troubleshooting

### "Ollama CLI not found"

Make sure Ollama is installed and in your PATH:
```bash
ollama --version
```

If not found, install from https://ollama.ai/ and ensure it's added to your PATH.

### Windows curses errors

Install the Windows curses library:
```bash
pip install windows-curses
```

Or use WSL for a better experience.

### Terminal too small

Ensure your terminal window is at least 80x24 characters for optimal display.

## Project Structure

```
ollie_cli/
├── main.py           # Main application with curses UI
├── ollama.py         # Ollama CLI wrapper module
├── requirements.txt  # Python dependencies
├── README.md         # This file
└── ollie.log        # Log file (created on first run)
```

## Development

The project is kept minimal with only essential files in the root directory (maximum 6 files).

### Key Implementation Details

- **Logging**: Simple file logger at INFO level in `ollie.log`
- **Curses Management**: Uses `def_prog_mode()` and `reset_prog_mode()` for suspend/resume
- **Error Handling**: All Ollama operations wrapped with proper exception handling
- **Streaming Output**: Model pulls stream progress to the terminal in real-time

## License

MIT License - See repository for details.

## Contributing

Issues and pull requests welcome! Please ensure changes maintain the minimal file structure (≤6 files in root).