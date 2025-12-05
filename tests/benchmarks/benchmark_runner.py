"""
Performance benchmark runner for prompt learning SDK.
"""

import time
import tracemalloc
import pandas as pd
import numpy as np
import sys
import os
from typing import List, Dict, Any
from dataclasses import dataclass

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from interfaces.token_counter import TiktokenCounter, ApproximateCounter
from core.dataset_splitter import DatasetSplitter


@dataclass
class BenchmarkResult:
    """Store benchmark results."""
    test_name: str
    execution_time_ms: float
    memory_usage_mb: float
    rows_processed: int
    tokens_processed: int


class DatasetGenerator:
    """Generate test datasets for benchmarking."""
    
    @staticmethod
    def create_test_dataset(num_rows: int, num_cols: int, avg_tokens_per_cell: int) -> pd.DataFrame:
        """Create synthetic dataset for testing."""
        np.random.seed(42)  # Reproducible results
        
        data = {}
        for col in range(num_cols):
            # Generate text with approximately avg_tokens_per_cell tokens
            # Using ~4 chars per token average
            texts = []
            for _ in range(num_rows):
                char_count = int(np.random.normal(avg_tokens_per_cell * 4, avg_tokens_per_cell))
                char_count = max(10, char_count)  # Minimum 10 characters
                text = 'x' * char_count  # Simple repeated character
                texts.append(text)
            
            data[f'col_{col}'] = texts
        
        # Add feedback columns
        data['feedback'] = ['positive'] * (num_rows // 2) + ['negative'] * (num_rows // 2)
        data['output'] = ['sample output'] * num_rows
        
        return pd.DataFrame(data)


class PerformanceBenchmark:
    """Run performance benchmarks on SDK components."""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
    
    def benchmark_token_counting(
        self, 
        counter_class, 
        df: pd.DataFrame, 
        columns: List[str],
        test_name: str
    ) -> BenchmarkResult:
        """Benchmark token counting performance."""
        
        # Initialize counter
        if counter_class == TiktokenCounter:
            counter = TiktokenCounter()
        else:
            counter = counter_class()
        
        # Start memory tracking
        tracemalloc.start()
        start_time = time.perf_counter()
        
        # Run token counting
        token_counts = counter.count_dataframe_tokens(df, columns)
        
        # Measure results
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        execution_time_ms = (end_time - start_time) * 1000
        memory_usage_mb = peak / (1024 * 1024)
        total_tokens = sum(token_counts)
        
        result = BenchmarkResult(
            test_name=test_name,
            execution_time_ms=execution_time_ms,
            memory_usage_mb=memory_usage_mb,
            rows_processed=len(df),
            tokens_processed=total_tokens
        )
        
        self.results.append(result)
        return result
    
    def benchmark_batch_splitting(
        self,
        df: pd.DataFrame,
        columns: List[str], 
        max_tokens: int,
        test_name: str
    ) -> BenchmarkResult:
        """Benchmark dataset splitting performance."""
        
        # Use approximate counter for speed
        counter = ApproximateCounter()
        splitter = DatasetSplitter(counter)
        
        # Start memory tracking
        tracemalloc.start()
        start_time = time.perf_counter()
        
        # Run batch splitting
        batches = splitter.split_into_batches(df, columns, max_tokens)
        
        # Measure results
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        execution_time_ms = (end_time - start_time) * 1000
        memory_usage_mb = peak / (1024 * 1024)
        
        result = BenchmarkResult(
            test_name=test_name,
            execution_time_ms=execution_time_ms,
            memory_usage_mb=memory_usage_mb,
            rows_processed=len(df),
            tokens_processed=sum(len(batch) for batch in batches)
        )
        
        self.results.append(result)
        return result
    
    def run_comprehensive_benchmark(self) -> Dict[str, List[BenchmarkResult]]:
        """Run all benchmarks across different dataset sizes."""
        
        # Test scenarios
        scenarios = [
            ("small", 100, 5, 50),
            ("medium", 1000, 10, 100), 
            ("large", 10000, 15, 200)
        ]
        
        results_by_category = {
            "token_counting": [],
            "batch_splitting": []
        }
        
        for scenario_name, num_rows, num_cols, avg_tokens in scenarios:
            print(f"\\n🔍 Running {scenario_name} dataset benchmark...")
            print(f"   Dataset: {num_rows} rows × {num_cols} cols × {avg_tokens} avg tokens")
            
            # Generate test data
            df = DatasetGenerator.create_test_dataset(num_rows, num_cols, avg_tokens)
            columns = [col for col in df.columns if col.startswith('col_')]
            
            # Token counting benchmarks
            tiktoken_result = self.benchmark_token_counting(
                TiktokenCounter, df, columns,
                f"{scenario_name}_tiktoken_counting"
            )
            
            approx_result = self.benchmark_token_counting(
                ApproximateCounter, df, columns, 
                f"{scenario_name}_approximate_counting"
            )
            
            # Batch splitting benchmark
            batch_result = self.benchmark_batch_splitting(
                df, columns, 32000,
                f"{scenario_name}_batch_splitting"
            )
            
            results_by_category["token_counting"].extend([tiktoken_result, approx_result])
            results_by_category["batch_splitting"].append(batch_result)
            
            # Print immediate results
            print(f"   TikToken: {tiktoken_result.execution_time_ms:.1f}ms, {tiktoken_result.memory_usage_mb:.1f}MB")
            print(f"   Approximate: {approx_result.execution_time_ms:.1f}ms, {approx_result.memory_usage_mb:.1f}MB") 
            print(f"   Batch Split: {batch_result.execution_time_ms:.1f}ms, {batch_result.memory_usage_mb:.1f}MB")
        
        return results_by_category
    
    def save_results(self, filename: str = "tests/benchmarks/baseline_results.md"):
        """Save benchmark results to markdown file."""
        
        with open(filename, 'w') as f:
            f.write("# Baseline Performance Results\\n\\n")
            f.write("Generated on: " + time.strftime('%Y-%m-%d %H:%M:%S') + "\\n\\n")
            
            f.write("## Token Counting Performance\\n\\n")
            f.write("| Test | Execution Time (ms) | Memory (MB) | Rows | Tokens/sec |\\n")
            f.write("|------|---------------------|-------------|------|------------|\\n")
            
            for result in self.results:
                if "counting" in result.test_name:
                    tokens_per_sec = int(result.tokens_processed / (result.execution_time_ms / 1000)) if result.execution_time_ms > 0 else 0
                    f.write(f"| {result.test_name} | {result.execution_time_ms:.1f} | {result.memory_usage_mb:.1f} | {result.rows_processed} | {tokens_per_sec:,} |\\n")
            
            f.write("\\n## Batch Splitting Performance\\n\\n")
            f.write("| Test | Execution Time (ms) | Memory (MB) | Rows | Rows/sec |\\n")
            f.write("|------|---------------------|-------------|------|----------|\\n")
            
            for result in self.results:
                if "splitting" in result.test_name:
                    rows_per_sec = int(result.rows_processed / (result.execution_time_ms / 1000)) if result.execution_time_ms > 0 else 0
                    f.write(f"| {result.test_name} | {result.execution_time_ms:.1f} | {result.memory_usage_mb:.1f} | {result.rows_processed} | {rows_per_sec:,} |\\n")


if __name__ == "__main__":
    print("🚀 Starting Prompt Learning SDK Performance Benchmark")
    
    benchmark = PerformanceBenchmark()
    results = benchmark.run_comprehensive_benchmark()
    
    print("\\n📊 Benchmark Complete!")
    benchmark.save_results()
    print("📁 Results saved to tests/benchmarks/baseline_results.md")