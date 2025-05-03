#!/usr/bin/env python3
import subprocess
import json
import click
from pathlib import Path
import yaml

# Load configuration
def load_config():
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

cfg = load_config()
OLLAMA_MODEL = cfg.get("ollama_model", "llama3.2:latest")

class OllamaError(Exception):
    pass


def call_ollama(prompt: str, timeout: int = 60) -> dict:
    """
    Call the local Ollama LLaMA model with a given prompt and return parsed JSON.
    """
    try:
        result = subprocess.run(
            ["ollama", "generate", OLLAMA_MODEL, "--json", "--prompt", prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise OllamaError(f"Model call failed: {e.stderr.strip()}")
    except subprocess.TimeoutExpired:
        raise OllamaError("Ollama call timed out")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        raise OllamaError("Failed to parse JSON from Ollama output")

@click.group()
def cli():
    """Ollama-related commands and testing utilities."""
    pass

@cli.command()
@click.argument('word')
@click.argument('context')
def gen_flashcard(word, context):
    """Generate flashcard data for a single word."""
    prompt = (
        f"Provide a JSON with keys 'translation_en', 'translation_de', 'definition', 'example_sentence' "
        f"for the Spanish word '{word}'. Use the following context: {context}."
    )
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