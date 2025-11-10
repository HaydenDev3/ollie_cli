#!/usr/bin/env python3
"""
Ollie CLI - A modular terminal interface for local LLM interaction via Ollama

Main entry point and core application logic.
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Local imports
from ollama_client import OllamaClient, OllamaError
from transcript import TranscriptManager
from ui import OllieUI
from dev_utils import DevUtils


__version__ = "1.0.0"

# Configure logging
LOG_FILE = Path.home() / ".ollie" / "ollie.log"
LOG_FILE.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class OllieCLI:
    """Main Ollie CLI application."""

    def __init__(self, skip_ollama_check=False):
        """Initialize Ollie CLI components."""
        self._ollama_client = None
        self._skip_ollama_check = skip_ollama_check
        self.transcript_manager = TranscriptManager()
        self.dev_utils = DevUtils()
        self.mode = "online"  # online or offline
        
        logger.info(f"Ollie CLI v{__version__} initialized")
    
    @property
    def ollama_client(self):
        """Lazy initialization of Ollama client."""
        if self._ollama_client is None:
            self._ollama_client = OllamaClient()
        return self._ollama_client

    def run_interactive(self):
        """Run the interactive UI mode."""
        try:
            import curses
            ui = OllieUI(self)
            curses.wrapper(ui.run)
        except ImportError:
            logger.error("Curses not available. Install windows-curses on Windows.")
            print("Error: Curses library not available.")
            print("On Windows, install: pip install windows-curses")
            sys.exit(1)
        except KeyboardInterrupt:
            logger.info("User interrupted application")
            print("\nGoodbye!")
        except Exception as e:
            logger.exception("Fatal error in interactive mode")
            print(f"Fatal error: {e}")
            sys.exit(1)

    def run_command(self, args):
        """Run a specific command from CLI arguments."""
        try:
            if args.command == "chat":
                self._cmd_chat(args)
            elif args.command == "list":
                self._cmd_list(args)
            elif args.command == "pull":
                self._cmd_pull(args)
            elif args.command == "delete":
                self._cmd_delete(args)
            elif args.command == "diff":
                self._cmd_diff(args)
            elif args.command == "scaffold":
                self._cmd_scaffold(args)
            elif args.command == "export":
                self._cmd_export(args)
            elif args.command == "mode":
                self._cmd_mode(args)
            else:
                print(f"Unknown command: {args.command}")
                sys.exit(1)
        except OllamaError as e:
            logger.error(f"Ollama error: {e}")
            print(f"Error: {e}")
            sys.exit(1)
        except Exception as e:
            logger.exception("Command execution failed")
            print(f"Error: {e}")
            sys.exit(1)

    def _cmd_chat(self, args):
        """Start a chat session."""
        model = args.model
        logger.info(f"Starting chat with model: {model}")
        
        # Validate mode
        if self.mode == "offline" and not self.ollama_client.is_model_available(model):
            print(f"Error: Model '{model}' not available in offline mode")
            sys.exit(1)
        
        # Start chat session
        session_id = self.transcript_manager.new_session(model)
        print(f"Starting chat with {model} (session: {session_id})")
        print("Type '/exit' to quit, '/save' to export transcript\n")
        
        self.ollama_client.chat_interactive(model, self.transcript_manager, session_id)

    def _cmd_list(self, args):
        """List available models."""
        print("Available models:")
        models = self.ollama_client.list_models()
        for model in models:
            size_gb = model.get("size", 0) / (1024**3)
            print(f"  - {model['name']} ({size_gb:.2f} GB)")

    def _cmd_pull(self, args):
        """Pull a new model."""
        model = args.model
        logger.info(f"Pulling model: {model}")
        print(f"Pulling model: {model}")
        self.ollama_client.pull_model(model)
        print(f"Successfully pulled: {model}")

    def _cmd_delete(self, args):
        """Delete a model."""
        model = args.model
        logger.info(f"Deleting model: {model}")
        
        if not args.force:
            response = input(f"Delete model '{model}'? (y/n): ")
            if response.lower() != 'y':
                print("Cancelled")
                return
        
        self.ollama_client.delete_model(model)
        print(f"Deleted: {model}")

    def _cmd_diff(self, args):
        """Show diff of files or sessions."""
        if args.sessions:
            # Compare two transcript sessions
            self.dev_utils.diff_sessions(
                args.sessions[0], 
                args.sessions[1],
                context=args.context
            )
        elif args.files:
            # Compare two files
            self.dev_utils.diff_files(
                args.files[0],
                args.files[1],
                context=args.context
            )
        else:
            print("Error: Specify --sessions or --files")
            sys.exit(1)

    def _cmd_scaffold(self, args):
        """Quick scaffold a project structure."""
        template = args.template
        output_dir = args.output or "."
        
        logger.info(f"Scaffolding {template} to {output_dir}")
        self.dev_utils.scaffold_project(template, output_dir, args.name)
        print(f"Scaffolded {template} project to: {output_dir}")

    def _cmd_export(self, args):
        """Export transcript session."""
        session_id = args.session
        output_file = args.output
        
        logger.info(f"Exporting session {session_id} to {output_file}")
        self.transcript_manager.export_session(session_id, output_file, format=args.format)
        print(f"Exported session {session_id} to: {output_file}")

    def _cmd_mode(self, args):
        """Switch between online/offline modes."""
        if args.set:
            self.mode = args.set
            logger.info(f"Mode set to: {self.mode}")
            print(f"Mode: {self.mode}")
        else:
            print(f"Current mode: {self.mode}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Ollie CLI - Terminal interface for local LLMs via Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"Ollie CLI v{__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start interactive chat")
    chat_parser.add_argument("model", help="Model name to chat with")
    
    # List command
    subparsers.add_parser("list", help="List available models")
    
    # Pull command
    pull_parser = subparsers.add_parser("pull", help="Pull a new model")
    pull_parser.add_argument("model", help="Model name to pull")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a model")
    delete_parser.add_argument("model", help="Model name to delete")
    delete_parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation")
    
    # Diff command
    diff_parser = subparsers.add_parser("diff", help="Show diff view")
    diff_parser.add_argument("--sessions", nargs=2, help="Compare two session IDs")
    diff_parser.add_argument("--files", nargs=2, help="Compare two files")
    diff_parser.add_argument("--context", "-c", type=int, default=3, help="Context lines")
    
    # Scaffold command
    scaffold_parser = subparsers.add_parser("scaffold", help="Quick project scaffolding")
    scaffold_parser.add_argument("template", choices=["python", "node", "web", "api"], help="Project template")
    scaffold_parser.add_argument("--name", "-n", required=True, help="Project name")
    scaffold_parser.add_argument("--output", "-o", help="Output directory")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export transcript session")
    export_parser.add_argument("session", help="Session ID to export")
    export_parser.add_argument("--output", "-o", required=True, help="Output file")
    export_parser.add_argument("--format", "-f", choices=["txt", "json", "md"], default="txt", help="Export format")
    
    # Mode command
    mode_parser = subparsers.add_parser("mode", help="Manage online/offline mode")
    mode_parser.add_argument("--set", choices=["online", "offline"], help="Set mode")
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Commands that don't need Ollama validation
    no_ollama_commands = {"diff", "scaffold", "export"}
    
    # Initialize Ollie CLI
    skip_check = hasattr(args, 'command') and args.command in no_ollama_commands
    cli = OllieCLI(skip_ollama_check=skip_check)
    
    # Check if command was provided
    if args.command:
        cli.run_command(args)
    else:
        # No command - run interactive UI
        cli.run_interactive()


if __name__ == "__main__":
    main()
