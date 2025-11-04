#!/usr/bin/env python3
"""
Ollie-CLI: Terminal interface for Ollama model management
"""

import curses
import logging
import os
import platform
import sys
from typing import Optional

import ollama


# Set up logging
def setup_logging():
    """Configure file-based logging."""
    logging.basicConfig(
        filename='ollie.log',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Also get a logger for this module
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Ollie-CLI starting")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info("=" * 60)
    return logger


logger = setup_logging()


def check_windows_compatibility():
    """Check if running on Windows and provide guidance."""
    if platform.system() == "Windows":
        print("\n" + "=" * 60)
        print("WINDOWS COMPATIBILITY NOTICE")
        print("=" * 60)
        print("\nOllie-CLI uses Python's curses library for terminal UI.")
        print("On Windows, curses support is limited.")
        print("\nRecommended options:")
        print("  1. Install windows-curses: pip install windows-curses")
        print("  2. Use WSL (Windows Subsystem for Linux)")
        print("  3. Use Git Bash or another Unix-like terminal")
        print("\nIf you've installed windows-curses, you can continue.")
        print("=" * 60 + "\n")

        response = input("Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            logger.info("User chose not to continue on Windows")
            sys.exit(0)
        logger.info("User continuing on Windows platform")


def validate_ollama():
    """Validate that Ollama CLI is available."""
    try:
        ollama.ensure_available()
        return True
    except ollama.OllamaError as e:
        print("\n" + "=" * 60)
        print("OLLAMA NOT FOUND")
        print("=" * 60)
        print(f"\n{str(e)}")
        print("\nPlease install Ollama from: https://ollama.ai/")
        print("\nAfter installation, ensure 'ollama' is in your PATH.")
        print("=" * 60 + "\n")
        logger.error(f"Ollama validation failed: {e}")
        return False


class OllieUI:
    """Curses-based UI for Ollama management."""

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.models = []
        self.selected_idx = 0
        self.status_msg = "Welcome to Ollie-CLI"

        # Store terminal mode for suspend/resume
        curses.curs_set(0)  # Hide cursor
        self.stdscr.keypad(True)
        self.stdscr.timeout(100)  # Non-blocking input with 100ms timeout

        # Initialize colors if available
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

        logger.info("UI initialized")

    def refresh_models(self):
        """Reload the list of models from Ollama."""
        try:
            self.models = ollama.list_models()
            self.status_msg = f"Loaded {len(self.models)} models"
            logger.info(f"Refreshed model list: {len(self.models)} models")

            # Adjust selection if out of bounds
            if self.selected_idx >= len(self.models):
                self.selected_idx = max(0, len(self.models) - 1)
        except ollama.OllamaError as e:
            self.status_msg = f"Error: {str(e)}"
            logger.error(f"Failed to refresh models: {e}")

    def draw_header(self):
        """Draw the header with title."""
        height, width = self.stdscr.getmaxyx()

        title = "=== OLLIE-CLI ==="
        subtitle = "Ollama Model Manager"

        try:
            if height > 0 and width > len(title):
                self.stdscr.addstr(0, (width - len(title)) // 2, title,
                                   curses.color_pair(1) | curses.A_BOLD if curses.has_colors() else curses.A_BOLD)
            if height > 1 and width > len(subtitle):
                self.stdscr.addstr(1, (width - len(subtitle)) // 2, subtitle,
                                   curses.color_pair(1) if curses.has_colors() else 0)
        except curses.error:
            pass  # Ignore errors from writing outside window

    def draw_models(self):
        """Draw the list of models."""
        height, width = self.stdscr.getmaxyx()
        start_y = 3

        if height <= start_y:
            return

        try:
            # Header for model list
            if height > start_y and width > 10:
                self.stdscr.addstr(start_y, 2, "Models:",
                                   curses.color_pair(2) | curses.A_BOLD if curses.has_colors() else curses.A_BOLD)
        except curses.error:
            pass

        # Draw each model
        for idx, model in enumerate(self.models):
            y = start_y + 2 + idx
            if y >= height - 3:  # Leave room for status and help
                break

            model_name = model.get("name", "unknown")
            model_size = model.get("size", "")

            # Truncate if too long
            max_len = width - 6
            display_text = f"{model_name} ({model_size})"
            if len(display_text) > max_len:
                display_text = display_text[:max_len - 3] + "..."

            try:
                if idx == self.selected_idx:
                    # Highlight selected model
                    self.stdscr.addstr(y, 2, f"> {display_text}",
                                       curses.color_pair(2) | curses.A_REVERSE if curses.has_colors() else curses.A_REVERSE)
                else:
                    self.stdscr.addstr(y, 2, f"  {display_text}")
            except curses.error:
                pass

    def draw_status(self):
        """Draw status message at bottom."""
        height, width = self.stdscr.getmaxyx()

        if height <= 2:
            return

        try:
            # Status line
            status_y = height - 2
            status_text = self.status_msg[:width - 4]
            if status_y > 0 and width > 4:
                self.stdscr.addstr(status_y, 2, status_text,
                                   curses.color_pair(3) if curses.has_colors() else 0)
        except curses.error:
            pass

    def draw_help(self):
        """Draw help text at bottom."""
        height, width = self.stdscr.getmaxyx()

        if height <= 1:
            return

        help_text = "↑/↓:Select  ENTER:Chat  P:Pull  D:Delete  R:Refresh  Q:Quit"

        try:
            help_y = height - 1
            if help_y > 0 and width > len(help_text):
                self.stdscr.addstr(help_y, (width - len(help_text)) // 2, help_text,
                                   curses.color_pair(1) if curses.has_colors() else 0)
        except curses.error:
            pass

    def draw(self):
        """Draw the entire UI."""
        self.stdscr.clear()
        self.draw_header()
        self.draw_models()
        self.draw_status()
        self.draw_help()
        self.stdscr.refresh()

    def suspend_curses(self):
        """Suspend curses for running external commands."""
        curses.def_prog_mode()  # Save current terminal mode
        curses.endwin()         # End curses mode

    def resume_curses(self):
        """Resume curses after external command."""
        curses.reset_prog_mode()  # Restore saved terminal mode
        curses.curs_set(0)        # Hide cursor again
        self.stdscr.clear()
        self.stdscr.refresh()

    def prompt_input(self, prompt: str) -> Optional[str]:
        """
        Prompt for text input from the user.
        Properly handles input without curses.doupdate misuse.
        """
        height, width = self.stdscr.getmaxyx()

        if height <= 3:
            return None

        prompt_y = height - 3

        try:
            # Clear the input line
            self.stdscr.move(prompt_y, 0)
            self.stdscr.clrtoeol()

            # Show prompt
            self.stdscr.addstr(prompt_y, 2, prompt, curses.A_BOLD)
            self.stdscr.refresh()

            # Enable cursor and echo
            curses.curs_set(1)
            curses.echo()

            # Get input
            input_x = 2 + len(prompt) + 1
            self.stdscr.move(prompt_y, input_x)
            self.stdscr.refresh()

            # Read input
            user_input = self.stdscr.getstr(prompt_y, input_x, width - input_x - 2).decode('utf-8')

            # Disable cursor and echo
            curses.noecho()
            curses.curs_set(0)

            # Clear the input line
            self.stdscr.move(prompt_y, 0)
            self.stdscr.clrtoeol()
            self.stdscr.refresh()

            return user_input.strip()

        except Exception as e:
            logger.error(f"Error in prompt_input: {e}")
            curses.noecho()
            curses.curs_set(0)
            return None

    def handle_chat(self):
        """Start chat with selected model."""
        if not self.models or self.selected_idx >= len(self.models):
            self.status_msg = "No model selected"
            return

        model_name = self.models[self.selected_idx].get("name", "")
        logger.info(f"Starting chat with {model_name}")

        # Suspend curses
        self.suspend_curses()

        try:
            print(f"\n{'='*60}")
            print(f"Starting chat with {model_name}")
            print(f"Type your messages and press Enter. Use /bye to exit.")
            print(f"{'='*60}\n")

            # Run chat
            ollama.run_chat(model_name)

            print(f"\n{'='*60}")
            print("Chat ended. Press Enter to return to Ollie-CLI...")
            print(f"{'='*60}")
            input()

        except Exception as e:
            print(f"\nError during chat: {e}")
            logger.error(f"Chat error: {e}")
            input("Press Enter to continue...")
        finally:
            # Resume curses
            self.resume_curses()
            self.status_msg = f"Chat with {model_name} ended"

    def handle_pull(self):
        """Pull a new model."""
        model_name = self.prompt_input("Model to pull: ")

        if not model_name:
            self.status_msg = "Pull cancelled"
            return

        logger.info(f"Pulling model: {model_name}")

        # Suspend curses
        self.suspend_curses()

        try:
            print(f"\n{'='*60}")
            print(f"Pulling model: {model_name}")
            print(f"{'='*60}\n")

            # Pull model with streaming
            ollama.pull_model(model_name, stream=True)

            print(f"\n{'='*60}")
            print(f"Model {model_name} pulled successfully!")
            print("Press Enter to return to Ollie-CLI...")
            print(f"{'='*60}")
            input()

            self.status_msg = f"Pulled {model_name}"

        except ollama.OllamaError as e:
            print(f"\nError: {e}")
            logger.error(f"Pull error: {e}")
            input("Press Enter to continue...")
            self.status_msg = f"Failed to pull {model_name}"
        finally:
            # Resume curses
            self.resume_curses()
            # Refresh model list
            self.refresh_models()

    def handle_delete(self):
        """Delete the selected model."""
        if not self.models or self.selected_idx >= len(self.models):
            self.status_msg = "No model selected"
            return

        model_name = self.models[self.selected_idx].get("name", "")

        # Confirm deletion
        confirm = self.prompt_input(f"Delete {model_name}? (y/n): ")

        if confirm and confirm.lower() == 'y':
            logger.info(f"Deleting model: {model_name}")

            try:
                ollama.delete_model(model_name)
                self.status_msg = f"Deleted {model_name}"
                self.refresh_models()
            except ollama.OllamaError as e:
                self.status_msg = f"Error: {str(e)}"
                logger.error(f"Delete error: {e}")
        else:
            self.status_msg = "Delete cancelled"

    def handle_resize(self):
        """Handle terminal resize."""
        try:
            curses.endwin()
            self.stdscr.refresh()
            logger.info("Terminal resized")
        except Exception as e:
            logger.error(f"Resize error: {e}")

    def run(self):
        """Main UI loop."""
        # Initial model refresh
        self.refresh_models()

        while True:
            self.draw()

            try:
                key = self.stdscr.getch()

                if key == -1:  # No input (timeout)
                    continue
                elif key == ord('q') or key == ord('Q'):
                    logger.info("User quit application")
                    break
                elif key == ord('r') or key == ord('R'):
                    self.status_msg = "Refreshing..."
                    self.refresh_models()
                elif key == curses.KEY_UP:
                    if self.models:
                        self.selected_idx = (self.selected_idx - 1) % len(self.models)
                elif key == curses.KEY_DOWN:
                    if self.models:
                        self.selected_idx = (self.selected_idx + 1) % len(self.models)
                elif key == ord('\n') or key == 10:  # 10 is Enter key
                    self.handle_chat()
                elif key == ord('p') or key == ord('P'):
                    self.handle_pull()
                elif key == ord('d') or key == ord('D'):
                    self.handle_delete()
                elif key == curses.KEY_RESIZE:
                    self.handle_resize()

            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                self.status_msg = f"Error: {str(e)}"


def main(stdscr):
    """Main entry point for curses application."""
    try:
        ui = OllieUI(stdscr)
        ui.run()
    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    # Check Windows compatibility
    check_windows_compatibility()

    # Validate Ollama presence
    if not validate_ollama():
        sys.exit(1)

    try:
        # Start curses application
        curses.wrapper(main)
        logger.info("Application exited normally")
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\nExiting...")
    except Exception as e:
        logger.error(f"Application crashed: {e}", exc_info=True)
        print(f"\nError: {e}")
        print("Check ollie.log for details.")
        sys.exit(1)
