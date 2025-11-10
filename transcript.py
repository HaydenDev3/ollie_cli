"""
Transcript Manager - Handle conversation transcripts and context embedding

Manages chat session transcripts with support for export and context tracking.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import uuid


logger = logging.getLogger(__name__)


class TranscriptManager:
    """Manage chat transcripts and context."""

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize transcript manager.
        
        Args:
            storage_dir: Directory to store transcripts (default: ~/.ollie/transcripts)
        """
        self.storage_dir = storage_dir or Path.home() / ".ollie" / "transcripts"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory session cache
        self.sessions: Dict[str, Dict] = {}
        
        logger.info(f"Transcript storage: {self.storage_dir}")

    def new_session(self, model_name: str) -> str:
        """
        Create a new chat session.
        
        Args:
            model_name: Name of the model for this session
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        session_data = {
            "session_id": session_id,
            "model": model_name,
            "created_at": timestamp,
            "messages": [],
            "context": []
        }
        
        self.sessions[session_id] = session_data
        self._save_session(session_id)
        
        logger.info(f"New session created: {session_id} with model {model_name}")
        return session_id

    def add_message(self, session_id: str, role: str, content: str):
        """
        Add a message to a session.
        
        Args:
            session_id: Session ID
            role: Message role (user, assistant, system)
            content: Message content
        """
        if session_id not in self.sessions:
            self._load_session(session_id)
        
        if session_id not in self.sessions:
            logger.error(f"Session not found: {session_id}")
            return
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        self.sessions[session_id]["messages"].append(message)
        self._save_session(session_id)
        
        logger.debug(f"Message added to {session_id}: {role}")

    def add_context(self, session_id: str, context_data: Dict):
        """
        Add context/embedding data to a session.
        
        Args:
            session_id: Session ID
            context_data: Context information to add
        """
        if session_id not in self.sessions:
            self._load_session(session_id)
        
        if session_id not in self.sessions:
            logger.error(f"Session not found: {session_id}")
            return
        
        context_entry = {
            "data": context_data,
            "timestamp": datetime.now().isoformat()
        }
        
        self.sessions[session_id]["context"].append(context_entry)
        self._save_session(session_id)
        
        logger.debug(f"Context added to {session_id}")

    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Get session data.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data or None if not found
        """
        if session_id not in self.sessions:
            self._load_session(session_id)
        
        return self.sessions.get(session_id)

    def list_sessions(self) -> List[Dict]:
        """
        List all available sessions.
        
        Returns:
            List of session metadata
        """
        sessions = []
        
        for session_file in self.storage_dir.glob("*.json"):
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)
                    sessions.append({
                        "session_id": data["session_id"],
                        "model": data["model"],
                        "created_at": data["created_at"],
                        "message_count": len(data.get("messages", []))
                    })
            except Exception as e:
                logger.warning(f"Failed to read session {session_file}: {e}")
        
        return sorted(sessions, key=lambda x: x["created_at"], reverse=True)

    def export_session(self, session_id: str, output_path: str, format: str = "txt"):
        """
        Export a session to a file.
        
        Args:
            session_id: Session ID to export
            output_path: Output file path
            format: Export format (txt, json, md)
        """
        session_data = self.get_session(session_id)
        
        if not session_data:
            raise ValueError(f"Session not found: {session_id}")
        
        if format == "json":
            self._export_json(session_data, output_path)
        elif format == "md":
            self._export_markdown(session_data, output_path)
        else:  # txt
            self._export_text(session_data, output_path)
        
        logger.info(f"Exported session {session_id} to {output_path} ({format})")

    def _export_text(self, session_data: Dict, output_path: str):
        """Export session as plain text."""
        with open(output_path, 'w') as f:
            f.write(f"Ollie CLI Chat Transcript\n")
            f.write(f"========================\n\n")
            f.write(f"Session ID: {session_data['session_id']}\n")
            f.write(f"Model: {session_data['model']}\n")
            f.write(f"Created: {session_data['created_at']}\n")
            f.write(f"\n{'=' * 50}\n\n")
            
            for msg in session_data["messages"]:
                role = msg["role"].upper()
                content = msg["content"]
                timestamp = msg["timestamp"]
                
                f.write(f"[{timestamp}] {role}:\n")
                f.write(f"{content}\n\n")

    def _export_json(self, session_data: Dict, output_path: str):
        """Export session as JSON."""
        with open(output_path, 'w') as f:
            json.dump(session_data, f, indent=2)

    def _export_markdown(self, session_data: Dict, output_path: str):
        """Export session as Markdown."""
        with open(output_path, 'w') as f:
            f.write(f"# Ollie CLI Chat Transcript\n\n")
            f.write(f"**Session ID:** {session_data['session_id']}  \n")
            f.write(f"**Model:** {session_data['model']}  \n")
            f.write(f"**Created:** {session_data['created_at']}  \n\n")
            f.write(f"---\n\n")
            
            for msg in session_data["messages"]:
                role = msg["role"].title()
                content = msg["content"]
                timestamp = msg["timestamp"]
                
                f.write(f"### {role} ({timestamp})\n\n")
                f.write(f"{content}\n\n")

    def _save_session(self, session_id: str):
        """Save session to disk."""
        if session_id not in self.sessions:
            return
        
        session_file = self.storage_dir / f"{session_id}.json"
        
        try:
            with open(session_file, 'w') as f:
                json.dump(self.sessions[session_id], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save session {session_id}: {e}")

    def _load_session(self, session_id: str):
        """Load session from disk."""
        session_file = self.storage_dir / f"{session_id}.json"
        
        if not session_file.exists():
            return
        
        try:
            with open(session_file, 'r') as f:
                self.sessions[session_id] = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")

    def delete_session(self, session_id: str):
        """
        Delete a session.
        
        Args:
            session_id: Session ID to delete
        """
        session_file = self.storage_dir / f"{session_id}.json"
        
        if session_file.exists():
            session_file.unlink()
            logger.info(f"Deleted session: {session_id}")
        
        if session_id in self.sessions:
            del self.sessions[session_id]

    def get_context_summary(self, session_id: str) -> str:
        """
        Get a summary of session context.
        
        Args:
            session_id: Session ID
            
        Returns:
            Context summary string
        """
        session_data = self.get_session(session_id)
        
        if not session_data:
            return "No session found"
        
        message_count = len(session_data.get("messages", []))
        context_count = len(session_data.get("context", []))
        
        return f"Messages: {message_count}, Context entries: {context_count}"
