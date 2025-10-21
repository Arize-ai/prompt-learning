from typing import List, Tuple
import pandas as pd
import openai
import os
import time
from openai import APITimeoutError, APIError

from .constants import END_DELIM, START_DELIM


class Annotator:
    def __init__(self, annotations_prompt_template: str):
        self.annotations_prompt_template = annotations_prompt_template

    def construct_content(
        self,
        batch_df: pd.DataFrame,
        baseline_prompt: str,
        template_variables: List[str],
        feedback_columns: List[str],
        output_column: str,
        ground_truth_column: str = None,
    ) -> str:
        """
        Generate annotations based on the evaluation results.
        
        Args:
            batch_df: DataFrame containing the evaluation data
            baseline_prompt: The original prompt that was evaluated
            template_variables: List of template variable names
            feedback_columns: List of feedback column names
            output_column: Name of the output column
            
        Returns:
            Formatted prompt string for annotation generation
        """
        content = self.annotations_prompt_template
        content = content.replace("{baseline prompt}", baseline_prompt)
        
        examples = ""
        # Iterate over the batch of data and populate the template with actual values
        for ind, row in batch_df.iterrows():
            row_dict = row.to_dict()
            output_value = row_dict[output_column]
            if output_value is not None and isinstance(output_value, str):
                output_value = output_value.replace(START_DELIM, " ").replace(END_DELIM, " ")
            else:
                output_value = "None"
            if ground_truth_column is not None:
                ground_truth_value = row_dict[ground_truth_column]
            else:
                ground_truth_value = "N/A"
            current_example = f"""\n
                Example {str(ind)}

                Input: {[row_dict[temp_var] for temp_var in template_variables]}

                Output: {output_value}

                Ground Truth: {row_dict.get('ground_truth', 'N/A')}

                Feedback:
            """

            for feedback_column in feedback_columns:
                feedback_value = row_dict[feedback_column]
                if feedback_value is not None:
                    # Cast to string to handle integers and other types
                    feedback_value = str(feedback_value)
                    feedback_value = feedback_value.replace(START_DELIM, " ").replace(END_DELIM, " ")
                else:
                    feedback_value = "None"
                current_example += f"\n{feedback_column}: {feedback_value}"
            examples += current_example
            
        content = content.replace("{examples}", examples)
        return content 
    
    def generate_annotation(
        self,
        prompt: str,
        max_retries: int = 5,
        initial_delay: float = 1.0,
        backoff_factor: float = 3.0,
    ) -> str:
        """
        Generate annotation using OpenAI API with retry logic.
        
        Args:
            prompt: The prompt to send to the API
            max_retries: Maximum number of retry attempts (default: 5)
            initial_delay: Initial delay in seconds before first retry (default: 1.0)
            backoff_factor: Multiplier for delay after each retry (default: 3.0)
            
        Returns:
            str: Generated annotation
            
        Raises:
            Exception: Re-raises the last exception if all retries fail
        """
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        delay = initial_delay
        
        for attempt in range(max_retries + 1):  # +1 for the initial attempt
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "user", "content": prompt},
                    ]
                )
                return response.choices[0].message.content
            except (APITimeoutError, APIError) as e:
                if attempt == max_retries:
                    # Last attempt failed, raise with clear message
                    print(f"❌ Annotation API call failed after {max_retries} retries")
                    raise Exception(f"Annotation API call failed after {max_retries} retries. Last error: {e}") from e
                
                # Calculate next delay
                next_delay = delay * backoff_factor if attempt > 0 else delay
                
                # Print retry information
                print(f"⚠️  Annotation API call failed (attempt {attempt + 1}/{max_retries + 1}): {type(e).__name__}: {str(e)}")
                print(f"   Retrying in {next_delay:.0f}s...")
                
                # Wait before retrying
                time.sleep(next_delay)
                delay = next_delay
            except Exception as e:
                # For other exceptions, fail immediately
                print(f"❌ Unexpected error during annotation API call: {type(e).__name__}: {str(e)}")
                raise

        