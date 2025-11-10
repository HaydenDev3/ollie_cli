"""
UI Module - Curses-based terminal UI for Ollie CLI

Provides interactive terminal interface for model management and chat.
"""

import curses
import logging
import platform
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ollie import OllieCLI


logger = logging.getLogger(__name__)


class OllieUI:
    """Curses-based terminal UI."""

    def __init__(self, cli_app: 'OllieCLI'):
        """
        Initialize UI.
        
        Args:
            cli_app: Main OllieCLI instance
        """
        self.cli_app = cli_app
        self.models = []
        self.selected_idx = 0
        self.status_msg = ""

    def run(self, stdscr):
        """
        Main UI loop.
        
        Args:
            stdscr: Curses screen object
        """
        self.stdscr = stdscr
        
        # Setup curses
        curses.curs_set(0)  # Hide cursor
        stdscr.clear()
        
        # Initialize colors if available
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
        
        # Load models
        self._refresh_models()
        
        # Main loop
        while True:
            try:
                self._draw_ui()
                
                # Get user input
                key = stdscr.getch()
                
                if not self._handle_input(key):
                    break
                    
            except curses.error as e:
                logger.error(f"Curses error: {e}")
                continue
            except KeyboardInterrupt:
                break

    def _draw_ui(self):
        """Draw the UI."""
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()
        
        # Title
        title = "Ollie CLI - Ollama Model Manager"
        mode_indicator = f"[{self.cli_app.mode.upper()}]"
        
        try:
            self.stdscr.addstr(0, 0, title, curses.A_BOLD | curses.color_pair(1))
            self.stdscr.addstr(0, width - len(mode_indicator) - 1, mode_indicator, curses.color_pair(2))
        except curses.error:
            pass
        
        # Separator
        try:
            self.stdscr.addstr(1, 0, "=" * (width - 1))
        except curses.error:
            pass
        
        # Models list
        start_line = 3
        
        if not self.models:
            try:
                self.stdscr.addstr(start_line, 2, "No models available. Press 'P' to pull a model.", curses.color_pair(3))
            except curses.error:
                pass
        else:
            try:
                self.stdscr.addstr(start_line, 0, "Available Models:", curses.A_BOLD)
            except curses.error:
                pass
            
            for idx, model in enumerate(self.models[:height - 10]):
                line = start_line + 2 + idx
                name = model.get("name", "unknown")
                size = model.get("size", 0)
                size_gb = size / (1024**3) if size > 0 else 0
                
                # Highlight selected
                attr = curses.A_REVERSE if idx == self.selected_idx else curses.A_NORMAL
                
                model_line = f"  {name}"
                if size_gb > 0:
                    model_line += f" ({size_gb:.2f} GB)"
                
                try:
                    self.stdscr.addstr(line, 2, model_line, attr)
                except curses.error:
                    pass
        
        # Help text
        help_line = height - 4
        help_texts = [
            "↑/↓: Navigate  ENTER: Chat  P: Pull  D: Delete  R: Refresh  M: Mode  Q: Quit"
        ]
        
        try:
            self.stdscr.addstr(help_line, 0, "─" * (width - 1))
            for i, text in enumerate(help_texts):
                self.stdscr.addstr(help_line + 1 + i, 2, text, curses.color_pair(2))
        except curses.error:
            pass
        
        # Status message
        if self.status_msg:
            try:
                self.stdscr.addstr(height - 1, 0, self.status_msg[:width-1], curses.color_pair(3))
            except curses.error:
                pass
        
        self.stdscr.refresh()

    def _handle_input(self, key) -> bool:
        """
        Handle keyboard input.
        
        Args:
            key: Key code
            
        Returns:
            True to continue, False to exit
        """
        # Navigation
        if key == curses.KEY_UP:
            self.selected_idx = max(0, self.selected_idx - 1)
            
        elif key == curses.KEY_DOWN:
            self.selected_idx = min(len(self.models) - 1, self.selected_idx + 1)
            
        # Actions
        elif key == ord('\n') or key == curses.KEY_ENTER:
            self._action_chat()
            
        elif key == ord('p') or key == ord('P'):
            self._action_pull()
            
        elif key == ord('d') or key == ord('D'):
            self._action_delete()
            
        elif key == ord('r') or key == ord('R'):
            self._action_refresh()
            
        elif key == ord('m') or key == ord('M'):
            self._action_toggle_mode()
            
        elif key == ord('q') or key == ord('Q'):
            return False
        
        # Handle resize
        elif key == curses.KEY_RESIZE:
            self.stdscr.clear()
        
        return True

    def _action_chat(self):
        """Start chat with selected model."""
        if not self.models or self.selected_idx >= len(self.models):
            self.status_msg = "No model selected"
            return
        
        model_name = self.models[self.selected_idx]["name"]
        
        # Suspend curses for interactive chat
        curses.def_prog_mode()
        curses.endwin()
        
        try:
            # Start chat
            session_id = self.cli_app.transcript_manager.new_session(model_name)
            print(f"\nStarting chat with {model_name}")
            print("Type '/exit' to quit, '/save' to export transcript\n")
            
            self.cli_app.ollama_client.chat_interactive(
                model_name,
                self.cli_app.transcript_manager,
                session_id
            )
            
        except Exception as e:
            print(f"\nChat error: {e}")
            input("\nPress Enter to continue...")
        finally:
            # Resume curses
            curses.reset_prog_mode()
            curses.curs_set(0)
            self.stdscr.clear()
            self.stdscr.refresh()

    def _action_pull(self):
        """Pull a new model."""
        # Suspend curses for input
        curses.def_prog_mode()
        curses.endwin()
        
        try:
            print("\n")
            model_name = input("Enter model name to pull (e.g., llama2, mistral): ").strip()
            
            if model_name:
                print(f"\nPulling {model_name}...")
                self.cli_app.ollama_client.pull_model(model_name)
                print(f"\nSuccessfully pulled: {model_name}")
                self._refresh_models()
            
            input("\nPress Enter to continue...")
            
        except Exception as e:
            print(f"\nError: {e}")
            input("\nPress Enter to continue...")
        finally:
            # Resume curses
            curses.reset_prog_mode()
            curses.curs_set(0)
            self.stdscr.clear()
            self.stdscr.refresh()

    def _action_delete(self):
        """Delete selected model."""
        if not self.models or self.selected_idx >= len(self.models):
            self.status_msg = "No model selected"
            return
        
        model_name = self.models[self.selected_idx]["name"]
        
        # Suspend curses for confirmation
        curses.def_prog_mode()
        curses.endwin()
        
        try:
            print("\n")
            confirm = input(f"Delete model '{model_name}'? (y/n): ").strip().lower()
            
            if confirm == 'y':
                print(f"\nDeleting {model_name}...")
                self.cli_app.ollama_client.delete_model(model_name)
                print(f"Deleted: {model_name}")
                self._refresh_models()
                if self.selected_idx >= len(self.models):
                    self.selected_idx = max(0, len(self.models) - 1)
            
            input("\nPress Enter to continue...")
            
        except Exception as e:
            print(f"\nError: {e}")
            input("\nPress Enter to continue...")
        finally:
            # Resume curses
            curses.reset_prog_mode()
            curses.curs_set(0)
            self.stdscr.clear()
            self.stdscr.refresh()

    def _action_refresh(self):
        """Refresh models list."""
        self._refresh_models()
        self.status_msg = "Models refreshed"

    def _action_toggle_mode(self):
        """Toggle between online/offline modes."""
        if self.cli_app.mode == "online":
            self.cli_app.mode = "offline"
        else:
            self.cli_app.mode = "online"
        
        self.status_msg = f"Mode: {self.cli_app.mode}"
        logger.info(f"Mode switched to: {self.cli_app.mode}")

    def _refresh_models(self):
        """Refresh the list of available models."""
        try:
            self.models = self.cli_app.ollama_client.list_models()
            self.status_msg = f"Loaded {len(self.models)} models"
        except Exception as e:
            logger.error(f"Failed to refresh models: {e}")
            self.status_msg = f"Error loading models: {e}"
            self.models = []


def check_curses_support():
    """Check if curses is supported on this platform."""
    if platform.system() == "Windows":
        try:
            import curses
            return True
        except ImportError:
            print("\n" + "=" * 60)
            print("WINDOWS COMPATIBILITY NOTICE")
            print("=" * 60)
            print("\nOllie-CLI uses Python's curses library for terminal UI.")
            print("On Windows, you need to install windows-curses:\n")
            print("  pip install windows-curses\n")
            print("Alternatively, you can:")
            print("  - Use WSL (Windows Subsystem for Linux)")
            print("  - Use command-line mode without UI")
            print("=" * 60 + "\n")
            return False
    
    return True
