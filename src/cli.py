#!/usr/bin/env python3
import click
import json
from datetime import datetime
from .db import get_connection, init
from .llm import call_ollama
from .srs import update_box, calculate_next_review
from .chat import start_session

@click.group()
def cli(args=None):
    """VocabCLI - A terminal-based Spanish vocabulary coach."""
    pass

@cli.command()
def init_db():
    """Initialize the database and create tables."""
    init()
    click.echo("Database initialized successfully!")

@cli.command()
@click.argument('word')
@click.argument('context')
def add(word, context):
    """Add a new word to your vocabulary list."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if word already exists
    cursor.execute("SELECT id FROM vocabulary WHERE word = ?", (word,))
    if cursor.fetchone():
        click.echo(f"Word '{word}' already exists in your vocabulary list!")
        conn.close()
        return
    
    # Generate flashcard content using Ollama
    try:
        response = call_ollama(f"Generate a flashcard for the Spanish word '{word}'. Include:\n"
                             f"1. English translation\n"
                             f"2. Definition in Spanish\n"
                             f"3. Example sentence in Spanish")
        
        # Insert into database
        cursor.execute("""
            INSERT INTO vocabulary (word, context, translation, definition, 
                                  example_spanish, box, next_review, created_at)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?)
        """, (
            word,
            context,
            response.get('translation', ''),
            response.get('definition', ''),
            response.get('example_spanish', ''),
            datetime.now(),
            datetime.now()
        ))
        conn.commit()
        click.echo(f"Added '{word}' to your vocabulary list!")
    except Exception as e:
        click.echo(f"Error: {str(e)}")
    finally:
        conn.close()

@cli.command()
def review():
    """Review due flashcards."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get all cards, not just due ones
    cursor.execute("""
        SELECT id, word, translation, definition, example_spanish, box
        FROM vocabulary
        ORDER BY next_review ASC
    """)
    
    cards = cursor.fetchall()
    if not cards:
        click.echo("No cards to review!")
        conn.close()
        return
    
    for card in cards:
        click.echo("\n" + "="*50)
        click.echo(f"Word: {card[1]}")
        click.echo(f"Box: {card[5]}")
        click.echo("\nPress Enter to see translation...")
        input()
        click.echo(f"Translation: {card[2]}")
        click.echo(f"Definition: {card[3]}")
        click.echo(f"Example: {card[4]}")
        
        while True:
            response = click.prompt("\nHow well did you know this? (1-5, q to quit)", type=str)
            if response.lower() == 'q':
                conn.close()
                return
            
            try:
                score = int(response)
                if 1 <= score <= 5:
                    break
                click.echo("Please enter a number between 1 and 5")
            except ValueError:
                click.echo("Please enter a number between 1 and 5")
        
        # Update box and next review date
        new_box = update_box(card[5], score)
        next_review = calculate_next_review(new_box)
        
        cursor.execute("""
            UPDATE vocabulary
            SET box = ?, next_review = ?
            WHERE id = ?
        """, (new_box, next_review, card[0]))
        conn.commit()
    
    conn.close()
    click.echo("\nReview session completed!")

@cli.command()
def chat():
    """Start a conversation practice session."""
    # Get all words from the database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM vocabulary")
    known_words = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if not known_words:
        click.echo("No words in your vocabulary list. Add some words first!")
        return
    
    start_session(known_words)

@cli.command()
@click.argument('output_file', type=click.Path())
def export(output_file):
    """Export vocabulary to a JSON file."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vocabulary")
    words = cursor.fetchall()
    conn.close()
    
    if not words:
        click.echo("No words to export!")
        return
    
    data = []
    for word in words:
        # Handle date fields
        next_review = word[7]
        created_at = word[8]
        
        # Convert dates to ISO format if they exist
        if isinstance(next_review, str):
            next_review = next_review if next_review else None
        else:
            next_review = next_review.isoformat() if next_review else None
            
        if isinstance(created_at, str):
            created_at = created_at if created_at else None
        else:
            created_at = created_at.isoformat() if created_at else None
        
        data.append({
            'word': word[1],
            'context': word[2],
            'translation': word[3],
            'definition': word[4],
            'example_spanish': word[5],
            'box': word[6],
            'next_review': next_review,
            'created_at': created_at
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    click.echo(f"Exported {len(data)} words to {output_file}")

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
def import_(input_file):
    """Import vocabulary data from JSON file."""
    conn = get_connection()
    cursor = conn.cursor()
    
    with open(input_file) as f:
        data = json.load(f)
    
    for item in data:
        cursor.execute("""
            INSERT OR REPLACE INTO vocabulary
            (word, context, translation, definition,
             example_spanish, box, next_review, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item['word'],
            item['context'],
            item['translation'],
            item['definition'],
            item['example_spanish'],
            item['box'],
            datetime.fromisoformat(item['next_review']) if item['next_review'] else None,
            datetime.fromisoformat(item['created_at']) if item['created_at'] else None
        ))
    
    conn.commit()
    conn.close()
    click.echo(f"Imported data from {input_file}")

@cli.command()
@click.argument('word')
def delete(word):
    """Delete a word from your vocabulary list."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM vocabulary WHERE word = ?", (word,))
    if cursor.rowcount > 0:
        conn.commit()
        click.echo(f"Deleted '{word}' from your vocabulary list!")
    else:
        click.echo(f"Word '{word}' not found in your vocabulary list!")
    
    conn.close()
