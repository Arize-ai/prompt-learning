# Constants for the prompt-learning-sdk module.


# Delimiters for template variables
START_DELIM = "{"
END_DELIM = "}"

SUPPORTED_MODELS = [
    "o1",
    "o3",
    "gpt-4o",
    "gpt-4",
    "gpt-3.5-turbo",
    "gpt-3.5",
]

# Meta prompt template sections
META_PROMPT_TEMPLATE = """
You are an expert in prompt optimization. Given the original baseline prompt and the following associated metadata (such as model inputs, outputs, evaluation labels and explanations),
generate a revised version of the original prompt that would likely improve results with respect to the evaluation labels.
Your goal is to align the prompt with the feedback and evaluation criteria.

BELOW IS THE ORIGINAL BASELINE PROMPT
************* start prompt *************


{baseline_prompt}
************* end prompt *************

BELOW ARE THE EXAMPLES USING THE ABOVE PROMPT
************* start example data *************


{examples}
************* end example data *************

FINAL INSTRUCTIONS
Iterate on the original prompt (above) with a new prompt that will improve the results, based on the examples and feedback above.

A common best practice in prompt optimization is to add guidelines and the most helpful few shot examples.

Note: Make sure to include the variables from the original prompt, which are wrapped in either single brackets or double brackets (e.g.
{var}). If you fail to include these variables, the LLM will not be able to access the required data.

YOUR NEW PROMPT:
"""

# Template placeholders
EXAMPLES_PLACEHOLDER = "{examples}"

# Example formatting constants
EXAMPLE_HEADER = "Example {index}"
ORIGINAL_TEMPLATE_LABEL = "Original Template With Variables from the Baseline Prompt Populated:"
OUTPUT_LABEL = "Output from the LLM using the template above:"
FEEDBACK_LABEL = "Feedback from the evaluator using the template above and the output above:"
