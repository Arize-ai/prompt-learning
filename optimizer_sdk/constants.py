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

HERE ARE SOME ANNOTATIONS THAT MAY BE HELPFUL:
{annotations}

FINAL INSTRUCTIONS
Iterate on the original prompt (above) with a new prompt that will improve the results, based on the examples and feedback above.

A common best practice in prompt optimization is to add guidelines and the most helpful few shot examples.

Note: Make sure to include the variables from the original prompt, which are wrapped in either single brackets or double brackets (e.g.
{var}). If you fail to include these variables, the LLM will not be able to access the required data.
Do not add any single or double brackets around anything other than the variables from the original prompt. The only curly brackets that should be used are the ones that wrap the variables from the original prompt.
Make sure to copy paste the exact return instructions from the original prompt. Do not add any brackets here. 

YOUR NEW PROMPT:
"""

CODING_AGENT_META_PROMPT_TEMPLATE = """
You are an expert in coding agent prompt optimization.  
Your goal is to improve the dynamic ruleset that guides the coding agent.  

Process:
1. Carefully review the baseline prompt, the current dynamic ruleset, examples, and annotations.  
2. Identify high-level issues in the baseline prompt and dynamic ruleset — focus on missing guidance, vague constraints, or areas where rules could be made more robust.  
3. Revise the dynamic ruleset so it is stronger, more reliable, and generalizes well beyond the provided examples.  

BELOW IS THE ORIGINAL BASELINE PROMPT WITH STATIC RULESET
************* start prompt *************  

{baseline_prompt}  
************* end prompt *************  

BELOW IS THE CURRENT DYNAMIC RULESET (CHANGE THESE OR ADD NEW RULES)
************* start ruleset *************  

{ruleset}  
************* end ruleset *************  

BELOW ARE THE EXAMPLES USING THE ABOVE PROMPT  
************* start example data *************  

{examples}  
************* end example data *************  

FINAL INSTRUCTIONS  
Iterate on the **dynamic ruleset only**. You may:  
- Add new rules  
- Edit or strengthen existing rules  

Important constraints:
- Do **not** modify the static rules in the baseline prompt.  
- Do **not** add rules that request user input, confirmations, or follow-up questions (e.g., `ask_followup_question`). The coding agent should always act autonomously.  
- Keep the ruleset concise and relevant — avoid unnecessary rules that don't match the general types of problems that the coding agent is likely to encounter or overly specific rules that only patch the given examples.  

Output format:
- Return only the final, revised dynamic ruleset as a bullet-point list.  
- Do not include any extra commentary, explanations, or text outside the ruleset.  

New ruleset:
"""


# Template placeholders
EXAMPLES_PLACEHOLDER = "{examples}"

# Example formatting constants
EXAMPLE_HEADER = "Example {index}"
ORIGINAL_TEMPLATE_LABEL = "Original Template With Variables from the Baseline Prompt Populated:"
OUTPUT_LABEL = "Output from the LLM using the template above:"
FEEDBACK_LABEL = "Feedback from the evaluator using the template above and the output above:"