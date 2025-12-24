"""
Utility Functions

Common helper functions used across the application.
"""

import os
import hashlib
from pathlib import Path
from typing import Optional, Any
from dotenv import load_dotenv


def load_environment():
    """Load environment variables from .env file or Streamlit secrets."""
    # First, try to load from Streamlit secrets (for Streamlit Cloud)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'ANTHROPIC_API_KEY' in st.secrets:
            os.environ['ANTHROPIC_API_KEY'] = st.secrets['ANTHROPIC_API_KEY']
            return True
    except Exception:
        pass

    # Fallback to .env file (for local development)
    env_locations = [
        Path('.env'),
        Path('../.env'),
        Path(__file__).parent.parent.parent / '.env'
    ]

    for env_path in env_locations:
        if env_path.exists():
            load_dotenv(env_path)
            return True

    return False


def get_api_key() -> Optional[str]:
    """Get the Anthropic API key from Streamlit secrets or environment."""
    # Try Streamlit secrets first
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'ANTHROPIC_API_KEY' in st.secrets:
            return st.secrets['ANTHROPIC_API_KEY']
    except Exception:
        pass

    # Fallback to environment variable
    load_environment()
    return os.getenv('ANTHROPIC_API_KEY')


def file_hash(content: bytes) -> str:
    """Generate a hash for file content."""
    return hashlib.md5(content).hexdigest()


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def safe_get(obj: Any, *keys, default=None):
    """Safely get nested dictionary values."""
    for key in keys:
        try:
            obj = obj[key]
        except (KeyError, TypeError, IndexError):
            return default
    return obj


def ensure_dir(path: str) -> Path:
    """Ensure a directory exists."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    if not text:
        return ""

    # Remove excessive whitespace
    import re
    text = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text
