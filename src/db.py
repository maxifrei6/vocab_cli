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
DROP TABLE IF EXISTS vocabulary;

CREATE TABLE vocabulary (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    word             TEXT    UNIQUE,
    context          TEXT,
    translation      TEXT,
    definition       TEXT,
    example_spanish  TEXT,
    box              INTEGER DEFAULT 1,
    next_review      DATETIME,
    created_at       DATETIME
);
"""

def get_connection():
    """Get a database connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init():
    """Initialize the SQLite database and create tables."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(SCHEMA)
    conn.commit()
    conn.close()
    click.echo(f"Initialized database at {DB_PATH}")

@click.group()
def cli():
    """Database utilities for VocabCLI."""
    pass

@cli.command()
def init_db():
    """Initialize the SQLite database and create tables."""
    init()

if __name__ == "__main__":
    cli()
