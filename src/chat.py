#!/usr/bin/env python3
import click
import re
from datetime import datetime
from . import llm, db, utils

def start_session(known_words: list):
    """
    Start a Spanish conversation practice session.
    known_words: List of words the user already knows
    """
    # Build context for the LLM
    context = {
        "known_words": known_words,
        "max_new_words": 3,
        "language_level": "intermediate",
        "conversation_length": "short"
    }
    
    click.echo("\nStarting Spanish conversation practice...")
    click.echo("Type 'exit' to end the session.\n")
    
    # Initial prompt to the model
    prompt = f"""
    You are a Spanish language tutor. Have a conversation with me in Spanish.
    Use only these known words: {', '.join(known_words)}
    Introduce up to 3 new words naturally in the conversation.
    Keep responses short and clear.
    Start with a greeting and a simple question.
    """
    
    try:
        while True:
            # Get model's response
            response = llm.call_ollama(prompt)
            model_text = response.get('response', '')
            click.echo(f"\nTutor: {model_text}")
            
            # Extract new words using regex
            new_words = re.findall(r'\b[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+\b', model_text)
            new_words = [w.lower() for w in new_words if w.lower() not in known_words]
            
            # If we found new words, add them to the database
            if new_words:
                click.echo("\nNew words detected:")
                for word in new_words:
                    click.echo(f"- {word}")
                    # Add each new word to the database
                    try:
                        data = llm.call_ollama(
                            f"Provide a JSON with keys 'translation_en', 'translation_de', 'definition', 'example_sentence' "
                            f"for the Spanish word '{word}'. Context: found in conversation practice."
                        )
                        
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
                            "Conversation practice",
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
                        click.echo(f"Error adding word {word}: {e}", err=True)
            
            # Get user's response
            user_input = click.prompt("\nYou", type=str)
            if user_input.lower() == 'exit':
                break
            
            # Update prompt with conversation history
            prompt = f"""
            Previous conversation:
            Tutor: {model_text}
            Student: {user_input}
            
            Continue the conversation in Spanish.
            Use only these known words: {', '.join(known_words)}
            Introduce up to 3 new words naturally in the conversation.
            Keep responses short and clear.
            """
    
    except Exception as e:
        click.echo(f"Error in chat session: {e}", err=True)
    
    click.echo("\nConversation practice ended.")
