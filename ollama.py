"""
Ollama CLI wrapper module.
Provides Python interface to the Ollama command-line tool.
"""

import json
import logging
import subprocess
import sys
from typing import List, Dict, Optional, Any

# Module-level logger
logger = logging.getLogger(__name__)


class OllamaError(Exception):
    """Base exception for Ollama-related errors."""
    pass


def ensure_available() -> bool:
    """
    Validate that the Ollama CLI is available and get version.

    Returns:
        bool: True if Ollama is available

    Raises:
        OllamaError: If Ollama is not found or not working
    """
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            logger.info(f"Ollama CLI found: {version}")
            return True
        else:
            logger.error(f"Ollama check failed: {result.stderr}")
            raise OllamaError(f"Ollama CLI check failed: {result.stderr}")
    except FileNotFoundError:
        logger.error("Ollama CLI not found in PATH")
        raise OllamaError("Ollama CLI not found. Please install Ollama from https://ollama.ai/")
    except subprocess.TimeoutExpired:
        logger.error("Ollama CLI check timed out")
        raise OllamaError("Ollama CLI check timed out")
    except Exception as e:
        logger.error(f"Unexpected error checking Ollama: {e}")
        raise OllamaError(f"Unexpected error checking Ollama: {e}")


def list_models() -> List[Dict[str, Any]]:
    """
    List available Ollama models.

    Returns:
        List of model dictionaries with name, size, and other metadata

    Raises:
        OllamaError: If listing models fails
    """
    try:
        result = subprocess.run(
            ["ollama", "list", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            logger.error(f"Failed to list models: {result.stderr}")
            raise OllamaError(f"Failed to list models: {result.stderr}")

        # Try to parse JSON output
        try:
            data = json.loads(result.stdout)

            # Handle both array and {models:[]} layouts
            if isinstance(data, list):
                models = data
            elif isinstance(data, dict) and "models" in data:
                models = data["models"]
            else:
                logger.warning("Unexpected JSON format, attempting fallback")
                models = []
        except json.JSONDecodeError:
            logger.warning("JSON decode failed, falling back to plain text parsing")
            # Fallback: parse plain text output
            models = []
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        models.append({
                            "name": parts[0],
                            "size": parts[1] if len(parts) > 1 else "unknown"
                        })

        logger.info(f"Listed {len(models)} models")
        return models

    except subprocess.TimeoutExpired:
        logger.error("Listing models timed out")
        raise OllamaError("Listing models timed out")
    except Exception as e:
        logger.error(f"Unexpected error listing models: {e}")
        raise OllamaError(f"Unexpected error listing models: {e}")


def pull_model(model_name: str, stream: bool = True) -> subprocess.CompletedProcess:
    """
    Pull/download an Ollama model with optional streaming output.

    Args:
        model_name: Name of the model to pull
        stream: If True, stream output to stdout in real-time

    Returns:
        subprocess.CompletedProcess-like object with returncode

    Raises:
        OllamaError: If pull fails
    """
    logger.info(f"Pulling model: {model_name}")

    try:
        if stream:
            # Stream output to terminal
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # Forward lines to stdout
            for line in process.stdout:
                print(line, end='', flush=True)

            process.wait()
            returncode = process.returncode

            if returncode != 0:
                logger.error(f"Failed to pull model {model_name}")
                raise OllamaError(f"Failed to pull model {model_name}")

            logger.info(f"Successfully pulled model: {model_name}")

            # Return a CompletedProcess-like object
            class Result:
                def __init__(self, returncode):
                    self.returncode = returncode

            return Result(returncode)
        else:
            # Non-streaming: capture all output
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                logger.error(f"Failed to pull model {model_name}: {result.stderr}")
                raise OllamaError(f"Failed to pull model {model_name}: {result.stderr}")

            logger.info(f"Successfully pulled model: {model_name}")
            return result

    except subprocess.TimeoutExpired:
        logger.error(f"Pulling model {model_name} timed out")
        raise OllamaError(f"Pulling model {model_name} timed out")
    except FileNotFoundError:
        logger.error("Ollama CLI not found")
        raise OllamaError("Ollama CLI not found")
    except Exception as e:
        logger.error(f"Unexpected error pulling model: {e}")
        raise OllamaError(f"Unexpected error pulling model: {e}")


def delete_model(model_name: str) -> subprocess.CompletedProcess:
    """
    Delete an Ollama model.

    Args:
        model_name: Name of the model to delete

    Returns:
        subprocess.CompletedProcess object

    Raises:
        OllamaError: If deletion fails
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
            logger.error(f"Failed to delete model {model_name}: {result.stderr}")
            raise OllamaError(f"Failed to delete model {model_name}: {result.stderr}")

        logger.info(f"Successfully deleted model: {model_name}")
        return result

    except subprocess.TimeoutExpired:
        logger.error(f"Deleting model {model_name} timed out")
        raise OllamaError(f"Deleting model {model_name} timed out")
    except FileNotFoundError:
        logger.error("Ollama CLI not found")
        raise OllamaError("Ollama CLI not found")
    except Exception as e:
        logger.error(f"Unexpected error deleting model: {e}")
        raise OllamaError(f"Unexpected error deleting model: {e}")


def run_chat(model_name: str) -> int:
    """
    Start an interactive chat session with a model.
    This directly invokes ollama CLI and passes through to the terminal.

    Args:
        model_name: Name of the model to chat with

    Returns:
        Exit code from the chat process
    """
    logger.info(f"Starting chat with model: {model_name}")

    try:
        result = subprocess.run(
            ["ollama", "run", model_name],
            timeout=None  # No timeout for interactive chat
        )
        return result.returncode
    except KeyboardInterrupt:
        logger.info("Chat interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Error running chat: {e}")
        raise OllamaError(f"Error running chat: {e}")
