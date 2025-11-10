"""
Utilities Module - Helper functions for diff-view, scaffolding, and other tools.

Provides developer utilities and quality-of-life features.
"""

import os
import difflib
from pathlib import Path
from datetime import datetime


class Utils:
    """Utility functions for Ollie CLI."""
    
    # Scaffold templates
    SCAFFOLD_TEMPLATES = {
        'python': {
            'files': {
                'main.py': '#!/usr/bin/env python3\n"""Main application file."""\n\ndef main():\n    """Main entry point."""\n    print("Hello, World!")\n\nif __name__ == "__main__":\n    main()\n',
                'README.md': '# New Python Project\n\nCreated with Ollie CLI\n\n## Installation\n\n```bash\npython main.py\n```\n',
                'requirements.txt': '# Add your dependencies here\n',
                '.gitignore': '__pycache__/\n*.pyc\n*.pyo\n*.pyd\n.Python\n*.so\n*.egg\n*.egg-info/\ndist/\nbuild/\n',
            }
        },
        'node': {
            'files': {
                'index.js': 'console.log("Hello, World!");\n',
                'package.json': '{\n  "name": "new-project",\n  "version": "1.0.0",\n  "description": "Created with Ollie CLI",\n  "main": "index.js",\n  "scripts": {\n    "start": "node index.js"\n  }\n}\n',
                'README.md': '# New Node.js Project\n\nCreated with Ollie CLI\n\n## Installation\n\n```bash\nnpm install\nnpm start\n```\n',
                '.gitignore': 'node_modules/\n*.log\n.env\n',
            }
        },
        'web': {
            'files': {
                'index.html': '<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>New Web Project</title>\n    <link rel="stylesheet" href="style.css">\n</head>\n<body>\n    <h1>Hello, World!</h1>\n    <script src="script.js"></script>\n</body>\n</html>\n',
                'style.css': '* {\n    margin: 0;\n    padding: 0;\n    box-sizing: border-box;\n}\n\nbody {\n    font-family: Arial, sans-serif;\n    display: flex;\n    justify-content: center;\n    align-items: center;\n    min-height: 100vh;\n    background: #1a1a1a;\n    color: #fff;\n}\n',
                'script.js': 'console.log("Hello, World!");\n',
                'README.md': '# New Web Project\n\nCreated with Ollie CLI\n\n## Usage\n\nOpen `index.html` in your browser.\n',
            }
        },
        'go': {
            'files': {
                'main.go': 'package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello, World!")\n}\n',
                'go.mod': 'module example.com/newproject\n\ngo 1.21\n',
                'README.md': '# New Go Project\n\nCreated with Ollie CLI\n\n## Build & Run\n\n```bash\ngo run main.go\n```\n',
                '.gitignore': '*.exe\n*.exe~\n*.dll\n*.so\n*.dylib\n',
            }
        },
    }
    
    def __init__(self, config):
        """Initialize utilities with config."""
        self.config = config
    
    def show_diff(self, file1, file2):
        """Show diff between two files."""
        try:
            # Read files
            with open(file1, 'r', encoding='utf-8') as f:
                file1_lines = f.readlines()
            
            with open(file2, 'r', encoding='utf-8') as f:
                file2_lines = f.readlines()
            
            # Generate diff
            diff = difflib.unified_diff(
                file1_lines,
                file2_lines,
                fromfile=file1,
                tofile=file2,
                lineterm=''
            )
            
            # Import UI for colored output
            from ui import UI
            ui = UI()
            
            # Print diff header
            ui.print_section(f"Diff: {file1} ↔ {file2}")
            
            # Print diff lines
            for line in diff:
                line = line.rstrip()
                if line.startswith('+++') or line.startswith('---'):
                    ui.print_diff_line(line, 'header')
                elif line.startswith('+'):
                    ui.print_diff_line(line[1:], 'add')
                elif line.startswith('-'):
                    ui.print_diff_line(line[1:], 'remove')
                elif line.startswith('@@'):
                    ui.print_diff_line(line, 'header')
                else:
                    ui.print_diff_line(line[1:] if line else '', 'context')
            
            print()
            
        except FileNotFoundError as e:
            from ui import UI
            UI().print_error(f"File not found: {e}")
        except Exception as e:
            from ui import UI
            UI().print_error(f"Error generating diff: {e}")
    
    def scaffold_project(self, project_type):
        """Create a new project scaffold."""
        project_type = project_type.lower()
        
        if project_type not in self.SCAFFOLD_TEMPLATES:
            from ui import UI
            ui = UI()
            ui.print_error(f"Unknown project type: {project_type}")
            ui.print_info(f"Available types: {', '.join(self.SCAFFOLD_TEMPLATES.keys())}")
            return
        
        # Get project name
        from ui import UI
        ui = UI()
        
        project_name = input(ui.colorize("Project name: ", 'cyan')).strip()
        if not project_name:
            project_name = f"new-{project_type}-project"
        
        # Create project directory
        project_dir = Path.cwd() / project_name
        
        if project_dir.exists():
            ui.print_error(f"Directory already exists: {project_dir}")
            return
        
        try:
            project_dir.mkdir(parents=True)
            
            # Create files from template
            template = self.SCAFFOLD_TEMPLATES[project_type]
            
            for filename, content in template['files'].items():
                file_path = project_dir / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            ui.print_success(f"Created {project_type} project: {project_name}")
            ui.print_info(f"Location: {project_dir}")
            
            # List created files
            print()
            ui.print_section("Created Files")
            for filename in template['files'].keys():
                ui.print_list_item(filename)
            print()
            
        except Exception as e:
            ui.print_error(f"Failed to create project: {e}")
    
    def format_timestamp(self, iso_timestamp):
        """Format ISO timestamp to readable string."""
        try:
            dt = datetime.fromisoformat(iso_timestamp)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return iso_timestamp
    
    def get_file_info(self, filepath):
        """Get file information."""
        try:
            path = Path(filepath)
            if not path.exists():
                return None
            
            stat = path.stat()
            return {
                'name': path.name,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'is_file': path.is_file(),
                'is_dir': path.is_dir(),
            }
        except Exception:
            return None
    
    def search_files(self, directory, pattern='*'):
        """Search for files matching pattern."""
        try:
            path = Path(directory)
            if not path.exists():
                return []
            
            return list(path.rglob(pattern))
        except Exception:
            return []
    
    def count_tokens_estimate(self, text):
        """Rough estimate of token count (words * 1.3)."""
        words = len(text.split())
        return int(words * 1.3)
    
    def truncate_text(self, text, max_length=100, suffix='...'):
        """Truncate text to max length."""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    def validate_file_path(self, filepath):
        """Validate if file path is accessible."""
        try:
            path = Path(filepath)
            return path.exists() and path.is_file()
        except Exception:
            return False
    
    def get_project_stats(self, directory='.'):
        """Get basic project statistics."""
        try:
            path = Path(directory)
            stats = {
                'files': 0,
                'directories': 0,
                'python_files': 0,
                'javascript_files': 0,
                'total_lines': 0,
            }
            
            for item in path.rglob('*'):
                if item.is_file():
                    stats['files'] += 1
                    
                    if item.suffix == '.py':
                        stats['python_files'] += 1
                    elif item.suffix in ['.js', '.jsx', '.ts', '.tsx']:
                        stats['javascript_files'] += 1
                    
                    # Count lines
                    try:
                        with open(item, 'r', encoding='utf-8') as f:
                            stats['total_lines'] += sum(1 for _ in f)
                    except Exception:
                        pass
                        
                elif item.is_dir():
                    stats['directories'] += 1
            
            return stats
        except Exception:
            return None
