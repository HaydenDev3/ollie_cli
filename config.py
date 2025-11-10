"""
Configuration Module - Manage Ollie CLI settings and preferences.

Handles configuration loading, saving, and default settings.
"""

import json
from pathlib import Path


class Config:
    """Configuration management for Ollie CLI."""
    
    DEFAULT_CONFIG = {
        'default_model': 'llama2',
        'max_context_length': 4096,
        'temperature': 0.7,
        'sessions_dir': '~/.ollie/sessions',
        'config_dir': '~/.ollie',
        'theme': 'retro',
        'auto_save_sessions': True,
        'show_timestamps': True,
    }
    
    def __init__(self):
        """Initialize configuration."""
        self.config_dir = Path.home() / '.ollie'
        self.config_file = self.config_dir / 'config.json'
        self.sessions_dir = self.config_dir / 'sessions'
        
        # Create directories if they don't exist
        self._ensure_directories()
        
        # Load or create config
        self.config = self._load_config()
    
    def _ensure_directories(self):
        """Ensure config and session directories exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self):
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                
                # Merge with defaults (in case new keys were added)
                config = self.DEFAULT_CONFIG.copy()
                config.update(loaded_config)
                return config
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def _save_config(self, config=None):
        """Save configuration to file."""
        config = config or self.config
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save config: {e}")
    
    def get(self, key, default=None):
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set a configuration value."""
        self.config[key] = value
        self._save_config()
    
    def get_config_dir(self):
        """Get config directory path."""
        return self.config_dir
    
    def get_sessions_dir(self):
        """Get sessions directory path."""
        return self.sessions_dir
    
    def list_sessions(self):
        """List saved session files."""
        try:
            session_files = list(self.sessions_dir.glob('session_*.json'))
            return sorted(session_files, key=lambda x: x.stat().st_mtime, reverse=True)
        except Exception:
            return []
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self.config = self.DEFAULT_CONFIG.copy()
        self._save_config()
    
    def show_config(self):
        """Display current configuration."""
        print("\n=== Current Configuration ===")
        for key, value in self.config.items():
            print(f"  {key}: {value}")
        print(f"\nConfig file: {self.config_file}")
        print(f"Sessions dir: {self.sessions_dir}")
