#!/usr/bin/env python3
"""
Ollie CLI - A retro-themed terminal chat interface with Ollama integration.

Main application file handling chat, context management, and LLM interactions.
"""

import sys
import os
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

# Import local modules
try:
    from ui import UI
    from config import Config
    from utils import Utils
except ImportError:
    # Handle case where modules are in the same directory
    import importlib.util
    import types
    
    def load_module(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    current_dir = Path(__file__).parent
    UI = load_module('ui', current_dir / 'ui.py')
    Config = load_module('config', current_dir / 'config.py')
    Utils = load_module('utils', current_dir / 'utils.py')


class OllieCLI:
    """Main Ollie CLI application class."""
    
    def __init__(self):
        """Initialize the Ollie CLI application."""
        self.config = Config.Config()
        self.ui = UI.UI()
        self.utils = Utils.Utils(self.config)
        self.conversation_history = []
        self.context_embeddings = []
        self.online_mode = True
        self.current_session = None
        
    def check_ollama_installed(self):
        """Check if Ollama is installed and accessible."""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def check_ollama_running(self):
        """Check if Ollama service is running."""
        try:
            result = subprocess.run(
                ['ollama', 'ps'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def list_models(self):
        """List available Ollama models."""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None
    
    def download_model(self, model_name):
        """Download an Ollama model."""
        self.ui.print_info(f"Downloading model: {model_name}")
        try:
            process = subprocess.Popen(
                ['ollama', 'pull', model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in process.stdout:
                print(line, end='', flush=True)
            
            process.wait()
            
            if process.returncode == 0:
                self.ui.print_success(f"Model {model_name} downloaded successfully!")
                return True
            else:
                self.ui.print_error(f"Failed to download model {model_name}")
                return False
        except FileNotFoundError:
            self.ui.print_error("Ollama not found. Please install Ollama first.")
            return False
    
    def send_message(self, message, model=None):
        """Send a message to Ollama and get response."""
        if not self.online_mode:
            self.ui.print_warning("Offline mode - LLM features disabled")
            return None
        
        model = model or self.config.get('default_model', 'llama2')
        
        # Add message to conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Build context from embeddings if available
        context = self._build_context()
        
        # Prepare the prompt with context
        full_prompt = message
        if context:
            full_prompt = f"Context:\n{context}\n\nUser: {message}"
        
        try:
            # Use ollama run command for streaming response
            process = subprocess.Popen(
                ['ollama', 'run', model, full_prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            response_text = ""
            self.ui.print_ai_prefix()
            
            for line in process.stdout:
                response_text += line
                print(line, end='', flush=True)
            
            process.wait()
            
            if process.returncode == 0:
                # Add response to conversation history
                self.conversation_history.append({
                    'role': 'assistant',
                    'content': response_text.strip(),
                    'timestamp': datetime.now().isoformat()
                })
                print()  # New line after response
                return response_text.strip()
            else:
                error = process.stderr.read()
                self.ui.print_error(f"Error from Ollama: {error}")
                return None
                
        except FileNotFoundError:
            self.ui.print_error("Ollama not found. Please install Ollama first.")
            return None
        except Exception as e:
            self.ui.print_error(f"Error communicating with Ollama: {str(e)}")
            return None
    
    def _build_context(self):
        """Build context string from embeddings and recent conversation."""
        context_parts = []
        
        # Add embedded context
        if self.context_embeddings:
            context_parts.append("# Embedded Context")
            for embed in self.context_embeddings[-5:]:  # Last 5 contexts
                context_parts.append(f"- {embed['summary']}")
        
        # Add recent conversation for continuity
        if len(self.conversation_history) > 2:
            context_parts.append("\n# Recent Conversation")
            for msg in self.conversation_history[-4:]:  # Last 4 messages
                role = msg['role'].capitalize()
                content = msg['content'][:200]  # Limit length
                context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def embed_context(self, context_text, source=None):
        """Embed context for future reference."""
        embedding = {
            'summary': context_text[:500],  # Store summary
            'source': source or 'manual',
            'timestamp': datetime.now().isoformat()
        }
        self.context_embeddings.append(embedding)
        self.ui.print_success(f"Context embedded from {source or 'input'}")
    
    def embed_file_context(self, filepath):
        """Embed file contents as context."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self.embed_context(content, source=filepath)
        except Exception as e:
            self.ui.print_error(f"Failed to embed file: {str(e)}")
    
    def toggle_mode(self):
        """Toggle between online and offline mode."""
        self.online_mode = not self.online_mode
        mode = "Online" if self.online_mode else "Offline"
        self.ui.print_info(f"Switched to {mode} mode")
    
    def start_session(self):
        """Start a new chat session."""
        self.current_session = {
            'id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'start_time': datetime.now().isoformat(),
            'messages': []
        }
        self.conversation_history = []
        self.ui.print_success(f"New session started: {self.current_session['id']}")
    
    def export_session(self, output_path=None):
        """Export current session to JSON file."""
        if not self.conversation_history:
            self.ui.print_warning("No conversation history to export")
            return
        
        session_data = {
            'session_id': self.current_session['id'] if self.current_session else 'unknown',
            'export_time': datetime.now().isoformat(),
            'conversation': self.conversation_history,
            'context_embeddings': self.context_embeddings
        }
        
        if output_path is None:
            sessions_dir = self.config.get_sessions_dir()
            output_path = sessions_dir / f"session_{session_data['session_id']}.json"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2)
        
        self.ui.print_success(f"Session exported to: {output_path}")
    
    def load_session(self, session_path):
        """Load a previous session."""
        try:
            with open(session_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            self.conversation_history = session_data.get('conversation', [])
            self.context_embeddings = session_data.get('context_embeddings', [])
            self.current_session = {
                'id': session_data['session_id'],
                'start_time': session_data.get('export_time')
            }
            
            self.ui.print_success(f"Session loaded: {session_data['session_id']}")
            self.ui.print_info(f"Restored {len(self.conversation_history)} messages")
        except Exception as e:
            self.ui.print_error(f"Failed to load session: {str(e)}")
    
    def show_help(self):
        """Display help information."""
        help_text = """
╔════════════════════════════════════════════════════════════════╗
║                     OLLIE CLI - HELP                          ║
╚════════════════════════════════════════════════════════════════╝

CHAT COMMANDS:
  /help                 Show this help message
  /quit, /exit          Exit Ollie CLI
  /mode                 Toggle online/offline mode
  /new                  Start a new session
  /export [path]        Export current session to JSON
  /load <path>          Load a previous session
  /models               List available models
  /download <model>     Download a new model
  /embed <text>         Embed context text
  /embedfile <path>     Embed file contents as context
  /clear                Clear conversation history
  /context              Show current context embeddings
  
DEVELOPER UTILITIES:
  /diff <file1> <file2> Show diff between files
  /scaffold <type>      Create project scaffold
  
GENERAL USAGE:
  - Type your message and press Enter to chat
  - Use /commands for special functions
  - Context is maintained across conversation
  - Sessions can be saved and restored
        """
        print(self.ui.colorize(help_text, 'cyan'))
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        self.ui.print_success("Conversation history cleared")
    
    def show_context(self):
        """Display current context embeddings."""
        if not self.context_embeddings:
            self.ui.print_info("No context embeddings")
            return
        
        print(self.ui.colorize("\n=== Context Embeddings ===", 'cyan'))
        for i, embed in enumerate(self.context_embeddings, 1):
            print(f"{i}. [{embed['source']}] {embed['summary'][:100]}...")
        print()
    
    def interactive_mode(self):
        """Run interactive chat mode."""
        self.ui.show_welcome()
        
        # Check Ollama installation
        if not self.check_ollama_installed():
            self.ui.print_warning("Ollama not found or not installed!")
            self.ui.print_info("Install Ollama from: https://ollama.ai")
            self.ui.print_info("Continuing in offline mode...")
            self.online_mode = False
        elif not self.check_ollama_running():
            self.ui.print_warning("Ollama service not running!")
            self.ui.print_info("Start Ollama with: ollama serve")
            self.online_mode = False
        
        # Start a new session
        self.start_session()
        
        # Main chat loop
        while True:
            try:
                # Get user input
                user_input = self.ui.get_user_input()
                
                if not user_input.strip():
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    self.handle_command(user_input)
                else:
                    # Send message to LLM
                    self.send_message(user_input)
                    
            except KeyboardInterrupt:
                print()
                self.ui.print_info("Use /quit to exit")
                continue
            except EOFError:
                print()
                break
    
    def handle_command(self, command):
        """Handle slash commands."""
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else None
        
        if cmd in ['/quit', '/exit']:
            self.ui.print_info("Exporting session before exit...")
            self.export_session()
            self.ui.print_success("Goodbye! ✨")
            sys.exit(0)
        elif cmd == '/help':
            self.show_help()
        elif cmd == '/mode':
            self.toggle_mode()
        elif cmd == '/new':
            self.export_session()  # Save current session
            self.start_session()
        elif cmd == '/export':
            self.export_session(args)
        elif cmd == '/load':
            if args:
                self.load_session(args)
            else:
                self.ui.print_error("Usage: /load <path>")
        elif cmd == '/models':
            models = self.list_models()
            if models:
                print(self.ui.colorize(models, 'cyan'))
            else:
                self.ui.print_error("Failed to list models")
        elif cmd == '/download':
            if args:
                self.download_model(args)
            else:
                self.ui.print_error("Usage: /download <model_name>")
        elif cmd == '/embed':
            if args:
                self.embed_context(args)
            else:
                self.ui.print_error("Usage: /embed <text>")
        elif cmd == '/embedfile':
            if args:
                self.embed_file_context(args)
            else:
                self.ui.print_error("Usage: /embedfile <path>")
        elif cmd == '/clear':
            self.clear_history()
        elif cmd == '/context':
            self.show_context()
        elif cmd == '/diff':
            if args:
                files = args.split()
                if len(files) == 2:
                    self.utils.show_diff(files[0], files[1])
                else:
                    self.ui.print_error("Usage: /diff <file1> <file2>")
            else:
                self.ui.print_error("Usage: /diff <file1> <file2>")
        elif cmd == '/scaffold':
            if args:
                self.utils.scaffold_project(args)
            else:
                self.ui.print_error("Usage: /scaffold <type>")
        else:
            self.ui.print_error(f"Unknown command: {cmd}")
            self.ui.print_info("Type /help for available commands")


def main():
    """Main entry point for Ollie CLI."""
    parser = argparse.ArgumentParser(
        description='Ollie CLI - Retro-themed terminal chat with Ollama',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--model', '-m',
        help='Specify model to use (default: llama2)',
        default=None
    )
    parser.add_argument(
        '--offline',
        action='store_true',
        help='Start in offline mode'
    )
    parser.add_argument(
        '--load-session',
        help='Load a previous session',
        default=None
    )
    
    args = parser.parse_args()
    
    # Create and run Ollie CLI
    ollie = OllieCLI()
    
    if args.model:
        ollie.config.set('default_model', args.model)
    
    if args.offline:
        ollie.online_mode = False
    
    if args.load_session:
        ollie.load_session(args.load_session)
    
    # Start interactive mode
    ollie.interactive_mode()


if __name__ == '__main__':
    main()
