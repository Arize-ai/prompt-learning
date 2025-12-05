"""
Main CLI entry point for prompt learning optimization.
"""

import click
from .commands import optimize, evaluate, test, image

@click.group()
@click.version_option()
@click.option(
    "--verbose", "-v", 
    is_flag=True, 
    help="Enable verbose output with detailed progress information"
)
@click.pass_context
def cli(ctx, verbose):
    """
    Prompt Learning CLI - Optimize LLM prompts using natural language feedback
    
    This tool helps you improve prompts by learning from examples and feedback
    rather than relying on numerical optimization scores. It supports multiple
    AI providers and can process datasets of any size efficiently.
    
    \b
    Quick Start:
        prompt-learn optimize -p "Your prompt here" -d data.csv -f feedback
        prompt-learn image -p "A detailed scene description" 
        
    \b
    Examples:
        # Optimize with OpenAI
        prompt-learn optimize \\
            --prompt "Summarize this text clearly" \\
            --dataset examples.csv \\
            --feedback-columns human_rating \\
            --provider openai
            
        # Generate and evaluate images  
        prompt-learn image \\
            --prompt "A futuristic cityscape at sunset" \\
            --iterations 3 \\
            --evaluate
    
    Environment Variables:
        OPENAI_API_KEY     - OpenAI API key for GPT models
        GOOGLE_API_KEY     - Google AI API key for Gemini models  
        GEMINI_API_KEY     - Alternative Google AI API key
    """
    # Store verbose flag in context for commands to access
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose

# Add command groups
cli.add_command(optimize.optimize)
cli.add_command(evaluate.evaluate) 
cli.add_command(test.test)
cli.add_command(image.image)

if __name__ == "__main__":
    cli()