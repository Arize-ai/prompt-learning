from typing import List, Mapping, Union

import pandas as pd

from arize_toolkit.extensions.prompt_optimizer.constants import END_DELIM, META_PROMPT_TEMPLATE, START_DELIM


class MetaPrompt:
    meta_prompt_messages = META_PROMPT_TEMPLATE

    def construct_content(
        self,
        batch_df: pd.DataFrame,
        prompt_to_optimize_content: str,
        template_variables: List[str],
        feedback_columns: List[str],
        output_column: str,
    ) -> str:
        content = self.meta_prompt_messages
        content = content.replace("{baseline_prompt}", prompt_to_optimize_content)
        examples = ""
        # iterate over the batch of data and populate the template with the actual values from the dataframe
        # need to populate the template customer is optimizing with template variables
        # add the output from the LLM, add the feedback (will be from evaluator or annotator)
        for ind, row in batch_df.iterrows():
            row_dict = row.to_dict()
            populated_template = self.format_template_with_vars(
                prompt_to_optimize_content,
                template_variables,
                {temp_var: row_dict[temp_var] for temp_var in template_variables},
            )
            output_value = row_dict[output_column]
            if output_value is not None and isinstance(output_value, str):
                output_value = output_value.replace(START_DELIM, " ").replace(END_DELIM, " ")
            else:
                output_value = "None"
            current_example = f"""\n
                Example {str(ind)}

                Original Template With Variables from the Baseline Prompt Populated: {populated_template}

                Output from the LLM using the template above: {output_value}

                Feedback from the evaluator using the template above and the output above:
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

    def format_template_with_vars(
        self,
        template: str,
        template_variables: List[str],
        variable_values: Mapping[str, Union[bool, int, float, str]],
    ) -> str:
        for template_var in template_variables:
            var_value = str(variable_values[template_var])
            if var_value is not None:
                var_value = var_value.replace(START_DELIM, " ")
                var_value = var_value.replace(END_DELIM, " ")
            template = template.replace(
                START_DELIM + template_var + END_DELIM,
                var_value,
            )
        return template
