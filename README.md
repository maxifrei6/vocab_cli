# VocabCLI: Spanish Vocabulary Coach

A lightweight, terminal-based flashcard and conversation coach for Spanish vocabulary.  
Built on Python and Ollama-powered LLaMA, it uses a simple SQLite backend to store words, contexts, translations (EN/DE), and spaced-repetition metadata.

## Features

- **Add new words** with context (movie, book, article, conversation, etc.).
- **Flashcard generation** via local LLaMA model (definitions, example sentences, English & German translations).
- **Spaced-Repetition Review** (Leitner box system with configurable intervals).
- **Conversational Practice**: chat in Spanish using known words and selected new ones; auto-capture new vocabulary.
- **Data persistence** in SQLite, with columns:
  - `word` (TEXT, PK)
  - `translation_en` (TEXT)
  - `translation_de` (TEXT)
  - `definition` (TEXT)
  - `example_sentence` (TEXT)
  - `context` (TEXT)
  - `first_seen` (DATE)
  - `last_seen` (DATE)
  - `known` (BOOLEAN)
  - `box` (INTEGER)

## Prerequisites

- Python 3.9+  
- Ollama installed and configured with a LLaMA model (e.g., `llama2`).  
- SQLite (bundled with Python).

## Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/maxifrei6/vocab_cli.git
   cd VocabCLI
   ```
2. (Optional) Create and activate a virtualenv:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```





