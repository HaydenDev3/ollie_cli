#!/usr/bin/env python3
"""
Universal Install/Run Script for Ollie CLI

Compatible with Linux, macOS, and Windows.
Handles installation, dependencies, and running the application.
"""

import sys
import os
import subprocess
import platform
from pathlib import Path


class OllieInstaller:
    """Universal installer for Ollie CLI."""
    
    def __init__(self):
        self.platform = platform.system()
        self.python_cmd = self._get_python_command()
        self.script_dir = Path(__file__).parent
    
    def _get_python_command(self):
        """Get the appropriate Python command for the platform."""
        # Try python3 first, then python
        for cmd in ['python3', 'python']:
            try:
                result = subprocess.run(
                    [cmd, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    # Check version is 3.6+
                    version_str = result.stdout + result.stderr
                    if 'Python 3.' in version_str:
                        return cmd
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        return None
    
    def check_python_version(self):
        """Check if Python version is adequate (3.6+)."""
        if self.python_cmd is None:
            return False, "Python 3.6+ not found"
        
        try:
            result = subprocess.run(
                [self.python_cmd, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            version_str = result.stdout + result.stderr
            # Extract version number
            import re
            match = re.search(r'Python (\d+)\.(\d+)', version_str)
            if match:
                major, minor = int(match.group(1)), int(match.group(2))
                if major >= 3 and minor >= 6:
                    return True, f"Python {major}.{minor} detected"
                else:
                    return False, f"Python {major}.{minor} is too old (need 3.6+)"
            
            return False, "Could not parse Python version"
        except Exception as e:
            return False, f"Error checking Python: {e}"
    
    def check_ollama_installed(self):
        """Check if Ollama is installed."""
        try:
            result = subprocess.run(
                ['ollama', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def print_banner(self):
        """Print installation banner."""
        banner = """
╔════════════════════════════════════════════════════════════╗
║              OLLIE CLI - Installation                     ║
║         Retro-Themed Terminal Chat with Ollama            ║
╚════════════════════════════════════════════════════════════╝
"""
        print(banner)
    
    def print_section(self, title):
        """Print section header."""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    
    def install(self):
        """Run installation process."""
        self.print_banner()
        
        self.print_section("System Check")
        
        # Check Python
        print("Checking Python installation...")
        py_ok, py_msg = self.check_python_version()
        print(f"  {py_msg}")
        
        if not py_ok:
            print("\n❌ Installation failed: Python 3.6+ is required")
            print("   Please install Python from: https://python.org")
            return False
        
        print("  ✓ Python check passed")
        
        # Check Ollama
        print("\nChecking Ollama installation...")
        if self.check_ollama_installed():
            print("  ✓ Ollama is installed")
        else:
            print("  ⚠ Ollama not found")
            print("  Note: Ollama is required for LLM features")
            print("  Install from: https://ollama.ai")
            print("  You can still run Ollie CLI in offline mode")
        
        # Check if running from source
        self.print_section("Setup")
        
        ollie_py = self.script_dir / 'ollie.py'
        if not ollie_py.exists():
            print("❌ ollie.py not found in the current directory")
            return False
        
        print("✓ All Ollie CLI files found")
        
        # Create config directory
        config_dir = Path.home() / '.ollie'
        config_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Config directory created: {config_dir}")
        
        # Create sessions directory
        sessions_dir = config_dir / 'sessions'
        sessions_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Sessions directory created: {sessions_dir}")
        
        self.print_section("Installation Complete")
        print("✓ Ollie CLI is ready to use!")
        print("\nTo run Ollie CLI:")
        print(f"  {self.python_cmd} {self.script_dir / 'ollie.py'}")
        print("\nOr run this script again:")
        print(f"  {self.python_cmd} {__file__}")
        
        # Create a convenience wrapper script if possible
        self._create_wrapper_script()
        
        return True
    
    def _create_wrapper_script(self):
        """Create a convenience wrapper script."""
        try:
            if self.platform == "Windows":
                wrapper_path = self.script_dir / 'ollie.bat'
                content = f'@echo off\n{self.python_cmd} "{self.script_dir / "ollie.py"}" %*\n'
            else:
                wrapper_path = self.script_dir / 'ollie'
                content = f'#!/bin/bash\n{self.python_cmd} "{self.script_dir / "ollie.py"}" "$@"\n'
            
            with open(wrapper_path, 'w') as f:
                f.write(content)
            
            # Make executable on Unix-like systems
            if self.platform != "Windows":
                os.chmod(wrapper_path, 0o755)
            
            print(f"\n✓ Created convenience wrapper: {wrapper_path}")
            if self.platform != "Windows":
                print(f"  You can run: ./{wrapper_path.name}")
            else:
                print(f"  You can run: {wrapper_path.name}")
                
        except Exception as e:
            print(f"\n⚠ Could not create wrapper script: {e}")
    
    def run(self):
        """Run Ollie CLI."""
        ollie_py = self.script_dir / 'ollie.py'
        
        if not ollie_py.exists():
            print("❌ ollie.py not found")
            print(f"   Expected location: {ollie_py}")
            return False
        
        try:
            # Run ollie.py with all command line arguments
            subprocess.run([self.python_cmd, str(ollie_py)] + sys.argv[1:])
            return True
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            return True
        except Exception as e:
            print(f"❌ Error running Ollie CLI: {e}")
            return False
    
    def show_help(self):
        """Show help information."""
        help_text = """
Usage: python3 install.py [command]

Commands:
  install    Run installation and setup
  run        Run Ollie CLI (default if no command given)
  help       Show this help message

Examples:
  python3 install.py install    # Install and setup
  python3 install.py run        # Run Ollie CLI
  python3 install.py            # Run Ollie CLI (default)

Platform Support:
  ✓ Linux
  ✓ macOS
  ✓ Windows

Requirements:
  - Python 3.6 or higher
  - Ollama (optional, for LLM features)
        """
        print(help_text)


def main():
    """Main entry point for installer."""
    installer = OllieInstaller()
    
    # Parse command
    command = sys.argv[1] if len(sys.argv) > 1 else 'run'
    
    if command == 'install':
        installer.install()
    elif command == 'run':
        installer.run()
    elif command == 'help' or command == '--help' or command == '-h':
        installer.show_help()
    else:
        # Assume it's meant to be passed to ollie.py
        installer.run()


if __name__ == '__main__':
    main()
