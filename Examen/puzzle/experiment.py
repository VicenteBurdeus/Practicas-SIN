#!/usr/bin/env python3
"""
8-Puzzle Performance Evaluator

This script evaluates the performance of different algorithms on a set of 8-puzzle instances.
It measures both spatial (memory) and temporal (time) requirements.

Usage:
    python experiment.py <input_file> <algorithm> [--save] [--verbose][--help]

Arguments:
    input_file: Path to a text file containing puzzle instances (one per line)
    algorithm: Name of the algorithm to use for solving
    --save: Optional flag to export results to CSV files
    --verbose: Optional flag to show detailed progress for each puzzle

Supported algorithms:
    - bfs: Breadth-First Search
    - dfs_graph: Depth-First Graph Search
    - dfs_backtracking: Depth-First Search with Backtracking
    - greedy_manhattan: Greedy search with Manhattan distance
    - iterative_deepening: Iterative Deepening search
    - a_star_manhattan: A* search with Manhattan distance
    - a_star_euclidean: A* search with Euclidean distance
    - ida_star_manhattan: IDA* search with Manhattan distance

Metrics collected:
    - Nodes Generated: Total number of nodes created during search
    - Nodes Expanded: Number of nodes whose children were generated
    - Max Nodes Stored: Peak number of nodes stored in memory
    - Solution Cost: Number of moves in the solution path    
    - Max Depth: Maximum depth reached during search
    - Execution Time: Wall-clock time to solve the puzzle
    
Examples:
    python experiment.py 10_puzzles.txt bfs
    python experiment.py 10_puzzles.txt a_star_manhattan --save
    python experiment.py 10_puzzles.txt greedy_manhattan --verbose
    python experiment.py 10_puzzles.txt ida_star_manhattan --save --verbose
"""

import sys
import os
import csv
import statistics
import time
import argparse
import textwrap
from typing import List, Dict, Optional

# Add the current directory to Python path to import main.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import main

class PerformanceEvaluator:
    """Evaluates algorithm performance on 8-puzzle instances."""
    
    # ============================================================================
    # STUDENT MODIFICATION ZONE: ALGORITHM CONFIGURATION
    # ============================================================================
    # Example:
    # 'your_algorithm_name': ('graphSearch', {'function_g': main.function_1, 'function_h': main.getYourHeuristic}),
    # ============================================================================
    ALGORITHMS = {
        'bfs': ('graphSearch', {'function_g': main.function_1, 'function_h': main.function_0}),
        'dfs_graph': ('graphSearch', {'function_g': main.function_N, 'function_h': main.function_0, 'maximum_depth': 20}),
        'dfs_backtracking': ('DFS_B', {'maximum_depth': 20}),
        'iterative_deepening': ('ID_B', {}),
        'greedy_manhattan': ('graphSearch', {'function_g': main.function_0, 'function_h': main.getManhattanDistance}),
        'a_star_manhattan': ('graphSearch', {'function_g': main.function_1, 'function_h': main.getManhattanDistance}),
        'ida_star_manhattan': ('IDA_B', {'function_h': main.getManhattanDistance}),
        'a_star_euclidean': ('graphSearch', {'function_g': main.function_1, 'function_h': main.getEuclideanDistance}),
        
        # ADD YOUR NEW ALGORITHMS BELOW THIS LINE:
        'Metodo_A': ('graphSearch', {'function_g': main.function_1, 'function_h': main.myMethod1}),
        'Metodo_B': ('graphSearch', {'function_g': main.function_1, 'function_h': main.myMethod2}),
        # ADD YOUR NEW ALGORITHMS ABOVE THIS LINE
    }
    # ============================================================================
    # END OF STUDENT MODIFICATION ZONE
    # ============================================================================
    
    def load_puzzles(self, file_path: str) -> List[str]:
        """Load puzzle instances from a text file and validate format."""
        try:
            with open(file_path, 'r') as f:
                puzzles = [line.strip() for line in f if line.strip()]
            
            # Validate each puzzle format
            valid_puzzles = []
            for line_number, puzzle in enumerate(puzzles, 1):
                if self.validate_puzzle(puzzle):
                    valid_puzzles.append(puzzle)
                else:
                    print(f"Warning: Invalid puzzle format at line {line_number}: {puzzle}")
            
            return valid_puzzles
            
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file '{file_path}': {e}")
            sys.exit(1)
    
    def validate_puzzle(self, puzzle: str) -> bool:
        """
        Validate that a puzzle string is properly formatted.
        
        A valid puzzle must:
        - Be exactly 9 characters long
        - Contain exactly the digits 0-8 (no repeats, no missing digits)
        """
        if len(puzzle) != 9:
            return False
        
        # Check if it contains exactly the digits 0-8
        digits = set(puzzle)
        expected_digits = set('012345678')
        
        return digits == expected_digits
    
    def _reset_performance_counters(self):
        """Reset all performance tracking variables in main.py."""
        main.graphf_counter = 0
        main.node_counter = 0
        main.explored_counter = 0
        main.heap_counter = 0
        main.open_counter = 0
        main.max_counter = 0
        main.max_rev_counter = 0
        main.graphf_path = []
        main.graphf_cost = 0
        main.graphf_depth = 0
        main.time_graphf = 0.0
    
    def _create_result_dict(self, solved: bool, include_solution_metrics: bool = True) -> Dict:
        """Create a standardized result dictionary."""
        result = {
            'solved': solved,
            'nodes_generated': main.node_counter,
            'nodes_expanded': main.graphf_counter,
            'execution_time': main.time_graphf,
        }
        
        if include_solution_metrics and solved:
            result.update({
                'solution_cost': main.graphf_cost,
                'max_depth': main.graphf_depth,
                'max_memory': getattr(main, 'max_node_stored', main.max_counter),
            })
        
        return result
    
    def _create_empty_result(self, puzzle: str) -> Dict:
        """Create an empty result for unsolvable puzzles."""
        return {
            'initial_state': puzzle,
            'solved': False,
            'nodes_generated': '',
            'nodes_expanded': '',
            'execution_time': '',
            'solution_cost': '',
            'max_depth': '',
            'max_memory': ''
        }
    
    def solve_puzzle(self, puzzle: str, algorithm: str) -> Optional[Dict]:
        """
        Solve a single puzzle and collect performance metrics.
        
        Returns a dictionary with performance data, or None if puzzle is unsolvable.
        """
        if algorithm not in self.ALGORITHMS:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        # Check if puzzle is solvable (saves time on impossible puzzles)
        if not main.isSolvable(puzzle):
            return None
        
        # Get algorithm configuration
        func_name, params = self.ALGORITHMS[algorithm]
        
        # Get the algorithm function from main.py
        algorithm_function = getattr(main, func_name)
        
        # Reset all performance tracking variables in main.py before solving
        self._reset_performance_counters()
        
        try:
            # Execute the appropriate algorithm with its required parameters
            if func_name == 'graphSearch':
                result = algorithm_function(puzzle, params['function_g'], params['function_h'], params.get('maximum_depth', -1))
            elif func_name == 'DFS_B':
                result = algorithm_function(puzzle, params.get('maximum_depth', -1))
            elif func_name == 'ID_B':
                result = algorithm_function(puzzle)
            elif func_name == 'IDA_B':
                result = algorithm_function(puzzle, params['function_h'])
            else:
                result = algorithm_function(puzzle)
            
            # Return standardized result dictionary
            return self._create_result_dict(solved=(result == 1), include_solution_metrics=True)
        
        except Exception as e:
            print(f"Error solving puzzle {puzzle}: {e}")
            return self._create_result_dict(solved=False, include_solution_metrics=False)
    
    def evaluate_algorithm(self, puzzles: List[str], algorithm: str, verbose: bool = False) -> Dict:
        """
        Evaluate algorithm performance on a set of puzzles.
        
        Returns a dictionary containing performance statistics and individual results.
        """
        # Display progress message
        if verbose:
            print(f"Evaluating {algorithm} on {len(puzzles)} puzzles...")
        else:
            print(f"Solving {len(puzzles)} puzzle instances...")
        
        solved_results = []
        all_results = []  # Track all results for CSV export
        unsolved_count = 0
        
        # Process each puzzle
        for puzzle_index, puzzle in enumerate(puzzles, 1):
            if verbose:
                print(f"Solving puzzle {puzzle_index}/{len(puzzles)}: {puzzle}", end=' ')
            
            result = self.solve_puzzle(puzzle, algorithm)
            
            if result is None:
                if verbose:
                    print("(unsolvable)")
                all_results.append(self._create_empty_result(puzzle))
            elif result['solved']:
                if verbose:
                    print(f"(solved in {result['execution_time']:.4f}s)")
                result['initial_state'] = puzzle
                solved_results.append(result)
                all_results.append(result)
            else:
                if verbose:
                    print("(failed)")
                # Create standardized failed result
                failed_result = self._create_empty_result(puzzle)
                # Fill in available metrics from the failed attempt
                for key in ['nodes_generated', 'nodes_expanded', 'execution_time']:
                    if key in result:
                        failed_result[key] = result[key]
                all_results.append(failed_result)
                unsolved_count += 1
        
        # Check if any puzzles were solved
        if not solved_results:
            return {'error': 'No puzzles were solved successfully'}
        
        # Calculate performance statistics
        metrics = ['nodes_generated', 'nodes_expanded', 'max_memory', 
                  'solution_cost', 'max_depth', 'execution_time']
        
        stats = {}
        for metric in metrics:
            values = [result[metric] for result in solved_results if metric in result and result[metric] != '']
            if values:
                stats[metric] = {
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'min': min(values),
                    'max': max(values),
                    'std_dev': statistics.stdev(values) if len(values) > 1 else 0
                }
        
        return {
            'algorithm': algorithm,
            'total_puzzles': len(puzzles),
            'solved_puzzles': len(solved_results),
            'unsolved_puzzles': unsolved_count,
            'success_rate': len(solved_results) / len(puzzles) * 100,
            'statistics': stats,
            'individual_results': solved_results,
            'all_results': all_results  # Include all results for CSV export
        }
    
    def print_results(self, evaluation: Dict, verbose: bool = False):
        """Print evaluation results in a formatted manner."""
        if 'error' in evaluation:
            print(f"Error: {evaluation['error']}")
            return
        
        print(f"\n{'='*60}")
        print(f"PERFORMANCE EVALUATION RESULTS")
        print(f"{'='*60}")
        print(f"Algorithm: {evaluation['algorithm']}")
        print(f"Total puzzles: {evaluation['total_puzzles']}")
        print(f"Solved puzzles: {evaluation['solved_puzzles']}")
        print(f"Success rate: {evaluation['success_rate']:.1f}%")
        
        # Adjust header and output based on verbose mode
        if verbose:
            print(f"\n{'PERFORMANCE METRICS':<25} {'MEAN':<12} {'MEDIAN':<12} {'MIN':<12} {'MAX':<12} {'STD DEV':<12}")
            print(f"{'-'*85}")
        else:
            print(f"\n{'PERFORMANCE METRICS':<25} {'MEAN':<12}")
            print(f"{'-'*37}")
        
        metrics_display = [
            ('nodes_generated', 'Nodes Generated'),
            ('nodes_expanded', 'Nodes Expanded'),
            ('max_memory', 'Max Nodes Stored'),
            ('solution_cost', 'Solution Cost'),
            ('max_depth', 'Max Depth'),
            ('execution_time', 'Execution Time (s)')
        ]
        
        for metric, display_name in metrics_display:
            if metric in evaluation['statistics']:
                stats = evaluation['statistics'][metric]
                if verbose:
                    # Show all statistics in verbose mode
                    if metric == 'execution_time':
                        print(f"{display_name:<25} {stats['mean']:<12.4f} {stats['median']:<12.4f} "
                              f"{stats['min']:<12.4f} {stats['max']:<12.4f} {stats['std_dev']:<12.4f}")
                    else:
                        print(f"{display_name:<25} {stats['mean']:<12.2f} {stats['median']:<12.0f} "
                              f"{stats['min']:<12.0f} {stats['max']:<12.0f} {stats['std_dev']:<12.2f}")
                else:
                    # Show only mean in non-verbose mode
                    if metric == 'execution_time':
                        print(f"{display_name:<25} {stats['mean']:<12.4f}")
                    else:
                        print(f"{display_name:<25} {stats['mean']:<12.2f}")

    def save_results_csv(self, evaluation: Dict, filename: str):
        """Save evaluation results to a CSV file."""
        if 'error' in evaluation:
            print(f"Cannot save results: {evaluation['error']}")
            return
        
        # Save summary statistics
        self._save_summary_csv(evaluation, f"summary_{filename}")
        
        # Save individual results
        self._save_details_csv(evaluation, f"details_{filename}")
        
        print(f"Results saved to summary_{filename} and details_{filename}")
    
    def _save_summary_csv(self, evaluation: Dict, filename: str):
        """Save summary statistics to CSV."""
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Algorithm', 'Total_Puzzles', 'Solved_Puzzles', 'Success_Rate', 'Metric',
                           'Mean', 'Median', 'Min', 'Max', 'Std_Dev'])
            
            algorithm = evaluation['algorithm']
            total = evaluation['total_puzzles']
            solved = evaluation['solved_puzzles']
            success_rate = evaluation['success_rate']
            
            for metric, stats in evaluation['statistics'].items():
                writer.writerow([
                    algorithm, total, solved, f"{success_rate:.1f}%", metric,
                    f"{stats['mean']:.4f}", f"{stats['median']:.4f}", 
                    f"{stats['min']:.4f}", f"{stats['max']:.4f}", f"{stats['std_dev']:.4f}"
                ])
    
    def _save_details_csv(self, evaluation: Dict, filename: str):
        """Save individual puzzle results to CSV."""
        all_results = evaluation.get('all_results')
        if not all_results:
            return
            
        with open(filename, 'w', newline='') as f:
            # Define fieldnames in the desired order
            base_fields = list(all_results[0].keys())
            if 'initial_state' in base_fields:
                base_fields.remove('initial_state')
            fieldnames = ['puzzle_index', 'initial_state'] + base_fields
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, result in enumerate(all_results, 1):
                row = {'puzzle_index': i}
                row.update(result)
                writer.writerow(row)


def run_evaluation():
    """Main function to handle command line arguments and run evaluation."""
    parser = argparse.ArgumentParser(
        description='Evaluate performance of 8-puzzle algorithms',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''
        Examples:
          python experiment.py instances.txt bfs --verbose
          python experiment.py instances.txt a_star_manhattan
          python experiment.py instances.txt greedy_manhattan --verbose --save
        ''')
    )
    
    parser.add_argument('input_file', help='Text file containing puzzle instances')
    parser.add_argument('algorithm', choices=list(PerformanceEvaluator.ALGORITHMS.keys()),
                      help='Algorithm to evaluate (includes heuristic when applicable)')
    parser.add_argument('--verbose', action='store_true',
                      help='Enable verbose output with detailed results')
    parser.add_argument('--save', action='store_true', help='Save results to CSV file')
    
    args = parser.parse_args()
    
    # Load and validate puzzles
    evaluator = PerformanceEvaluator()
    puzzles = evaluator.load_puzzles(args.input_file)
    if not puzzles:
        print("Error: No valid puzzles found in the file.")
        sys.exit(1)
    
    print(f"Loaded {len(puzzles)} valid puzzles from {args.input_file}")
    
    # Run evaluation
    evaluation = evaluator.evaluate_algorithm(puzzles, args.algorithm, args.verbose)
    evaluator.print_results(evaluation, args.verbose)
    
    # Save results if requested
    if args.save:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        evaluator.save_results_csv(evaluation, f"{args.algorithm}_{timestamp}.csv")

if __name__ == '__main__':
    run_evaluation()
