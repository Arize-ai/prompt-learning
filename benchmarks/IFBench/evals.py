from phoenix.evals import create_evaluator
from phoenix.evals.llm import LLM
import re
import string
from collections import Counter


# Initialize the LLM once (reused across evaluations)
llm = LLM(provider="openai", model="gpt-4.1-mini")

EVALUATION_PROMPT = """
Your job is to check whether a response adheres to the given constraints. 

Response: {response}
Constraints: {constraints}

You MUST return a JSON object with exactly two fields:
1. "label": Must be EXACTLY the string "True" or "False"
   - Return "True" if the response adheres to the constraints
   - Return "False" if the response does not adhere to the constraints
2. "explanation": A detailed explanation of your reasoning
"""


@create_evaluator(name="evaluator", source="llm")
def evaluate_response(input, output, expected):
    response = output["final_response"]
    constraints = input["constraint"]
    
    prompt = EVALUATION_PROMPT.replace("{response}", response).replace("{constraints}", constraints)
    response = llm.generate_object(
        prompt=prompt,
        schema={
            "type": "object",
            "properties": {
                "label": {
                    "type": "string",
                    "enum": ["True", "False"]
                },
                "explanation": {"type": "string"}
            },
            "required": ["label", "explanation"]
        })
    label = response["label"]
    explanation = response["explanation"]
    
    return {"label": label, "score": 1.0 if label == "True" else 0.0, "explanation": explanation}
