from typing import List, Tuple
import pandas as pd
import openai
import os

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
                output_value = output_value.replace(START_DELIM, " ").replace(
                    END_DELIM, " "
                )
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
                    feedback_value = feedback_value.replace(START_DELIM, " ").replace(
                        END_DELIM, " "
                    )
                else:
                    feedback_value = "None"
                current_example += f"\n{feedback_column}: {feedback_value}"
            examples += current_example

        content = content.replace("{examples}", examples)
        return content

    def generate_annotation(
        self,
        prompt: str,
    ) -> str:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content
