"""
Developer Utilities - Tools for developers using Ollie CLI

Provides diff viewing, project scaffolding, and other developer-focused features.
"""

import difflib
import logging
import os
import shutil
from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)


class DevUtils:
    """Developer utility functions."""

    def __init__(self):
        """Initialize developer utilities."""
        self.scaffold_templates = {
            "python": self._scaffold_python,
            "node": self._scaffold_node,
            "web": self._scaffold_web,
            "api": self._scaffold_api
        }

    def diff_files(self, file1: str, file2: str, context: int = 3):
        """
        Show unified diff between two files.
        
        Args:
            file1: Path to first file
            file2: Path to second file
            context: Number of context lines
        """
        try:
            with open(file1, 'r') as f1:
                lines1 = f1.readlines()
            
            with open(file2, 'r') as f2:
                lines2 = f2.readlines()
            
            diff = difflib.unified_diff(
                lines1,
                lines2,
                fromfile=file1,
                tofile=file2,
                lineterm='',
                n=context
            )
            
            # Print with color if terminal supports it
            for line in diff:
                if line.startswith('+'):
                    print(f"\033[32m{line}\033[0m")  # Green
                elif line.startswith('-'):
                    print(f"\033[31m{line}\033[0m")  # Red
                elif line.startswith('@'):
                    print(f"\033[36m{line}\033[0m")  # Cyan
                else:
                    print(line)
                    
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            print(f"Error: File not found - {e}")
        except Exception as e:
            logger.exception("Error in diff_files")
            print(f"Error: {e}")

    def diff_sessions(self, session1_id: str, session2_id: str, context: int = 3):
        """
        Show diff between two transcript sessions.
        
        Args:
            session1_id: First session ID
            session2_id: Second session ID
            context: Number of context lines
        """
        from transcript import TranscriptManager
        
        tm = TranscriptManager()
        
        # Get sessions
        s1 = tm.get_session(session1_id)
        s2 = tm.get_session(session2_id)
        
        if not s1:
            print(f"Error: Session {session1_id} not found")
            return
        
        if not s2:
            print(f"Error: Session {session2_id} not found")
            return
        
        # Convert to text
        text1 = self._session_to_text(s1)
        text2 = self._session_to_text(s2)
        
        # Show diff
        diff = difflib.unified_diff(
            text1.splitlines(keepends=True),
            text2.splitlines(keepends=True),
            fromfile=f"Session {session1_id}",
            tofile=f"Session {session2_id}",
            lineterm='',
            n=context
        )
        
        for line in diff:
            if line.startswith('+'):
                print(f"\033[32m{line}\033[0m")
            elif line.startswith('-'):
                print(f"\033[31m{line}\033[0m")
            elif line.startswith('@'):
                print(f"\033[36m{line}\033[0m")
            else:
                print(line)

    def _session_to_text(self, session_data: dict) -> str:
        """Convert session data to text format."""
        lines = []
        for msg in session_data.get("messages", []):
            role = msg["role"].upper()
            content = msg["content"]
            lines.append(f"{role}: {content}")
        return "\n".join(lines)

    def scaffold_project(self, template: str, output_dir: str, name: str):
        """
        Scaffold a new project from template.
        
        Args:
            template: Template name (python, node, web, api)
            output_dir: Output directory
            name: Project name
        """
        if template not in self.scaffold_templates:
            raise ValueError(f"Unknown template: {template}")
        
        # Create output directory
        project_path = Path(output_dir) / name
        project_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Scaffolding {template} project: {name} at {project_path}")
        
        # Execute template function
        self.scaffold_templates[template](project_path, name)
        
        print(f"✓ Created {template} project: {name}")

    def _scaffold_python(self, project_path: Path, name: str):
        """Scaffold a Python project."""
        # Create directory structure
        (project_path / name).mkdir(exist_ok=True)
        (project_path / "tests").mkdir(exist_ok=True)
        
        # Create __init__.py
        (project_path / name / "__init__.py").write_text(
            f'"""{name} - A Python project"""\n\n__version__ = "0.1.0"\n'
        )
        
        # Create main.py
        (project_path / name / "main.py").write_text(
            '"""Main module."""\n\n'
            'def main():\n'
            '    """Main entry point."""\n'
            '    print("Hello from {name}!")\n\n'
            'if __name__ == "__main__":\n'
            '    main()\n'.format(name=name)
        )
        
        # Create requirements.txt
        (project_path / "requirements.txt").write_text("")
        
        # Create README.md
        (project_path / "README.md").write_text(
            f"# {name}\n\n"
            f"A Python project scaffolded by Ollie CLI.\n\n"
            f"## Installation\n\n"
            f"```bash\n"
            f"pip install -r requirements.txt\n"
            f"```\n\n"
            f"## Usage\n\n"
            f"```bash\n"
            f"python -m {name}.main\n"
            f"```\n"
        )
        
        # Create .gitignore
        (project_path / ".gitignore").write_text(
            "__pycache__/\n"
            "*.py[cod]\n"
            "*$py.class\n"
            "*.so\n"
            ".Python\n"
            "build/\n"
            "develop-eggs/\n"
            "dist/\n"
            "eggs/\n"
            ".eggs/\n"
            "*.egg-info/\n"
            "*.egg\n"
            ".venv/\n"
            "venv/\n"
        )

    def _scaffold_node(self, project_path: Path, name: str):
        """Scaffold a Node.js project."""
        # Create directory structure
        (project_path / "src").mkdir(exist_ok=True)
        
        # Create package.json
        (project_path / "package.json").write_text(
            '{\n'
            f'  "name": "{name}",\n'
            '  "version": "0.1.0",\n'
            f'  "description": "{name} - A Node.js project",\n'
            '  "main": "src/index.js",\n'
            '  "scripts": {\n'
            '    "start": "node src/index.js"\n'
            '  },\n'
            '  "keywords": [],\n'
            '  "author": "",\n'
            '  "license": "MIT"\n'
            '}\n'
        )
        
        # Create src/index.js
        (project_path / "src" / "index.js").write_text(
            f"console.log('Hello from {name}!');\n"
        )
        
        # Create README.md
        (project_path / "README.md").write_text(
            f"# {name}\n\n"
            f"A Node.js project scaffolded by Ollie CLI.\n\n"
            f"## Installation\n\n"
            f"```bash\n"
            f"npm install\n"
            f"```\n\n"
            f"## Usage\n\n"
            f"```bash\n"
            f"npm start\n"
            f"```\n"
        )
        
        # Create .gitignore
        (project_path / ".gitignore").write_text(
            "node_modules/\n"
            "*.log\n"
            ".env\n"
        )

    def _scaffold_web(self, project_path: Path, name: str):
        """Scaffold a basic web project."""
        # Create directory structure
        (project_path / "css").mkdir(exist_ok=True)
        (project_path / "js").mkdir(exist_ok=True)
        
        # Create index.html
        (project_path / "index.html").write_text(
            f'<!DOCTYPE html>\n'
            f'<html lang="en">\n'
            f'<head>\n'
            f'    <meta charset="UTF-8">\n'
            f'    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f'    <title>{name}</title>\n'
            f'    <link rel="stylesheet" href="css/style.css">\n'
            f'</head>\n'
            f'<body>\n'
            f'    <h1>Welcome to {name}</h1>\n'
            f'    <p>Scaffolded by Ollie CLI</p>\n'
            f'    <script src="js/main.js"></script>\n'
            f'</body>\n'
            f'</html>\n'
        )
        
        # Create css/style.css
        (project_path / "css" / "style.css").write_text(
            'body {\n'
            '    font-family: Arial, sans-serif;\n'
            '    max-width: 800px;\n'
            '    margin: 0 auto;\n'
            '    padding: 20px;\n'
            '}\n'
        )
        
        # Create js/main.js
        (project_path / "js" / "main.js").write_text(
            f"console.log('Welcome to {name}!');\n"
        )
        
        # Create README.md
        (project_path / "README.md").write_text(
            f"# {name}\n\n"
            f"A web project scaffolded by Ollie CLI.\n\n"
            f"Open `index.html` in your browser to view.\n"
        )

    def _scaffold_api(self, project_path: Path, name: str):
        """Scaffold a basic API project (Python Flask)."""
        # Create directory structure
        (project_path / "app").mkdir(exist_ok=True)
        
        # Create app/__init__.py
        (project_path / "app" / "__init__.py").write_text(
            'from flask import Flask\n\n'
            'def create_app():\n'
            '    app = Flask(__name__)\n'
            '    \n'
            '    from app import routes\n'
            '    app.register_blueprint(routes.bp)\n'
            '    \n'
            '    return app\n'
        )
        
        # Create app/routes.py
        (project_path / "app" / "routes.py").write_text(
            'from flask import Blueprint, jsonify\n\n'
            'bp = Blueprint("api", __name__, url_prefix="/api")\n\n'
            '@bp.route("/health")\n'
            'def health():\n'
            '    return jsonify({"status": "healthy"})\n\n'
            '@bp.route("/")\n'
            'def index():\n'
            f'    return jsonify({{"message": "Welcome to {name} API"}})\n'
        )
        
        # Create run.py
        (project_path / "run.py").write_text(
            'from app import create_app\n\n'
            'app = create_app()\n\n'
            'if __name__ == "__main__":\n'
            '    app.run(debug=True)\n'
        )
        
        # Create requirements.txt
        (project_path / "requirements.txt").write_text(
            'Flask>=2.0.0\n'
        )
        
        # Create README.md
        (project_path / "README.md").write_text(
            f"# {name}\n\n"
            f"An API project scaffolded by Ollie CLI.\n\n"
            f"## Installation\n\n"
            f"```bash\n"
            f"pip install -r requirements.txt\n"
            f"```\n\n"
            f"## Usage\n\n"
            f"```bash\n"
            f"python run.py\n"
            f"```\n\n"
            f"API will be available at: http://localhost:5000/api\n"
        )
