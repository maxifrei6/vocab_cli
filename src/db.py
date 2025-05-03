#!/usr/bin/env python3
import sqlite3
import click
import yaml
from pathlib import Path

# Load config
CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
with open(CONFIG_PATH) as f:
    cfg = yaml.safe_load(f)

DB_PATH = Path(cfg["database_path"])
SCHEMA = """
CREATE TABLE IF NOT EXISTS vocab (
    word             TEXT    PRIMARY KEY,
    translation_en   TEXT,
    translation_de   TEXT,
    definition       TEXT,
    example_sentence TEXT,
    context          TEXT,
    first_seen       DATE,
    last_seen        DATE,
    known            INTEGER DEFAULT 0,
    box              INTEGER DEFAULT 1,
    next_review      DATE
);
"""

def get_connection():
    """Get a database connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

@click.group()
def cli():
    """Database utilities for VocabCLI."""
    pass

@cli.command()
def init():
    """Initialize the SQLite database and create tables."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(SCHEMA)
    conn.commit()
    conn.close()
    click.echo(f"Initialized database at {DB_PATH}")

if __name__ == "__main__":
    cli()
