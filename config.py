# Configuration file for Python experiments
# This template is processed by CMake to generate the actual config.py

# Directory locations (these placeholders will be replaced by CMake during configuration)
BINARY_DIR = "c:/Users/thall/Documents/GitHub/Trabalho-Pratico-PAA/build/bin"  # Location of compiled executables
OUTPUT_DIR = "c:/Users/thall/Documents/GitHub/Trabalho-Pratico-PAA/output"                      # Main output directory
INSTANCES_DIR = "c:/Users/thall/Documents/GitHub/Trabalho-Pratico-PAA/output/instances"                # Directory for knapsack problem instances
RESULTS_DIR = "c:/Users/thall/Documents/GitHub/Trabalho-Pratico-PAA/output/results"                    # Directory for experiment results
GRAPHS_DIR = "c:/Users/thall/Documents/GitHub/Trabalho-Pratico-PAA/output/graphs"                      # Directory for generated graphs/plots

# Executables (relative to BINARY_DIR)
BACKTRACKING_EXE = "run_backtracking"        # Backtracking algorithm executable
BRANCH_AND_BOUND_EXE = "run_branch_and_bound" # Branch and bound algorithm executable
DYNAMIC_PROGRAMMING_EXE = "run_dynamic_programming" # Dynamic programming algorithm executable
INSTANCE_GENERATOR_EXE = "generate_instances"    # Instance generator executable