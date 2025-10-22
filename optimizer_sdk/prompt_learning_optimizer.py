import copy
import re
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union

import pandas as pd
from phoenix.client.types import PromptVersion
from phoenix.evals.models import OpenAIModel
from openai import APITimeoutError, APIError
from pyarrow._flight import FlightUnauthorizedError, FlightError

from .meta_prompt import MetaPrompt
from .tiktoken_splitter import TiktokenSplitter
from .utils import get_key_value
from .annotator import Annotator
import time
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score
from arize.experimental.prompt_hub import Prompt, LLMProvider


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

    def _call_llm_with_retry(
        self,
        model: OpenAIModel,
        prompt_content: str,
        max_retries: int = 5,
        initial_delay: float = 1.0,
        backoff_factor: float = 3.0,
    ) -> str:
        """
        Call LLM with exponential backoff retry logic.
        
        Args:
            model: OpenAIModel instance to call
            prompt_content: Prompt content to send
            max_retries: Maximum number of retry attempts (default: 5)
            initial_delay: Initial delay in seconds before first retry (default: 1.0)
            backoff_factor: Multiplier for delay after each retry (default: 3.0)
            
        Returns:
            str: Model response
            
        Raises:
            Exception: Re-raises the last exception if all retries fail
        """
        delay = initial_delay
        
        for attempt in range(max_retries + 1):  # +1 for the initial attempt
            try:
                response = model(prompt_content)
                return response
            except (APITimeoutError, APIError) as e:
                if attempt == max_retries:
                    # Last attempt failed, raise with clear message
                    print(f"❌ API call failed after {max_retries} retries")
                    raise Exception(f"API call failed after {max_retries} retries. Last error: {e}") from e
                
                # Calculate next delay
                next_delay = delay * backoff_factor if attempt > 0 else delay
                
                # Print retry information
                print(f"⚠️  API call failed (attempt {attempt + 1}/{max_retries + 1}): {type(e).__name__}: {str(e)}")
                print(f"   Retrying in {next_delay:.0f}s...")
                
                # Wait before retrying
                time.sleep(next_delay)
                delay = next_delay
            except Exception as e:
                # For other exceptions, fail immediately
                print(f"❌ Unexpected error during API call: {type(e).__name__}: {str(e)}")
                raise

    def _call_arize_with_retry(
        self,
        operation_callable: Callable,
        operation_name: str,
        *args,
        max_retries: int = 3,
        initial_delay: float = 2.0,
        backoff_factor: float = 2.0,
        **kwargs
    ):
        """
        Call Arize client operations with exponential backoff retry logic.
        
        Args:
            operation_callable: The Arize operation to call (e.g., arize_client.run_experiment)
            operation_name: Name of the operation for logging purposes
            *args: Positional arguments to pass to the operation
            max_retries: Maximum number of retry attempts (default: 3, keyword-only)
            initial_delay: Initial delay in seconds before first retry (default: 2.0, keyword-only)
            backoff_factor: Multiplier for delay after each retry (default: 2.0, keyword-only)
            **kwargs: Keyword arguments to pass to the operation
            
        Returns:
            Result from the Arize operation
            
        Raises:
            Exception: Re-raises the last exception if all retries fail
        """
        delay = initial_delay
        
        for attempt in range(max_retries + 1):  # +1 for the initial attempt
            try:
                result = operation_callable(*args, **kwargs)
                return result
            except (FlightUnauthorizedError, FlightError, RuntimeError, ConnectionError) as e:
                if attempt == max_retries:
                    # Last attempt failed, raise with clear message
                    print(f"❌ {operation_name} failed after {max_retries} retries")
                    raise Exception(f"{operation_name} failed after {max_retries} retries. Last error: {e}") from e
                
                # Calculate next delay
                next_delay = delay * backoff_factor if attempt > 0 else delay
                
                # Print retry information
                print(f"⚠️  {operation_name} failed (attempt {attempt + 1}/{max_retries + 1}): {type(e).__name__}: {str(e)}")
                print(f"   Retrying in {next_delay:.0f}s...")
                
                # Wait before retrying
                time.sleep(next_delay)
                delay = next_delay
            except Exception as e:
                # For other exceptions, fail immediately
                print(f"❌ Unexpected error during {operation_name}: {type(e).__name__}: {str(e)}")
                raise

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
    
    def create_annotation(
        self,
        prompt: str, 
        template_variables: List[str],
        dataset: Union[pd.DataFrame, str],
        feedback_columns: List[str],
        annotator_prompts: List[str],
        output_column: str,
        ground_truth_column: str = None,
    ) -> List[str]:
        """
        Create an annotation for the dataset using the annotator
        """
        dataset = self._load_dataset(dataset)
        self._validate_inputs(dataset, feedback_columns)
        annotations = []
        print(f"🔍 Running annotator...")
        for i, annotator_prompt in enumerate(annotator_prompts):
            try:
                annotator = Annotator(annotator_prompt)
                prompt = annotator.construct_content(dataset, prompt, template_variables, feedback_columns, output_column, ground_truth_column)
                annotation = annotator.generate_annotation(prompt)
                annotations.append(annotation)
            except Exception as e:
                print(f"   ⚠️  Annotator {i + 1} failed: {e}")
        return annotations


    def optimize(
        self,
        dataset: Union[pd.DataFrame, str],
        output_column: str,
        evaluators: List[Callable] = [],
        feedback_columns: List[str] = [],
        annotations: List[str] = [],
        ruleset: str = "",
        context_size_k: int = 128000,
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
        print(columns_to_count)

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
                    annotations=annotations,
                    ruleset=ruleset,
                )

                model = OpenAIModel(
                    model=self.model_choice,
                    api_key=self.openai_api_key.get_secret_value(),
                )

                response = self._call_llm_with_retry(model, meta_prompt_content)

                if ruleset:
                    ruleset = response
                else:
                    potential_new_prompt = response
                    # Validate that new prompt has same template variables
                    print(f"   ✅ Batch {i + 1}/{len(batch_dataframes)}: Optimized")
                    optimized_prompt_content = potential_new_prompt

            except Exception as e:
                print(f"   ❌ Batch {i + 1}/{len(batch_dataframes)}: Failed - {e}")
                continue

        if ruleset:
            return ruleset
        optimized_prompt = self._create_optimized_prompt(optimized_prompt_content)
        return optimized_prompt

    def optimize_with_experiments(
        self,
        train_dataset: pd.DataFrame,
        test_dataset: pd.DataFrame,
        train_dataset_id: str,
        test_dataset_id: str,
        evaluators: List[Callable],
        test_evaluator: Callable,
        task_fn: Callable,
        arize_client,
        arize_space_id: str,
        experiment_name_prefix: str,
        prompt_hub_client,
        prompt_name: str,
        model_name: str,
        feedback_columns: List[str],
        annotations_prompt_path: str = None,
        threshold: float = 1.0,
        loops: int = 5,
        scorer: str = "accuracy",
        context_size_k: int = 90000,
    ) -> Union[PromptVersion, Sequence, str]:
        """
        Optimize the prompt with full experiment workflow including sampling, evaluation, and iteration.
        
        This method handles the complete optimization pipeline:
        1. Pre-samples training data to fit context window (efficient!)
        2. Runs experiments with evaluators on sampled data
        3. Iteratively optimizes the prompt
        4. Tests each iteration on held-out test set
        5. Uploads prompt versions to Arize Prompt Hub
        
        Args:
            train_dataset: Training dataset DataFrame
            test_dataset: Test dataset DataFrame
            train_dataset_id: Arize dataset ID for training data
            test_dataset_id: Arize dataset ID for test data
            evaluators: List of evaluators to run on training data (e.g., [output_evaluator])
            test_evaluator: Evaluator to run on test data
            task_fn: Function that takes system_prompt and returns an async task function
            arize_client: ArizeDatasetsClient instance
            arize_space_id: Arize space ID
            experiment_name_prefix: Prefix for experiment names (loop number will be appended)
            prompt_hub_client: ArizePromptClient instance
            prompt_name: Name for prompt in Arize Prompt Hub
            model_name: Model name for the task
            feedback_columns: List of feedback column names to extract
            annotations_prompt_path: Path to annotations prompt file (optional, default: None)
            threshold: Performance threshold to stop optimization (default: 1.0)
            loops: Maximum number of optimization iterations (default: 5)
            scorer: Metric to use for evaluation (default: "accuracy")
            context_size_k: Context window size in tokens for sampling (default: 90000)
            
        Returns:
            Optimized prompt in the same format as the input prompt
        """
        print(f"🚀 Starting prompt optimization with {loops} iterations (scorer: {scorer}, threshold: {threshold})")
        
        # Initialize optimization results tracking
        optimization_results = []
        
        # Extract initial prompt content
        initial_prompt_content = self._extract_prompt_content()
        current_prompt_content = initial_prompt_content
        
        # Run initial evaluation on test set
        print(f"\n📊 Initial evaluation:")
        print(f"⏳ Running initial evaluation experiment...")
        task = task_fn(current_prompt_content)
        
        initial_experiment_id, _ = self._call_arize_with_retry(
            arize_client.run_experiment,
            "Initial evaluation experiment",
            space_id=arize_space_id,
            dataset_id=test_dataset_id,
            task=task,
            evaluators=[test_evaluator],
            experiment_name=f"{experiment_name_prefix}_initial",
            concurrency=10
        )
        
        print(f"⏳ Retrieving experiment results...")
        time.sleep(3)
        
        initial_metric_value = self._compute_metric(
            arize_client, arize_space_id, initial_experiment_id, 
            "eval.test_evaluator.score", scorer
        )
        print(f"✅ Initial {scorer}: {initial_metric_value:.3f}")
        
        # Upload initial prompt to Prompt Hub
        print(f"⏳ Uploading initial prompt version to Prompt Hub...")
        prompt_version_id = self._add_prompt_version(
            prompt_hub_client, current_prompt_content, prompt_name, 
            model_name, initial_metric_value, 0
        )
        print(f"✅ Uploaded to Prompt Hub")
        
        if initial_metric_value >= threshold:
            print("\n🎉 Initial prompt already meets threshold!")
            return self._create_optimized_prompt(current_prompt_content)
        
        # Calculate sampling parameters once
        splitter = TiktokenSplitter(model=self.model_choice)
        columns_to_count = list(train_dataset.columns)
        max_rows = splitter.get_max_rows_for_context(train_dataset, columns_to_count, context_size_k)
        print(f"🔢 Maximum number of rows for training context: {max_rows}")
        
        should_sample = len(train_dataset) > max_rows
        if should_sample:
            print(f"🔧 EFFICIENCY SETUP: Will sample {max_rows} examples from {len(train_dataset)} total training examples each loop")
            print(f"   💰 This saves ~{(len(train_dataset) - max_rows) * len(evaluators)} evaluator calls per loop!")
        else:
            print(f"📊 Training dataset ({len(train_dataset)} examples) fits within context window")
        
        # Main optimization loop
        curr_loop = 1
        train_df = train_dataset.copy()
        threshold_met = False
        
        while loops > 0:
            print(f"\n{'='*80}")
            print(f"📊 Loop {curr_loop}: Optimizing prompt...")
            print(f"{'='*80}")
            
            # Sample training data if needed
            if should_sample:
                train_df_to_process = train_df.sample(n=max_rows).reset_index(drop=True)
                print(f"   🎲 Sampled {len(train_df_to_process)} examples for this loop")
            else:
                train_df_to_process = train_df
            
            # Run training experiment
            print(f"⏳ Running training experiment...")
            task = task_fn(current_prompt_content)
            train_experiment_id, _ = self._call_arize_with_retry(
                arize_client.run_experiment,
                f"Training experiment (loop {curr_loop})",
                space_id=arize_space_id,
                experiment_name=f"{experiment_name_prefix}_train_loop_{curr_loop}",
                task=task,
                dataset_df=train_df_to_process,  # Pass sampled dataframe
                dataset_id=train_dataset_id,  # Still provide dataset_id for reference
                evaluators=evaluators + [test_evaluator],
                concurrency=10
            )
            
            print(f"⏳ Retrieving training experiment results...")
            time.sleep(3)
            
            # Compute training metric
            train_metric = self._compute_metric(
                arize_client, arize_space_id, train_experiment_id,
                "eval.output_evaluator.score", "accuracy"
            )
            print(f"✅ Training {scorer}: {train_metric:.3f}")
            
            # Process experiment results to get feedback
            print(f"⏳ Processing experiment results and extracting feedback...")
            train_df_with_feedback = self._process_experiment(
                arize_client, arize_space_id, train_experiment_id,
                train_df_to_process, "query", "output", feedback_columns
            )
            
            # Detect template variables (needed for optimization)
            self.template_variables = self._detect_template_variables(current_prompt_content)
            
            # Create annotations if path is provided
            annotations_list = []
            if annotations_prompt_path is not None:
                print(f"⏳ Generating annotations...")
                with open(annotations_prompt_path, "r") as file:
                    annotations_prompt = file.read()
                
                annotator = Annotator(annotations_prompt)
                annotation = annotator.generate_annotation(
                    annotator.construct_content(
                        train_df_with_feedback, current_prompt_content,
                        self.template_variables, feedback_columns, "output", "ground_truth"
                    )
                )
                annotations_list = [annotation]
            
            # Optimize the prompt
            print(f"⏳ Optimizing prompt with meta-prompt...")
            current_prompt_content = self._optimize_single_batch(
                train_df_with_feedback, "output", feedback_columns, annotations_list, current_prompt_content
            )
            print(f"✅ Prompt optimization complete")
            
            # Run test experiment
            print(f"⏳ Running test evaluation experiment...")
            test_experiment_id, _ = self._call_arize_with_retry(
                arize_client.run_experiment,
                f"Test evaluation experiment (loop {curr_loop})",
                space_id=arize_space_id,
                dataset_id=test_dataset_id,
                task=task_fn(current_prompt_content),
                evaluators=[test_evaluator],
                experiment_name=f"{experiment_name_prefix}_test_loop_{curr_loop}",
                concurrency=10
            )
            
            print(f"⏳ Retrieving test experiment results...")
            time.sleep(3)
            
            # Compute test metric
            test_metric = self._compute_metric(
                arize_client, arize_space_id, test_experiment_id,
                "eval.test_evaluator.score", scorer
            )
            print(f"✅ Test {scorer}: {test_metric:.3f}")
            
            # Upload prompt version to Prompt Hub
            print(f"⏳ Uploading prompt version to Prompt Hub...")
            prompt_version_id = self._add_prompt_version(
                prompt_hub_client, current_prompt_content, prompt_name,
                model_name, test_metric, curr_loop
            )
            print(f"✅ Uploaded to Prompt Hub")
            
            # Track results for this loop
            loop_result = {
                'loop_id': curr_loop,
                'train_experiment_id': train_experiment_id,
                'test_experiment_id': test_experiment_id,
                'train_metric': train_metric,
                'test_metric': test_metric,
                'prompt_version_id': prompt_version_id,
                'initial_test_experiment_id': initial_experiment_id if curr_loop == 1 else None
            }
            optimization_results.append(loop_result)
            
            # Check if threshold met
            if test_metric >= threshold:
                print("\n🎉 Prompt optimization met threshold!")
                threshold_met = True
                break
            
            loops -= 1
            curr_loop += 1
        
        # Display optimization summary
        final_metric = optimization_results[-1]['test_metric'] if optimization_results else initial_metric_value
        self._print_optimization_summary(
            optimization_results=optimization_results,
            initial_metric=initial_metric_value,
            final_metric=final_metric,
            scorer=scorer,
            prompt_name=prompt_name,
            threshold_met=threshold_met
        )
        
        return self._create_optimized_prompt(current_prompt_content)
    
    def optimize_with_experiments_batched(
        self,
        train_dataset: pd.DataFrame,
        test_dataset: pd.DataFrame,
        train_dataset_id: str,
        test_dataset_id: str,
        evaluators: List[Callable],
        test_evaluator: Callable,
        task_fn: Callable,
        arize_client,
        arize_space_id: str,
        experiment_name_prefix: str,
        prompt_hub_client,
        prompt_name: str,
        model_name: str,
        feedback_columns: List[str],
        annotations_prompt_path: str = None,
        threshold: float = 1.0,
        loops: int = 5,
        scorer: str = "accuracy",
        context_size_k: int = 90000,
    ) -> Union[PromptVersion, Sequence, str]:
        """
        Optimize the prompt with batched processing that ensures all training examples are used.
        
        This method processes all training data in batches within each loop:
        1. Shuffles training data at the start of each loop
        2. Splits data into batches based on context window size
        3. For each batch: run experiment → optimize → test → upload
        4. Continues outer loops until threshold met or max loops reached
        
        Args:
            train_dataset: Training dataset DataFrame
            test_dataset: Test dataset DataFrame
            train_dataset_id: Arize dataset ID for training data
            test_dataset_id: Arize dataset ID for test data
            evaluators: List of evaluators to run on training data (e.g., [output_evaluator])
            test_evaluator: Evaluator to run on test data
            task_fn: Function that takes system_prompt and returns an async task function
            arize_client: ArizeDatasetsClient instance
            arize_space_id: Arize space ID
            experiment_name_prefix: Prefix for experiment names
            prompt_hub_client: ArizePromptClient instance
            prompt_name: Name for prompt in Arize Prompt Hub
            model_name: Model name for the task
            feedback_columns: List of feedback column names to extract
            annotations_prompt_path: Path to annotations prompt file (optional, default: None)
            threshold: Performance threshold to stop optimization (default: 1.0)
            loops: Maximum number of optimization iterations (default: 5)
            scorer: Metric to use for evaluation (default: "accuracy")
            context_size_k: Context window size in tokens for batching (default: 90000)
            
        Returns:
            Optimized prompt in the same format as the input prompt
        """
        print(f"🚀 Starting batched prompt optimization with {loops} outer loops (scorer: {scorer}, threshold: {threshold})")
        
        # Initialize optimization results tracking
        optimization_results = []
        
        # Extract initial prompt content
        initial_prompt_content = self._extract_prompt_content()
        current_prompt_content = initial_prompt_content
        
        # Run initial evaluation on test set
        print(f"\n📊 Initial evaluation:")
        print(f"⏳ Running initial evaluation experiment...")
        task = task_fn(current_prompt_content)
        
        initial_experiment_id, _ = self._call_arize_with_retry(
            arize_client.run_experiment,
            "Initial evaluation experiment",
            space_id=arize_space_id,
            dataset_id=test_dataset_id,
            task=task,
            evaluators=[test_evaluator],
            experiment_name=f"{experiment_name_prefix}_initial",
            concurrency=10
        )
        
        print(f"⏳ Retrieving experiment results...")
        time.sleep(3)
        
        initial_metric_value = self._compute_metric(
            arize_client, arize_space_id, initial_experiment_id, 
            "eval.test_evaluator.score", scorer
        )
        print(f"✅ Initial {scorer}: {initial_metric_value:.3f}")
        
        # Upload initial prompt to Prompt Hub
        print(f"⏳ Uploading initial prompt version to Prompt Hub...")
        prompt_version_id = self._add_prompt_version(
            prompt_hub_client, current_prompt_content, prompt_name, 
            model_name, initial_metric_value, 0
        )
        print(f"✅ Uploaded to Prompt Hub")
        
        if initial_metric_value >= threshold:
            print("\n🎉 Initial prompt already meets threshold!")
            return self._create_optimized_prompt(current_prompt_content)
        
        # Calculate batch size once
        splitter = TiktokenSplitter(model=self.model_choice)
        columns_to_count = list(train_dataset.columns)
        max_rows = splitter.get_max_rows_for_context(train_dataset, columns_to_count, context_size_k)
        print(f"🔧 Calculated max rows for context: {max_rows} rows fit within {context_size_k:,} tokens")
        print(f"🔢 Will process {len(train_dataset)} training examples in batches of ~{max_rows} rows")
        
        # Main optimization loop
        curr_loop = 1
        train_df = train_dataset.copy()
        threshold_met = False
        batch_counter = 0  # Global counter for unique batch IDs
        
        while loops > 0:
            print(f"\n{'='*80}")
            print(f"📊 Loop {curr_loop}: Processing all training data in batches...")
            print(f"{'='*80}")
            
            # Shuffle training data at the start of each loop
            train_df_shuffled = train_df.sample(frac=1).reset_index(drop=True)
            
            # Split into batches
            num_batches = (len(train_df_shuffled) + max_rows - 1) // max_rows  # Ceiling division
            print(f"   🔀 Shuffled {len(train_df_shuffled)} examples into {num_batches} batches")
            
            # Process each batch
            for batch_idx in range(num_batches):
                batch_counter += 1
                start_idx = batch_idx * max_rows
                end_idx = min(start_idx + max_rows, len(train_df_shuffled))
                batch_df = train_df_shuffled.iloc[start_idx:end_idx].reset_index(drop=True)
                
                print(f"\n   📦 Batch {batch_idx + 1}/{num_batches} (rows {start_idx}-{end_idx-1}, {len(batch_df)} examples)")
                
                # Run training experiment on this batch
                print(f"   ⏳ Running training experiment...")
                task = task_fn(current_prompt_content)
                train_experiment_id, _ = self._call_arize_with_retry(
                    arize_client.run_experiment,
                    f"Training experiment (loop {curr_loop}, batch {batch_idx + 1})",
                    space_id=arize_space_id,
                    experiment_name=f"{experiment_name_prefix}_train_L{curr_loop}_B{batch_idx + 1}",
                    task=task,
                    dataset_df=batch_df,
                    dataset_id=train_dataset_id,
                    evaluators=evaluators + [test_evaluator],
                    concurrency=10
                )
                
                print(f"   ⏳ Retrieving training experiment results...")
                time.sleep(3)
                
                # Compute training metric
                train_metric = self._compute_metric(
                    arize_client, arize_space_id, train_experiment_id,
                    "eval.output_evaluator.score", "accuracy"
                )
                print(f"   ✅ Training {scorer}: {train_metric:.3f}")
                
                # Process experiment results to get feedback
                print(f"   ⏳ Processing experiment results and extracting feedback...")
                batch_df_with_feedback = self._process_experiment(
                    arize_client, arize_space_id, train_experiment_id,
                    batch_df, "query", "output", feedback_columns
                )
                
                # Detect template variables
                self.template_variables = self._detect_template_variables(current_prompt_content)
                
                # Create annotations if path is provided
                annotations_list = []
                if annotations_prompt_path is not None:
                    with open(annotations_prompt_path, "r") as file:
                        annotations_prompt = file.read()
                    
                    annotator = Annotator(annotations_prompt)
                    annotation = annotator.generate_annotation(
                        annotator.construct_content(
                            batch_df_with_feedback, current_prompt_content,
                            self.template_variables, feedback_columns, "output", "ground_truth"
                        )
                    )
                    annotations_list = [annotation]
                
                # Optimize the prompt
                print(f"   ⏳ Optimizing prompt with meta-prompt...")
                current_prompt_content = self._optimize_single_batch(
                    batch_df_with_feedback, "output", feedback_columns, annotations_list, current_prompt_content
                )
                print(f"   ✅ Prompt optimization complete")
                
                # Run test experiment
                print(f"   ⏳ Running test evaluation experiment...")
                test_experiment_id, _ = self._call_arize_with_retry(
                    arize_client.run_experiment,
                    f"Test evaluation experiment (loop {curr_loop}, batch {batch_idx + 1})",
                    space_id=arize_space_id,
                    dataset_id=test_dataset_id,
                    task=task_fn(current_prompt_content),
                    evaluators=[test_evaluator],
                    experiment_name=f"{experiment_name_prefix}_test_L{curr_loop}_B{batch_idx + 1}",
                    concurrency=10
                )
                
                print(f"   ⏳ Retrieving test experiment results...")
                time.sleep(3)
                
                # Compute test metric
                test_metric = self._compute_metric(
                    arize_client, arize_space_id, test_experiment_id,
                    "eval.test_evaluator.score", scorer
                )
                print(f"   ✅ Test {scorer}: {test_metric:.3f}")
                
                # Upload prompt version to Prompt Hub
                print(f"   ⏳ Uploading prompt version to Prompt Hub...")
                prompt_version_id = self._add_prompt_version(
                    prompt_hub_client, current_prompt_content, prompt_name,
                    model_name, test_metric, batch_counter
                )
                print(f"   ✅ Uploaded to Prompt Hub")
                
                # Track results for this batch
                loop_result = {
                    'loop_id': curr_loop,
                    'batch_id': batch_idx + 1,
                    'total_batches': num_batches,
                    'batch_size': len(batch_df),
                    'train_experiment_id': train_experiment_id,
                    'test_experiment_id': test_experiment_id,
                    'train_metric': train_metric,
                    'test_metric': test_metric,
                    'prompt_version_id': prompt_version_id,
                    'initial_test_experiment_id': initial_experiment_id if curr_loop == 1 and batch_idx == 0 else None
                }
                optimization_results.append(loop_result)
                
                # Check if threshold met
                if test_metric >= threshold:
                    print(f"\n🎉 Prompt optimization met threshold after batch {batch_idx + 1}!")
                    threshold_met = True
                    break
            
            # Break outer loop if threshold was met
            if threshold_met:
                break
            
            loops -= 1
            curr_loop += 1
        
        # Display optimization summary
        final_metric = optimization_results[-1]['test_metric'] if optimization_results else initial_metric_value
        self._print_batched_optimization_summary(
            optimization_results=optimization_results,
            initial_metric=initial_metric_value,
            final_metric=final_metric,
            scorer=scorer,
            prompt_name=prompt_name,
            threshold_met=threshold_met
        )
        
        return self._create_optimized_prompt(current_prompt_content)
    
    def _optimize_single_batch(
        self,
        dataset: pd.DataFrame,
        output_column: str,
        feedback_columns: List[str],
        annotations: List[str],
        current_prompt_content: str,
    ) -> str:
        """Helper method to optimize a single batch of data"""
        meta_prompt_content = self.meta_prompter.construct_content(
            batch_df=dataset,
            prompt_to_optimize_content=current_prompt_content,
            template_variables=self.template_variables,
            feedback_columns=feedback_columns,
            output_column=output_column,
            annotations=annotations,
            ruleset="",
        )
        
        model = OpenAIModel(
            model=self.model_choice,
            api_key=self.openai_api_key.get_secret_value(),
        )
        
        response = self._call_llm_with_retry(model, meta_prompt_content)
        return response
    
    def _compute_metric(
        self,
        arize_client,
        space_id: str,
        experiment_id: str,
        prediction_column_name: str,
        scorer: str = "accuracy",
        average: str = "macro"
    ) -> float:
        """Compute classification metric from an Arize experiment"""
        experiment_df = self._call_arize_with_retry(
            arize_client.get_experiment,
            "Get experiment results",
            space_id,
            experiment_id=experiment_id
        )
        
        y_pred = experiment_df[prediction_column_name]
        y_true = [1] * len(experiment_df)
        
        if scorer == "accuracy":
            return accuracy_score(y_true, y_pred)
        elif scorer == "f1":
            return f1_score(y_true, y_pred, zero_division=0, average=average)
        elif scorer == "precision":
            return precision_score(y_true, y_pred, zero_division=0, average=average)
        elif scorer == "recall":
            return recall_score(y_true, y_pred, zero_division=0, average=average)
        else:
            raise ValueError(f"Unknown scorer: {scorer}")
    
    def _process_experiment(
        self,
        arize_client,
        space_id: str,
        experiment_id: str,
        train_set: pd.DataFrame,
        input_column_name: str,
        output_column_name: str,
        feedback_columns: List[str]
    ) -> pd.DataFrame:
        """Process experiment results and extract feedback into dataframe"""
        experiment_df = self._call_arize_with_retry(
            arize_client.get_experiment,
            "Get experiment results for processing",
            space_id,
            experiment_id=experiment_id
        )
        
        train_set_with_experiment_results = pd.merge(
            train_set, experiment_df, left_on='id', right_on='example_id', how='inner'
        )
        
        # Initialize feedback columns
        for column in feedback_columns:
            train_set[column] = [None] * len(train_set)
        
        # Extract feedback from experiment results
        for idx, row in train_set_with_experiment_results.iterrows():
            index = row["example_id"]
            eval_output = row["eval.output_evaluator.explanation"]
            if feedback_columns:
                for item in eval_output.split(";"):
                    key_value = item.split(":")
                    if len(key_value) >= 2 and key_value[0].strip() in feedback_columns:
                        key, value = key_value[0].strip(), key_value[1].strip()
                        train_set.loc[train_set["id"] == index, key] = value
        
        train_set[output_column_name] = train_set_with_experiment_results["result"]
        train_set.rename(columns={"query": input_column_name}, inplace=True)
        
        return train_set
    
    def _print_optimization_summary(
        self,
        optimization_results: List[Dict],
        initial_metric: float,
        final_metric: float,
        scorer: str,
        prompt_name: str,
        threshold_met: bool = False
    ):
        """
        Display a professional summary of the optimization results
        
        Args:
            optimization_results: List of dictionaries containing loop results
            initial_metric: Initial test metric value
            final_metric: Final test metric value
            scorer: Name of the metric used
            prompt_name: Name of the prompt in Prompt Hub
            threshold_met: Whether the threshold was met
        """
        print("\n")
        print("╔════════════════════════════════════════════════════════════════════════════════╗")
        print("║                      PROMPT OPTIMIZATION SUMMARY                               ║")
        print("╚════════════════════════════════════════════════════════════════════════════════╝")
        print()
        
        # Summary statistics
        num_iterations = len(optimization_results)
        improvement = ((final_metric - initial_metric) / initial_metric * 100) if initial_metric > 0 else 0
        
        if threshold_met:
            print(f"✓ Optimization completed successfully - threshold met after {num_iterations} iteration(s)")
        else:
            print(f"Optimization completed after {num_iterations} iteration(s)")
        
        print(f"Final test {scorer}: {final_metric:.3f}")
        print(f"Improvement over baseline: {improvement:+.1f}%")
        print()
        
        # Table header
        print("┌──────┬─────────────┬─────────────┬──────────────────┬──────────────────┐")
        print("│ Loop │ Train Acc   │ Test Acc    │ Train Exp ID     │ Test Exp ID      │")
        print("├──────┼─────────────┼─────────────┼──────────────────┼──────────────────┤")
        
        # Initial row
        initial_train_id = optimization_results[0].get('train_experiment_id', '-') if optimization_results else '-'
        initial_test_id = optimization_results[0].get('initial_test_experiment_id', '-') if optimization_results else '-'
        print(f"│  {0:2d}  │      -      │   {initial_metric:.3f}     │        -         │ {self._truncate_id(initial_test_id):16s} │")
        
        # Results rows
        for result in optimization_results:
            loop_id = result.get('loop_id', 0)
            train_metric = result.get('train_metric', 0)
            test_metric = result.get('test_metric', 0)
            train_exp_id = self._truncate_id(result.get('train_experiment_id', '-'))
            test_exp_id = self._truncate_id(result.get('test_experiment_id', '-'))
            
            print(f"│  {loop_id:2d}  │   {train_metric:.3f}     │   {test_metric:.3f}     │ {train_exp_id:16s} │ {test_exp_id:16s} │")
        
        # Table footer
        print("└──────┴─────────────┴─────────────┴──────────────────┴──────────────────┘")
        print()
        print(f"All prompt versions have been uploaded to Arize Prompt Hub: {prompt_name}")
        print()
    
    def _truncate_id(self, exp_id: str, max_length: int = 16) -> str:
        """Truncate experiment ID to fit in table cell"""
        if exp_id == '-':
            return '-'
        if len(exp_id) <= max_length:
            return exp_id
        return exp_id[:max_length-3] + '...'
    
    def _print_batched_optimization_summary(
        self,
        optimization_results: List[Dict],
        initial_metric: float,
        final_metric: float,
        scorer: str,
        prompt_name: str,
        threshold_met: bool = False
    ):
        """
        Display a professional summary of the batched optimization results.
        Shows each batch as a separate row with loop and batch information.
        
        Args:
            optimization_results: List of dictionaries containing batch results
            initial_metric: Initial test metric value
            final_metric: Final test metric value
            scorer: Name of the metric used
            prompt_name: Name of the prompt in Prompt Hub
            threshold_met: Whether the threshold was met
        """
        print("\n")
        print("╔════════════════════════════════════════════════════════════════════════════════╗")
        print("║                  BATCHED PROMPT OPTIMIZATION SUMMARY                           ║")
        print("╚════════════════════════════════════════════════════════════════════════════════╝")
        print()
        
        # Summary statistics
        num_batches_processed = len(optimization_results)
        improvement = ((final_metric - initial_metric) / initial_metric * 100) if initial_metric > 0 else 0
        
        if threshold_met:
            print(f"✓ Optimization completed successfully - threshold met after {num_batches_processed} batch(es)")
        else:
            print(f"Optimization completed after {num_batches_processed} batch(es)")
        
        print(f"Final test {scorer}: {final_metric:.3f}")
        print(f"Improvement over baseline: {improvement:+.1f}%")
        print()
        
        # Table header
        print("┌──────┬─────────┬─────────────┬─────────────┬──────────────────┬──────────────────┐")
        print("│ Loop │ Batch   │ Train Acc   │ Test Acc    │ Train Exp ID     │ Test Exp ID      │")
        print("├──────┼─────────┼─────────────┼─────────────┼──────────────────┼──────────────────┤")
        
        # Initial row
        initial_test_id = optimization_results[0].get('initial_test_experiment_id', '-') if optimization_results else '-'
        print(f"│  {0:2d}  │    -    │      -      │   {initial_metric:.3f}     │        -         │ {self._truncate_id(initial_test_id):16s} │")
        
        # Results rows - show each batch
        for result in optimization_results:
            loop_id = result.get('loop_id', 0)
            batch_id = result.get('batch_id', 0)
            total_batches = result.get('total_batches', 0)
            train_metric = result.get('train_metric', 0)
            test_metric = result.get('test_metric', 0)
            train_exp_id = self._truncate_id(result.get('train_experiment_id', '-'))
            test_exp_id = self._truncate_id(result.get('test_experiment_id', '-'))
            
            # Format batch as "1/5", "2/5", etc.
            batch_str = f"{batch_id}/{total_batches}"
            
            print(f"│  {loop_id:2d}  │  {batch_str:5s}  │   {train_metric:.3f}     │   {test_metric:.3f}     │ {train_exp_id:16s} │ {test_exp_id:16s} │")
        
        # Table footer
        print("└──────┴─────────┴─────────────┴─────────────┴──────────────────┴──────────────────┘")
        print()
        print(f"All prompt versions have been uploaded to Arize Prompt Hub: {prompt_name}")
        print()
    
    def _add_prompt_version(
        self,
        prompt_hub_client,
        system_prompt: str,
        prompt_name: str,
        model_name: str,
        test_metric: float,
        loop_number: int
    ) -> Optional[str]:
        """
        Upload prompt version to Arize Prompt Hub
        
        Returns:
            Optional[str]: Prompt version ID if successful, None otherwise
        """
        try:
            existing_prompt = prompt_hub_client.pull_prompt(prompt_name=prompt_name)
            existing_prompt.messages = [{"role": "system", "content": system_prompt}]
            existing_prompt.commit_message = f"Loop {loop_number} - Test Metric: {test_metric:.3f}"
            prompt_hub_client.push_prompt(existing_prompt, commit_message=existing_prompt.commit_message)
            return f"{prompt_name}_v{loop_number}"
        except Exception:
            new_prompt = Prompt(
                name=prompt_name,
                model_name=model_name,
                messages=[{"role": "system", "content": system_prompt}],
                provider=LLMProvider.OPENAI,
            )
            new_prompt.commit_message = f"Loop {loop_number}\nTest Metric: {test_metric:.3f}"
            prompt_hub_client.push_prompt(new_prompt, commit_message=new_prompt.commit_message)
            return f"{prompt_name}_v{loop_number}"

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