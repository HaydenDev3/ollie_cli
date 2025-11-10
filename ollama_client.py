"""
Ollama Client - Wrapper for Ollama CLI and API interactions

Provides robust error handling and streaming support for Ollama operations.
"""

import json
import logging
import subprocess
import sys
from typing import Dict, List, Optional, Generator


logger = logging.getLogger(__name__)


class OllamaError(Exception):
    """Base exception for Ollama-related errors."""
    pass


class OllamaClient:
    """Client for interacting with Ollama CLI and API."""

    def __init__(self):
        """Initialize Ollama client and validate availability."""
        self._validate_ollama()

    def _validate_ollama(self):
        """Ensure Ollama CLI is available."""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise OllamaError("Ollama CLI found but not functioning properly")
            
            version = result.stdout.strip()
            logger.info(f"Ollama version: {version}")
        except FileNotFoundError:
            raise OllamaError(
                "Ollama CLI not found. Please install from https://ollama.ai/"
            )
        except subprocess.TimeoutExpired:
            raise OllamaError("Ollama CLI timed out during validation")

    def list_models(self) -> List[Dict]:
        """
        List all available Ollama models.
        
        Returns:
            List of model dictionaries with name, size, and metadata
        """
        try:
            result = subprocess.run(
                ["ollama", "list", "--json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.warning("Failed to list models with --json flag, trying without")
                # Fallback to plain list
                result = subprocess.run(
                    ["ollama", "list"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return self._parse_plain_list(result.stdout)
            
            # Try to parse JSON
            try:
                data = json.loads(result.stdout)
                # Handle both array and object formats
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "models" in data:
                    return data["models"]
                else:
                    logger.warning(f"Unexpected JSON format: {type(data)}")
                    return []
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON, falling back to plain parsing")
                return self._parse_plain_list(result.stdout)
                
        except subprocess.TimeoutExpired:
            raise OllamaError("Timeout while listing models")
        except Exception as e:
            logger.exception("Error listing models")
            raise OllamaError(f"Failed to list models: {e}")

    def _parse_plain_list(self, output: str) -> List[Dict]:
        """Parse plain text output from 'ollama list'."""
        models = []
        lines = output.strip().split('\n')
        
        # Skip header line
        for line in lines[1:]:
            if not line.strip():
                continue
            
            parts = line.split()
            if len(parts) >= 1:
                models.append({
                    "name": parts[0],
                    "size": 0,  # Size not easily parseable from plain text
                    "modified": " ".join(parts[1:]) if len(parts) > 1 else ""
                })
        
        return models

    def is_model_available(self, model_name: str) -> bool:
        """
        Check if a model is available locally.
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            True if model is available locally
        """
        models = self.list_models()
        return any(m["name"] == model_name for m in models)

    def pull_model(self, model_name: str, stream: bool = True) -> None:
        """
        Pull a model from Ollama registry.
        
        Args:
            model_name: Name of the model to pull
            stream: Whether to stream output to stdout
        """
        logger.info(f"Pulling model: {model_name}")
        
        try:
            if stream:
                # Stream output to stdout
                process = subprocess.Popen(
                    ["ollama", "pull", model_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                for line in process.stdout:
                    print(line, end='', flush=True)
                
                process.wait()
                
                if process.returncode != 0:
                    raise OllamaError(f"Failed to pull model: {model_name}")
            else:
                # Run without streaming
                result = subprocess.run(
                    ["ollama", "pull", model_name],
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minute timeout for pulling
                )
                
                if result.returncode != 0:
                    raise OllamaError(f"Failed to pull model: {result.stderr}")
                    
        except subprocess.TimeoutExpired:
            raise OllamaError(f"Timeout while pulling model: {model_name}")
        except Exception as e:
            logger.exception(f"Error pulling model: {model_name}")
            raise OllamaError(f"Failed to pull model: {e}")

    def delete_model(self, model_name: str) -> None:
        """
        Delete a model.
        
        Args:
            model_name: Name of the model to delete
        """
        logger.info(f"Deleting model: {model_name}")
        
        try:
            result = subprocess.run(
                ["ollama", "rm", model_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise OllamaError(f"Failed to delete model: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise OllamaError(f"Timeout while deleting model: {model_name}")
        except Exception as e:
            logger.exception(f"Error deleting model: {model_name}")
            raise OllamaError(f"Failed to delete model: {e}")

    def chat_interactive(self, model_name: str, transcript_manager=None, session_id: str = None):
        """
        Start an interactive chat session.
        
        Args:
            model_name: Name of the model to chat with
            transcript_manager: Optional transcript manager for logging
            session_id: Optional session ID for transcript
        """
        logger.info(f"Starting interactive chat with: {model_name}")
        
        try:
            # Use ollama run for interactive chat
            process = subprocess.Popen(
                ["ollama", "run", model_name],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Simple loop for chat interaction
            try:
                while True:
                    # Get user input
                    user_input = input("You: ")
                    
                    if user_input == "/exit":
                        break
                    elif user_input == "/save" and transcript_manager:
                        output_file = input("Save to file: ")
                        transcript_manager.export_session(session_id, output_file)
                        print(f"Saved to {output_file}")
                        continue
                    
                    # Log to transcript
                    if transcript_manager and session_id:
                        transcript_manager.add_message(session_id, "user", user_input)
                    
                    # Send to model
                    process.stdin.write(user_input + "\n")
                    process.stdin.flush()
                    
                    # Read response (simplified - real implementation would need better parsing)
                    print("Assistant: ", end="", flush=True)
                    response = ""
                    # This is a simplified version - real implementation needs proper response handling
                    
            except KeyboardInterrupt:
                logger.info("Chat interrupted by user")
            finally:
                process.terminate()
                process.wait(timeout=5)
                
        except Exception as e:
            logger.exception(f"Error in interactive chat: {model_name}")
            raise OllamaError(f"Chat failed: {e}")

    def chat_once(self, model_name: str, message: str) -> str:
        """
        Send a single message and get response.
        
        Args:
            model_name: Name of the model
            message: Message to send
            
        Returns:
            Model's response
        """
        logger.info(f"Single chat with {model_name}")
        
        try:
            # Use ollama run with stdin
            result = subprocess.run(
                ["ollama", "run", model_name, message],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                raise OllamaError(f"Chat failed: {result.stderr}")
            
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            raise OllamaError("Chat timed out")
        except Exception as e:
            logger.exception("Error in single chat")
            raise OllamaError(f"Chat failed: {e}")
