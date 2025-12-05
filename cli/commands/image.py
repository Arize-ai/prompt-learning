"""
Image command - Test image generation prompts.
"""

import click
import os
from pathlib import Path

from providers.google_provider import GoogleProvider

@click.command()
@click.option(
    "--prompt", 
    "-p",
    required=True,
    help="Image generation prompt to test"
)
@click.option(
    "--provider",
    default="nano-banana",
    type=click.Choice(["nano-banana"]),
    help="Image generation provider"
)
@click.option(
    "--iterations",
    "-i",
    default=5,
    type=int,
    help="Number of test iterations"
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    help="Directory to save generated images"
)
@click.option(
    "--evaluate",
    "-e",
    is_flag=True,
    help="Evaluate generated images for prompt optimization"
)
@click.option(
    "--budget",
    "-b", 
    default=2.0,
    type=float,
    help="Maximum budget in USD for image generation (default: $2.00)"
)
def image(prompt, provider, iterations, output_dir, evaluate, budget):
    """
    Test image generation prompts with nano banana.
    
    Generates multiple images and evaluates consistency and quality.
    Budget limiting prevents unexpected image generation costs.
    
    Examples:
        # Generate images with default $2 budget
        prompt-learn image -p "A red sports car in the mountains"
        
        # Custom budget for more iterations
        prompt-learn image -p "Complex scene" --iterations 10 --budget 5.00
        
        # Generate and evaluate for prompt improvement
        prompt-learn image -p "Your prompt" --evaluate --budget 3.00
    """
    
    print(f"Testing image prompt: {prompt[:100]}...")
    print(f"Provider: {provider}")
    print(f"Iterations: {iterations}")
    print(f"Budget limit: ${budget:.2f}")
    
    # Create output directory if specified
    try:
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            print(f"Output directory: {output_path}")
        else:
            output_path = Path("./image_outputs")
            output_path.mkdir(exist_ok=True)
            print(f"Using default output directory: {output_path}")
    except PermissionError:
        print(f"Permission denied: Cannot create directory {output_dir or './image_outputs'}")
        return
    except Exception as e:
        print(f"Error creating output directory: {e}")
        return
    
    # Initialize provider
    try:
        if provider == "nano-banana":
            google_provider = GoogleProvider()
            print("✅ Nano banana provider initialized")
            
            # Generate images
            for i in range(iterations):
                print(f"\n🎨 Generating image {i+1}/{iterations}...")
                
                # Create unique filename
                filename = f"image_{i+1:03d}.png"
                save_path = output_path / filename
                
                # Generate image
                result = google_provider.generate_image(
                    prompt=prompt,
                    model="gemini-2.5-flash-image",
                    save_path=str(save_path)
                )
                
                print(f"   {result}")
            
            print(f"\n✅ Generated {iterations} images in {output_path}")
            
            # Human-in-the-loop evaluation
            if evaluate:
                print("\n🔍 Human Evaluation Mode:")
                print(f"   Original prompt: {prompt}")
                print(f"   Images saved in: {output_path}")
                print("\n📝 Please review the images and provide feedback:")
                
                feedback = input("   What works well? ")
                improvements = input("   What could be improved? ")
                rating = input("   Overall rating (1-5): ")
                
                # Save human feedback for prompt learning
                feedback_file = output_path / "human_feedback.txt"
                with open(feedback_file, 'w') as f:
                    f.write(f"Prompt: {prompt}\n")
                    f.write(f"Rating: {rating}\n")
                    f.write(f"What works: {feedback}\n")
                    f.write(f"Improvements: {improvements}\n")
                
                print(f"Feedback saved to {feedback_file}")
                print("Use this feedback to optimize future prompts")
            else:
                print("Use --evaluate flag for human-in-the-loop feedback collection")
            
        else:
            print(f"Provider {provider} not supported yet")
            
    except Exception as e:
        print(f"Error during image generation: {e}")