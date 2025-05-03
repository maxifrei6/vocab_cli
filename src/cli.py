#!/usr/bin/env python3
import click
import yaml
from pathlib import Path
from datetime import datetime, timedelta
import json
from . import db, llm, srs, chat, utils

# Load configuration
CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
with open(CONFIG_PATH) as f:
    cfg = yaml.safe_load(f)

@click.group()
def cli():
    """VocabCLI - A terminal-based Spanish vocabulary coach."""
    pass

@cli.command()
def init():
    """Initialize the database and create tables."""
    db.init()

@cli.command()
@click.argument('word')
@click.argument('context')
def add(word, context):
    """Add a new word to your vocabulary list."""
    # Generate flashcard data using LLM
    try:
        data = llm.call_ollama(
            f"Provide a JSON with keys 'translation_en', 'translation_de', 'definition', 'example_sentence' "
            f"for the Spanish word '{word}'. Use the following context: {context}."
        )
        
        # Add to database
        conn = db.get_connection()
        cursor = conn.cursor()
        today = datetime.now().date()
        
        cursor.execute("""
            INSERT OR REPLACE INTO vocab 
            (word, translation_en, translation_de, definition, example_sentence, context, 
             first_seen, last_seen, known, box, next_review)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            word,
            data['translation_en'],
            data['translation_de'],
            data['definition'],
            data['example_sentence'],
            context,
            today,
            today,
            0,  # known
            1,  # box
            today  # next_review
        ))
        
        conn.commit()
        conn.close()
        click.echo(f"Added word: {word}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.command()
def review():
    """Review due flashcards."""
    conn = db.get_connection()
    cursor = conn.cursor()
    today = datetime.now().date()
    
    # Get due cards
    cursor.execute("""
        SELECT word, translation_en, translation_de, definition, example_sentence
        FROM vocab
        WHERE next_review <= ? AND known = 0
        ORDER BY box
    """, (today,))
    
    cards = cursor.fetchall()
    if not cards:
        click.echo("No cards due for review today!")
        return
    
    for word, en, de, definition, example in cards:
        click.echo("\n" + "="*50)
        click.echo(f"Word: {word}")
        click.echo(f"English: {en}")
        click.echo(f"German: {de}")
        
        if click.confirm("Show definition and example?"):
            click.echo(f"\nDefinition: {definition}")
            click.echo(f"Example: {example}")
        
        correct = click.confirm("Did you know this word?")
        
        # Update card based on response
        new_box = srs.update_box(cursor, word, correct)
        next_review = srs.calculate_next_review(today, new_box)
        
        cursor.execute("""
            UPDATE vocab
            SET box = ?, next_review = ?, last_seen = ?
            WHERE word = ?
        """, (new_box, next_review, today, word))
    
    conn.commit()
    conn.close()
    click.echo("\nReview session complete!")

@cli.command()
def chat():
    """Start a Spanish conversation practice session."""
    try:
        # Get known words for context
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT word FROM vocab WHERE known = 1")
        known_words = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Start chat session
        chat.start_session(known_words)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.command()
@click.argument('output_file', type=click.Path())
def export(output_file):
    """Export vocabulary data to JSON file."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM vocab")
    columns = [description[0] for description in cursor.description]
    data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    conn.close()
    click.echo(f"Exported data to {output_file}")

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
def import_(input_file):
    """Import vocabulary data from JSON file."""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    for item in data:
        cursor.execute("""
            INSERT OR REPLACE INTO vocab 
            (word, translation_en, translation_de, definition, example_sentence, context,
             first_seen, last_seen, known, box, next_review)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item['word'],
            item['translation_en'],
            item['translation_de'],
            item['definition'],
            item['example_sentence'],
            item['context'],
            item['first_seen'],
            item['last_seen'],
            item['known'],
            item['box'],
            item['next_review']
        ))
    
    conn.commit()
    conn.close()
    click.echo(f"Imported data from {input_file}")

if __name__ == '__main__':
    cli()
