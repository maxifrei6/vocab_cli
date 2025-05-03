# VocabCLI: Spanish Vocabulary Coach [Work in Progress]

A terminal-based Spanish vocabulary coach and flashcard system that uses a local LLaMA model (via Ollama) to generate translations, definitions, and example sentences.

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

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/vocab_cli.git
   cd vocab_cli
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python -m src.cli init
   ```

## Configuration

Edit `config.yaml` to customize:
- Ollama model name
- Database path
- SRS intervals
- Logging settings

## Usage

### Add a New Word
```bash
python -m src.cli add "palabra" "contexto"
```

### Review Flashcards
```bash
python -m src.cli review
```

### Practice Conversation
```bash
python -m src.cli chat
```

### Export/Import Data
```bash
# Export
python -m src.cli export vocab_backup.json

# Import
python -m src.cli import vocab_backup.json
```

## Project Structure

```
vocab_cli/
├── config.yaml          # Configuration settings
├── data/               # SQLite database
├── logs/               # Application logs
├── requirements.txt    # Python dependencies
└── src/               # Source code
    ├── cli.py         # Command-line interface
    ├── db.py          # Database operations
    ├── llm.py         # LLaMA model integration
    ├── srs.py         # Spaced repetition system
    ├── chat.py        # Conversation practice
    └── utils.py       # Helper functions
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.





