"""
Main CLI entry point for prompt learning optimization.
"""

import click
from .commands import optimize, evaluate, test, image

@click.group()
@click.version_option()
def cli():
    """
    Prompt Learning CLI
    
    Optimize LLM prompts using natural language feedback instead of numerical scores.
    """
    pass

# Add command groups
cli.add_command(optimize.optimize)
cli.add_command(evaluate.evaluate) 
cli.add_command(test.test)
cli.add_command(image.image)

if __name__ == "__main__":
    cli()