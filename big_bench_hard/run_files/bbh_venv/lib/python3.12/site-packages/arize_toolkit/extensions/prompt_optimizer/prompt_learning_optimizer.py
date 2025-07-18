import copy
import re
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union

import pandas as pd
from phoenix.client.types import PromptVersion
from phoenix.evals.models import OpenAIModel

from arize_toolkit.extensions.prompt_optimizer.meta_prompt import MetaPrompt
from arize_toolkit.extensions.prompt_optimizer.tiktoken_splitter import TiktokenSplitter
from arize_toolkit.utils import get_key_value


class PromptLearningOptimizer:
    """
    PromptLearningOptimizer is a class that optimizes a prompt using the meta-prompt approach.

    Args:
        prompt: Either a PromptVersion object or list of messages or a string representing the user prompt
        model_choice: OpenAI model to use for optimization - currently only supports OpenAI models (default: "gpt-4")
        openai_api_key: OpenAI API key for optimization. Can also be set via OPENAI_API_KEY environment variable.

    Methods:
        run_evaluators: Run evaluators on the dataset and add results to feedback columns
            Args:
                dataset: DataFrame or path to JSON file containing the dataset of requests, responses, and feedback to use for optimization
                evaluators: List of Phoenix evaluators to run on the dataset - see https://arize.com/docs/phoenix/evaluation/how-to-evals (default: [])
                feedback_columns: List of column names containing existing feedback from the dataset (required if not using new evaluations)
            Returns:
                Tuple of (dataset, feedback_columns)
        optimize: Optimize the prompt using a meta-prompt approach and return an optimized prompt object
            Args:
                dataset: DataFrame or path to JSON file containing the dataset of requests, responses, and feedback to use for optimization
                output_column: Name of the column containing LLM outputs from the dataset
                evaluators: List of Phoenix evaluators to run on the dataset - see https://arize.com/docs/phoenix/evaluation/how-to-evals (default: [])
                feedback_columns: List of column names containing existing feedback from the dataset (required if not using new evaluations)
                context_size_k: Context window size in thousands of tokens (default: 8k)
                evaluate: Whether to run evaluators on the dataset (default: True)
            Returns:
                optimized_prompt: Optimized prompt object

    Example:
    ```python
        import pandas as pd
        import os
        from arize_toolkit.extensions.prompt_optimizer import PromptLearningOptimizer

        os.environ["OPENAI_API_KEY"] = "your-api-key"

        optimizer = PromptLearningOptimizer(
            prompt="You are a helpful assistant. Answer this question: {question}",
            model_choice="gpt-4",
        )

        dataset = pd.DataFrame({
            "question": ["What is the capital of France?", ...],
            "answer": ["Paris", ...],
            "feedback": ["correct", ...]
        })

        optimized_prompt = optimizer.optimize(
            dataset=dataset,
            output_column="answer",
            feedback_columns=["feedback"],
        )
        print(optimized_prompt.to_dict())
    ```
    """

    def __init__(
        self,
        prompt: Union[PromptVersion, str, List[Dict[str, str]]],
        model_choice: str = "gpt-4",
        openai_api_key: Optional[str] = None,
    ):
        self.prompt = prompt
        self.model_choice = model_choice
        self.openai_api_key = get_key_value("OPENAI_API_KEY", openai_api_key)

        # Initialize components
        self.meta_prompter = MetaPrompt()
        self.optimization_history = []

    def _load_dataset(self, dataset: Union[pd.DataFrame, str]) -> pd.DataFrame:
        """Load dataset from DataFrame or JSON file"""
        if isinstance(dataset, pd.DataFrame):
            return dataset
        elif isinstance(dataset, str):
            # Assume it's a JSON file path
            try:
                return pd.read_json(dataset)
            except Exception as e:
                raise ValueError(f"Failed to load dataset from {dataset}: {e}")

    def _validate_inputs(
        self,
        dataset: pd.DataFrame,
        feedback_columns: List[str] = [],
        evaluators: List[Callable] = [],
        output_column: Optional[str] = None,
        output_required: bool = False,
    ):
        """Validate that we have the necessary inputs for optimization"""
        # Check if we have either feedback columns or evaluators
        if not feedback_columns and not evaluators:
            raise ValueError("Either feedback_columns or evaluators must be provided. " "Need some feedback for MetaPrompt optimization.")

        # Validate dataset has required columns
        required_columns = []
        if output_required:
            if output_column is None:
                raise ValueError("output_column must be provided")
            required_columns.append(output_column)
        if feedback_columns:
            required_columns.extend(feedback_columns)

        missing_columns = [col for col in required_columns if col not in dataset.columns]
        if missing_columns:
            raise ValueError(f"Dataset missing required columns: {missing_columns}")

    def _extract_prompt_messages(
        self,
    ) -> Sequence:
        """Extract messages from prompt object or list"""
        if isinstance(self.prompt, PromptVersion):
            # Extract messages from PromptVersion template
            template = self.prompt._template
            if template["type"] == "chat":
                return template["messages"]
            else:
                raise ValueError("Only chat templates are supported")
        elif isinstance(self.prompt, list):
            return self.prompt
        elif isinstance(self.prompt, str):  # ADD FUNCTIONALITY FOR USER OR SYSTEM PROMPT
            return [{"role": "user", "content": self.prompt}]
        else:
            raise ValueError("Prompt must be either a PromptVersion object or list of messages")

    def _extract_prompt_content(self) -> str:
        """Extract the main prompt content from messages"""
        messages = self._extract_prompt_messages()

        # Look for system or developer message first
        for message in messages:
            if message.get("role") in ["user"]:
                return message.get("content", "")

        # Fall back to first message
        if messages:
            return messages[0].get("content", "")

        raise ValueError("No valid prompt content found in messages. CURRENTLY ONLY CHECKING FOR USER PROMPT")

    def _detect_template_variables(self, prompt_content: str) -> list[str]:
        _TEMPLATE_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")
        """Return unique {placeholders} that look like template vars."""
        return list({m.group(1) for m in _TEMPLATE_RE.finditer(prompt_content)})

    def run_evaluators(
        self,
        dataset: Union[pd.DataFrame, str],
        evaluators: List[Callable],
        feedback_columns: List[str] = [],
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Run evaluators on the dataset and add results to feedback columns

        Returns:
            DataFrame with evaluator results added
        """
        dataset = self._load_dataset(dataset)
        self._validate_inputs(dataset, feedback_columns, evaluators)

        print(f"🔍 Running {len(evaluators)} evaluator(s)...")
        for i, evaluator in enumerate(evaluators):
            try:
                feedback_data, column_names = evaluator(dataset)
                for column_name in column_names:
                    dataset[column_name] = feedback_data[column_name]
                    feedback_columns.append(column_name)
                print(f"   ✅ Evaluator {i + 1}: {column_name}")
            except Exception as e:
                print(f"   ⚠️  Evaluator {i + 1} failed: {e}")

        return dataset, feedback_columns

    def _create_dummy_dataframe(self) -> pd.DataFrame:
        """Create dummy DataFrame for llm_generate to preserve template variables"""
        # Create a dummy df to outsmart the mapping done in phoenix
        # Should replace {var} with {var} so meta prompt is correct
        dummy_data = {
            "var": ["{var}"],  # Add hardcoded var column like in prompt_optimizer.py
        }
        for var in self.template_variables:
            dummy_data[var] = ["{" + var + "}"]

        return pd.DataFrame(dummy_data)

    def optimize(
        self,
        dataset: Union[pd.DataFrame, str],
        output_column: str,
        evaluators: List[Callable] = [],
        feedback_columns: List[str] = [],
        context_size_k: int = 8000,
    ) -> Union[PromptVersion, Sequence]:
        """
        Optimize the prompt using the meta-prompt approach

        Args:
            dataset: DataFrame or path to JSON file containing the dataset of requests, responses, and feedback to use for optimization
            output_column: Name of the column containing LLM outputs from the dataset
            feedback_columns: List of column names containing existing feedback from the dataset (required if not using new evaluations)
            evaluators: List of Phoenix evaluators to run on the dataset - see https://arize.com/docs/phoenix/evaluation/how-to-evals (default: [])
            context_size_k: Context window size in thousands of tokens (default: 8k)

        Returns:
            Optimized prompt in the same format as the input prompt
        """
        # Run evaluators if provided
        dataset = self._load_dataset(dataset)
        self._validate_inputs(dataset, feedback_columns, evaluators, output_column, output_required=True)
        if evaluators:
            dataset, feedback_columns = self.run_evaluators(dataset, evaluators, feedback_columns)

        # Extract prompt content
        prompt_content = self._extract_prompt_content()
        # Auto-detect template variables
        self.template_variables = self._detect_template_variables(prompt_content)

        # Initialize tiktoken splitter
        splitter = TiktokenSplitter(model=self.model_choice)

        # Determine which columns to include in token counting
        # columns_to_count = self.template_variables + self.feedback_columns + [self.output_column]
        columns_to_count = list(dataset.columns)

        # Create batches based on token count
        context_size_tokens = context_size_k
        batch_dataframes = splitter.get_batch_dataframes(dataset, columns_to_count, context_size_tokens)

        print(f"📊 Processing {len(dataset)} examples in {len(batch_dataframes)} batches")

        # Process dataset in batches
        optimized_prompt_content = prompt_content

        for i, batch in enumerate(batch_dataframes):

            try:

                # Construct meta-prompt content
                meta_prompt_content = self.meta_prompter.construct_content(
                    batch_df=batch,
                    prompt_to_optimize_content=optimized_prompt_content,
                    template_variables=self.template_variables,
                    feedback_columns=feedback_columns,
                    output_column=output_column,
                )

                model = OpenAIModel(
                    model=self.model_choice,
                    api_key=self.openai_api_key.get_secret_value(),
                )

                response = model(meta_prompt_content)

                potential_new_prompt = response

                # Validate that new prompt has same template variables

                print(f"   ✅ Batch {i + 1}/{len(batch_dataframes)}: Optimized")
                optimized_prompt_content = potential_new_prompt

            except Exception as e:
                print(f"   ❌ Batch {i + 1}/{len(batch_dataframes)}: Failed - {e}")
                continue

        # Create optimized prompt object
        optimized_prompt = self._create_optimized_prompt(optimized_prompt_content)
        return optimized_prompt

    def _create_optimized_prompt(self, optimized_content: str) -> Union[PromptVersion, Sequence]:
        """Create optimized prompt in the same format as input"""

        if isinstance(self.prompt, PromptVersion):
            # Create new Prompt object with optimized content
            original_messages = self._extract_prompt_messages()
            optimized_messages = copy.deepcopy(original_messages)

            # Replace the main content (system or first message)
            for i, message in enumerate(optimized_messages):
                if message.get("role") in ["user"]:  # ADD FUNCTIONALITY FOR SYSTEM PROMPT
                    optimized_messages[i]["content"] = optimized_content
                    break
            else:
                print("No user prompt found in the original prompt")

            # Create a new PromptVersion with optimized content
            return PromptVersion(
                optimized_messages,
                model_name=self.prompt._model_name,
                model_provider=self.prompt._model_provider,
                description=f"Optimized version of {getattr(self.prompt, 'name', 'prompt')}",
            )

        elif isinstance(self.prompt, list):
            # Return optimized messages list
            original_messages = self._extract_prompt_messages()
            optimized_messages = copy.deepcopy(original_messages)

            # Replace the main content
            for i, message in enumerate(optimized_messages):
                if message.get("role") in ["user"]:  # ADD FUNCTIONALITY FOR SYSTEM PROMPT
                    optimized_messages[i]["content"] = optimized_content
                    break
            else:
                print("No user prompt found in the original prompt")

            return optimized_messages

        elif isinstance(self.prompt, str):
            return optimized_content

        else:
            raise ValueError("Prompt must be either a PromptVersion object or list of messages or string")
