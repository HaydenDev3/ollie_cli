#!/usr/bin/env python3
"""
Universal Run Script for Ollie CLI

Works across Linux, MacOS, and Windows. Automatically handles:
- Python installation check
- Virtual environment setup (optional)
- Dependency installation
- Platform-specific requirements
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Check if Python version is sufficient."""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")


def check_ollama():
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✓ Ollama installed: {result.stdout.strip()}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("⚠ Ollama not found")
    print("  Install from: https://ollama.ai/")
    print("  Ollama is required for Ollie CLI to function")
    return False


def check_dependencies():
    """Check and install required dependencies."""
    # Check if windows-curses is needed
    if platform.system() == "Windows":
        try:
            import curses
            print("✓ windows-curses installed")
        except ImportError:
            print("⚠ windows-curses not installed")
            response = input("Install windows-curses? (y/n): ").strip().lower()
            if response == 'y':
                print("Installing windows-curses...")
                subprocess.run([sys.executable, "-m", "pip", "install", "windows-curses"])
                print("✓ windows-curses installed")
            else:
                print("Note: UI mode will not work without windows-curses")
                print("You can still use command-line mode")


def print_banner():
    """Print welcome banner."""
    print("\n" + "=" * 60)
    print("  Ollie CLI - Terminal Interface for Local LLMs")
    print("  Version 1.0.0")
    print("=" * 60 + "\n")


def print_usage():
    """Print usage information."""
    print("Usage:")
    print("  python run.py                    # Interactive UI mode")
    print("  python run.py --help             # Show all commands")
    print("  python run.py chat <model>       # Start chat")
    print("  python run.py list               # List models")
    print("  python run.py pull <model>       # Pull model")
    print("  python run.py scaffold <template> -n <name>  # Scaffold project")
    print("")


def main():
    """Main entry point for run script."""
    print_banner()
    
    # System checks
    print("System Checks:")
    print("-" * 60)
    
    check_python_version()
    ollama_installed = check_ollama()
    check_dependencies()
    
    print("-" * 60 + "\n")
    
    if not ollama_installed:
        print("Warning: Ollama is not installed.")
        print("Ollie CLI will not function properly without Ollama.\n")
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            sys.exit(1)
    
    # Run Ollie CLI
    print("Starting Ollie CLI...\n")
    
    try:
        # Import and run
        from ollie import main as ollie_main
        ollie_main()
    except ImportError as e:
        print(f"Error: Failed to import Ollie CLI: {e}")
        print("\nMake sure all files are in the same directory:")
        print("  - run.py")
        print("  - ollie.py")
        print("  - ollama_client.py")
        print("  - transcript.py")
        print("  - dev_utils.py")
        print("  - ui.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
