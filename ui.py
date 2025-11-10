"""
UI Module - Retro CRT-style terminal interface with neon visual elements.

Provides terminal styling, colors, and visual effects for Ollie CLI.
"""

import sys
import shutil
from datetime import datetime


class UI:
    """UI class for retro-themed terminal interface."""
    
    # ANSI color codes for retro neon theme
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m',
        
        # Neon colors
        'neon_green': '\033[38;5;46m',
        'neon_pink': '\033[38;5;201m',
        'neon_cyan': '\033[38;5;51m',
        'neon_yellow': '\033[38;5;226m',
        'neon_orange': '\033[38;5;208m',
        'neon_purple': '\033[38;5;165m',
        
        # Standard colors
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'gray': '\033[90m',
    }
    
    # Special effects
    GLOW_CHAR = '▓'
    BORDER_CHARS = {
        'h': '═',
        'v': '║',
        'tl': '╔',
        'tr': '╗',
        'bl': '╚',
        'br': '╝',
    }
    
    def __init__(self):
        """Initialize UI."""
        self.terminal_width = self._get_terminal_width()
        self.use_colors = self._supports_color()
    
    def _get_terminal_width(self):
        """Get terminal width."""
        try:
            return shutil.get_terminal_size().columns
        except Exception:
            return 80
    
    def _supports_color(self):
        """Check if terminal supports colors."""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    def colorize(self, text, color='reset'):
        """Apply color to text."""
        if not self.use_colors:
            return text
        
        color_code = self.COLORS.get(color, self.COLORS['reset'])
        return f"{color_code}{text}{self.COLORS['reset']}"
    
    def glow_text(self, text, color='neon_cyan'):
        """Apply glow effect to text."""
        if not self.use_colors:
            return text
        
        return f"{self.COLORS['bold']}{self.colorize(text, color)}"
    
    def print_banner(self, text, color='neon_cyan', width=None):
        """Print a banner with border."""
        width = width or self.terminal_width
        
        # Create border
        top_border = f"{self.BORDER_CHARS['tl']}{self.BORDER_CHARS['h'] * (width - 2)}{self.BORDER_CHARS['tr']}"
        bottom_border = f"{self.BORDER_CHARS['bl']}{self.BORDER_CHARS['h'] * (width - 2)}{self.BORDER_CHARS['br']}"
        
        # Center text
        padding = (width - 4 - len(text)) // 2
        text_line = f"{self.BORDER_CHARS['v']} {' ' * padding}{text}{' ' * (width - 4 - padding - len(text))} {self.BORDER_CHARS['v']}"
        
        # Print with color
        print(self.colorize(top_border, color))
        print(self.glow_text(text_line, color))
        print(self.colorize(bottom_border, color))
    
    def show_welcome(self):
        """Display welcome screen with retro ASCII art."""
        welcome_art = r"""
   ____  _     _     _        ____ _     ___ 
  / __ \| |   | |   (_) ___  / ___| |   |_ _|
 | |  | | |   | |   | |/ _ \| |   | |    | | 
 | |  | | |___| |___| |  __/| |___| |___ | | 
 | |__| |_____|_____|_|\___| \____|_____|___|
  \____/                                      
        """
        
        # Print ASCII art with glow effect
        for line in welcome_art.split('\n'):
            print(self.glow_text(line, 'neon_cyan'))
        
        # Print tagline
        tagline = "⚡ A Retro-Themed Terminal Chat with Ollama ⚡"
        print(self.glow_text(tagline.center(self.terminal_width), 'neon_pink'))
        print()
        
        # Print separator
        separator = self.GLOW_CHAR * self.terminal_width
        print(self.colorize(separator, 'neon_purple'))
        print()
        
        # Print quick start info
        self.print_info("Type /help for commands or start chatting!")
        self.print_info(f"Session started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    def get_user_input(self):
        """Get user input with styled prompt."""
        prompt = self.glow_text("┃ You ▸ ", 'neon_green')
        try:
            return input(prompt)
        except (KeyboardInterrupt, EOFError):
            raise
    
    def print_ai_prefix(self):
        """Print AI response prefix."""
        prefix = self.glow_text("┃ Ollie ▸ ", 'neon_cyan')
        print(prefix, end='', flush=True)
    
    def print_success(self, message):
        """Print success message."""
        icon = "✓"
        print(self.colorize(f"{icon} {message}", 'green'))
    
    def print_error(self, message):
        """Print error message."""
        icon = "✗"
        print(self.colorize(f"{icon} {message}", 'red'))
    
    def print_warning(self, message):
        """Print warning message."""
        icon = "⚠"
        print(self.colorize(f"{icon} {message}", 'yellow'))
    
    def print_info(self, message):
        """Print info message."""
        icon = "ℹ"
        print(self.colorize(f"{icon} {message}", 'cyan'))
    
    def print_section(self, title):
        """Print section header."""
        separator = '─' * (self.terminal_width - 4)
        print()
        print(self.glow_text(f"┏━ {title} ", 'neon_pink'))
        print(self.colorize(f"┃ {separator}", 'neon_pink'))
    
    def print_code_block(self, code, language=''):
        """Print code block with syntax highlighting."""
        border = '─' * (self.terminal_width - 4)
        print(self.colorize(f"┌─[{language}]─{border}", 'gray'))
        
        for line in code.split('\n'):
            print(self.colorize(f"│ {line}", 'white'))
        
        print(self.colorize(f"└─{border}", 'gray'))
    
    def print_diff_line(self, line, line_type):
        """Print a diff line with appropriate color."""
        if line_type == 'add':
            print(self.colorize(f"+ {line}", 'green'))
        elif line_type == 'remove':
            print(self.colorize(f"- {line}", 'red'))
        elif line_type == 'context':
            print(self.colorize(f"  {line}", 'gray'))
        elif line_type == 'header':
            print(self.glow_text(f"@@ {line}", 'neon_cyan'))
        else:
            print(line)
    
    def print_list_item(self, text, level=0):
        """Print a list item with indentation."""
        indent = '  ' * level
        bullet = '▸'
        print(self.colorize(f"{indent}{bullet} {text}", 'cyan'))
    
    def show_progress_bar(self, current, total, label=''):
        """Show a progress bar."""
        bar_length = min(50, self.terminal_width - 20)
        filled_length = int(bar_length * current // total)
        bar = self.GLOW_CHAR * filled_length + '░' * (bar_length - filled_length)
        percent = 100 * current / total
        
        progress_line = f"\r{label} |{bar}| {percent:.1f}%"
        print(self.colorize(progress_line, 'neon_green'), end='', flush=True)
        
        if current >= total:
            print()  # New line when complete
    
    def clear_screen(self):
        """Clear the terminal screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_table(self, headers, rows):
        """Print a formatted table."""
        if not rows:
            return
        
        # Calculate column widths
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Print header
        header_line = ' │ '.join(
            self.glow_text(headers[i].ljust(col_widths[i]), 'neon_cyan')
            for i in range(len(headers))
        )
        print(f"┌─{header_line}─┐")
        
        # Print separator
        separator = '─┼─'.join('─' * w for w in col_widths)
        print(self.colorize(f"├─{separator}─┤", 'gray'))
        
        # Print rows
        for row in rows:
            row_line = ' │ '.join(
                str(row[i]).ljust(col_widths[i])
                for i in range(len(row))
            )
            print(f"│ {row_line} │")
        
        # Print bottom border
        print(f"└─{'─' * (len(header_line) - 4)}─┘")
    
    def show_spinner(self, message='Loading'):
        """Show a loading spinner (would need threading for real animation)."""
        spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        # This is a simple static version; real animation would need threading
        print(self.colorize(f"{spinner_chars[0]} {message}...", 'neon_cyan'))
