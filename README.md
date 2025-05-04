# VocabCLI: Spanish Vocabulary Coach [Work in Progress]

A terminal-based Spanish vocabulary learning system that leverages local LLaMA models (via Ollama) to create an intelligent, personalized learning experience. Built through Vibe coding using Cursor.

## Features

- **Add New Words**: Input a Spanish word and context, and the system generates:
  - English translation
  - German translation
  - Spanish definition
  - Example sentence
- **Spaced Repetition Review**: Leitner-style SRS with configurable intervals
- **Conversational Practice**: Chat in Spanish with the model, which uses your known vocabulary and introduces new words
- **Data Persistence**: SQLite database stores all your vocabulary data
- **Import/Export**: Backup and restore your vocabulary data

## Requirements

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running with a LLaMA model (e.g., `llama3.2:latest`)
- Dependencies listed in `requirements.txt`

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/maxifrei6/vocab_cli.git
   cd vocab_cli
   ```

2. Set up your environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the system:
   ```bash
   python vocab_cli.py init
   ```

## Configuration

Customize your learning experience by editing `config.yaml`:
- Select your preferred Ollama model
- Configure database location
- Adjust SRS review intervals
- Set logging preferences

## Core Commands

### Add Vocabulary
```bash
python vocab_cli.py add "palabra" "contexto"
```

### Review Flashcards
```bash
python vocab_cli.py review
```

### Conversation Practice
```bash
python vocab_cli.py chat
```

### Data Management
```bash
# Export your vocabulary
python vocab_cli.py export vocab_backup.json

# Import vocabulary
python vocab_cli.py import vocab_backup.json
```

## Project Structure

```
vocab_cli/
├── vocab_cli.py       # Main application entry
├── config.yaml        # User configuration
├── data/             # Database storage
├── logs/             # Application logs
├── requirements.txt  # Dependencies
└── src/             # Source modules
    ├── cli.py       # Command interface
    ├── db.py        # Database operations
    ├── llm.py       # AI model integration
    ├── srs.py       # Learning algorithm
    ├── chat.py      # Interactive practice
    └── utils.py     # Shared utilities
```

## Next Steps

- Import top 1000 frequently used Spanish vocabulary
- Enhance interactive conversation functionality
- Optimize LLM prompts to ensure complete database entries
