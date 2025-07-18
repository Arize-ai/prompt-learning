#!/usr/bin/env python3
"""
Standalone script to run BigBench Hard experiments.
This script can be run directly or through VS Code debugging.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main function to run BigBench Hard experiments."""
    print("🚀 Starting BigBench Hard Experiments")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key as an environment variable.")
        sys.exit(1)
    
    print("✓ OpenAI API key found")
    
    try:
        # Import the function
        from pl_multidataset import run_bbh_experiments
        
        print("✓ Successfully imported BigBench Hard functions")
        print("")
        
        # Run the experiments
        print("🔄 Running BigBench Hard experiments...")
        print("This may take several minutes depending on your configuration.")
        print("")
        
        results_df = run_bbh_experiments()
        
        print("")
        print("🎉 Experiments completed successfully!")
        print(f"Results saved to: bbh_results.csv")
        print(f"Number of experiments: {len(results_df)}")
        
        return results_df
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required packages are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error running experiments: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 