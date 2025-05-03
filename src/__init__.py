# Export version
__version__ = '0.1.0'

# Export main functions
from .db import get_connection, init
from .llm import call_ollama
from .srs import update_box, calculate_next_review
from .chat import start_session
from .utils import normalize_text, extract_words, setup_logging

__all__ = [
    'get_connection',
    'init',
    'call_ollama',
    'update_box',
    'calculate_next_review',
    'start_session',
    'normalize_text',
    'extract_words',
    'setup_logging'
]
