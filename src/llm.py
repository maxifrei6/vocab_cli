#!/usr/bin/env python3
import subprocess
import json
import click
from pathlib import Path
import yaml
import re

# Load configuration
CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    cfg = yaml.safe_load(f)

OLLAMA_MODEL = cfg.get("ollama_model", "llama3.2:latest")

class OllamaError(Exception):
    pass

def parse_ollama_response(text: str) -> dict:
    """Parse the Ollama response into a structured dictionary."""
    # Print the raw response for debugging
    print("Raw Ollama response:")
    print(text)
    print("---")
    
    result = {
        'translation': '',
        'definition': '',
        'example_spanish': ''
    }
    
    # Look for translation (multiple possible formats)
    trans_patterns = [
        r'1\.\s*\*\*English Translation:\*\*\s*(.*?)(?:\n|$)',
        r'1\.\s*English Translation:\s*(.*?)(?:\n|$)',
        r'\*\*English Translation:\*\*\s*(.*?)(?:\n|$)',
        r'English Translation:\s*(.*?)(?:\n|$)',
        r'\*\s*English Translation:\s*(.*?)(?:\n|$)'
    ]
    for pattern in trans_patterns:
        trans_match = re.search(pattern, text, re.IGNORECASE)
        if trans_match:
            result['translation'] = trans_match.group(1).strip().strip('*')
            break
    
    # Look for definition (multiple possible formats)
    def_patterns = [
        r'2\.\s*\*\*Definition.*?Spanish\):\*\*\s*(.*?)(?:\n|$)',
        r'2\.\s*Definition.*?Spanish\):\s*(.*?)(?:\n|$)',
        r'2\.\s*\*\*Definition in Spanish:\*\*\s*(.*?)(?:\n|$)',
        r'2\.\s*Definition in Spanish:\s*(.*?)(?:\n|$)',
        r'\*\*Definition.*?Spanish\):\*\*\s*(.*?)(?:\n|$)',
        r'Definition.*?Spanish\):\s*(.*?)(?:\n|$)',
        r'\*\s*Definition.*?Spanish\):\s*(.*?)(?:\n|$)',
        r'\*\*Spanish Definition:\*\*\s*(.*?)(?:\n|$)',
        r'Spanish Definition:\s*(.*?)(?:\n|$)'
    ]
    for pattern in def_patterns:
        def_match = re.search(pattern, text, re.IGNORECASE)
        if def_match:
            result['definition'] = def_match.group(1).strip().strip('*')
            break
    
    # Look for Spanish example (multiple possible formats)
    es_patterns = [
        r'3\.\s*\*\*Example Sentence.*?Spanish\):\*\*\s*"(.*?)"',
        r'3\.\s*Example Sentence.*?Spanish\):\s*"(.*?)"',
        r'3\.\s*\*\*Example Sentence:\*\*\s*"(.*?)"',
        r'3\.\s*Example Sentence:\s*"(.*?)"',
        r'\*\*Example Sentence.*?Spanish\):\*\*\s*"(.*?)"',
        r'Example Sentence.*?Spanish\):\s*"(.*?)"',
        r'\*\s*Example Sentence:\s*"(.*?)"',
        r'Example Sentence:\s*"(.*?)"'
    ]
    for pattern in es_patterns:
        es_match = re.search(pattern, text, re.IGNORECASE)
        if es_match:
            # Extract the Spanish part before any parentheses
            example = es_match.group(1).strip()
            if '(' in example:
                example = example.split('(')[0].strip()
            result['example_spanish'] = example
            break
    
    # Print the parsed result for debugging
    print("Parsed result:")
    print(json.dumps(result, indent=2))
    print("---")
    
    return result

def call_ollama(prompt: str, timeout: int = 60) -> dict:
    """
    Call the local Ollama LLaMA model with a given prompt and return parsed data.
    """
    try:
        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL, prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise OllamaError(f"Model call failed: {e.stderr.strip()}")
    except subprocess.TimeoutExpired:
        raise OllamaError("Ollama call timed out")

    # Parse the response and add the raw response
    parsed = parse_ollama_response(result.stdout)
    parsed['raw_response'] = result.stdout
    return parsed

@click.group()
def cli():
    """Ollama-related commands and testing utilities."""
    pass

@cli.command()
@click.argument('word')
@click.argument('context')
def gen_flashcard(word, context):
    """Generate flashcard data for a single word."""
    prompt = f"""Create a flashcard for the Spanish word '{word}' (context: {context}).

Please provide the following information in this exact format:

1. English Translation: [English translation of the word]
2. Definition (Spanish): [Definition in Spanish]
3. Example Sentence (Spanish): "[Example sentence in Spanish]"

IMPORTANT:
1. Use EXACTLY these labels and format with numbers (1., 2., 3.)
2. The example sentence must be a simple sentence using the word '{word}'
3. Do not add any extra text, explanations, or translations
4. Do not include any markdown formatting
5. Do not include any notes or additional information
6. Do not include parentheses or translations in the example sentence
7. The example sentence must be in quotes
8. Do not use asterisks or bold formatting

Example format for the word "gracias":
1. English Translation: thank you
2. Definition (Spanish): expresión de agradecimiento
3. Example Sentence (Spanish): "Muchas gracias por tu ayuda."

Your response must match this format exactly."""
    
    try:
        data = call_ollama(prompt)
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))
    except OllamaError as e:
        click.echo(f"Error: {e}", err=True)

@cli.command()
@click.argument('session_file', type=click.Path(exists=True))
def gen_chat(session_file):
    """Run conversational practice based on a prompt template file."""
    prompt = Path(session_file).read_text(encoding='utf-8')
    try:
        data = call_ollama(prompt)
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))
    except OllamaError as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == '__main__':
    cli()