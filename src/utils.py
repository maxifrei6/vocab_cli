#!/usr/bin/env python3
import logging
import yaml
from pathlib import Path
import unicodedata
import re

# Load configuration
CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
with open(CONFIG_PATH) as f:
    cfg = yaml.safe_load(f)

# Setup logging
LOG_PATH = Path(cfg["logging"]["file"])
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=cfg["logging"]["level"],
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def normalize_text(text: str) -> str:
    """
    Normalize text by removing accents and converting to lowercase.
    """
    # Remove accents
    text = ''.join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn')
    # Convert to lowercase
    return text.lower()

def extract_words(text: str) -> list:
    """
    Extract Spanish words from text, handling accents and special characters.
    """
    # Match Spanish words including accents and ñ
    pattern = r'\b[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+\b'
    return re.findall(pattern, text)

def setup_logging():
    """
    Configure logging based on config.yaml settings.
    """
    log_level = cfg["logging"]["level"]
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    
    logging.getLogger().setLevel(numeric_level)
    logger.info(f"Logging initialized with level {log_level}")
