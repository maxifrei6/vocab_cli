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
    
    # Create a prompt that includes the known words
    words_str = ", ".join(known_words)
    prompt = f"""You are a Spanish language tutor. The student knows these words: {words_str}

Please have a natural conversation in Spanish, using simple sentences and the words the student knows.
Keep your responses short and clear. If the student makes a mistake, gently correct them.
If the student says they don't understand, explain in simpler terms.

Start the conversation with a simple greeting."""

    try:
        # Get initial greeting
        response = llm.call_ollama(prompt)
        tutor_response = response.get('raw_response', '').strip()
        if tutor_response:
            # Remove any markdown formatting
            tutor_response = re.sub(r'\*\*|\*|`', '', tutor_response)
            # Remove any English translations in parentheses
            tutor_response = re.sub(r'\(.*?\)', '', tutor_response)
            # Remove any notes or explanations
            tutor_response = re.sub(r'Note:.*|\(Note:.*?\)', '', tutor_response)
            # Take only the first line if there are multiple lines
            tutor_response = tutor_response.split('\n')[0].strip()
        
        click.echo(f"Tutor: {tutor_response}")
        
        conversation_history = []
        conversation_history.append(f"Tutor: {tutor_response}")
        
        while True:
            user_input = click.prompt("\nYou", type=str)
            if user_input.lower() == 'exit':
                break
                
            conversation_history.append(f"Student: {user_input}")
            
            # Create a prompt for the response
            response_prompt = f"""You are a Spanish language tutor having a conversation with a student.
The student knows these words: {words_str}

Previous conversation:
{chr(10).join(conversation_history[-4:])}

IMPORTANT:
1. Continue the conversation naturally based on the student's last message
2. Do not start a new conversation or say hello again
3. Keep your response short and clear
4. Use only the words the student knows
5. Do not include any English translations or notes
6. Do not include any explanations or corrections unless the student asks for them

Please respond to the student's last message in Spanish."""

            response = llm.call_ollama(response_prompt)
            tutor_response = response.get('raw_response', '').strip()
            if tutor_response:
                # Remove any markdown formatting
                tutor_response = re.sub(r'\*\*|\*|`', '', tutor_response)
                # Remove any English translations in parentheses
                tutor_response = re.sub(r'\(.*?\)', '', tutor_response)
                # Remove any notes or explanations
                tutor_response = re.sub(r'Note:.*|\(Note:.*?\)', '', tutor_response)
                # Take only the first line if there are multiple lines
                tutor_response = tutor_response.split('\n')[0].strip()
            
            if tutor_response:
                click.echo(f"\nTutor: {tutor_response}")
                conversation_history.append(f"Tutor: {tutor_response}")
            else:
                click.echo("\nTutor: Lo siento, no entiendo. ¿Podrías repetir?")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
    
    click.echo("\nConversation ended. ¡Hasta luego!")
