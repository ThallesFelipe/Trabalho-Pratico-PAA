# Configuration file for Python experiments
# This template is processed by CMake to generate the actual config.py

# Directory locations (these placeholders will be replaced by CMake during configuration)
BINARY_DIR = "@CMAKE_RUNTIME_OUTPUT_DIRECTORY@"  # Location of compiled executables
OUTPUT_DIR = "@OUTPUT_DIR@"                      # Main output directory
INSTANCES_DIR = "@INSTANCES_DIR@"                # Directory for knapsack problem instances
RESULTS_DIR = "@RESULTS_DIR@"                    # Directory for experiment results
GRAPHS_DIR = "@GRAPHS_DIR@"                      # Directory for generated graphs/plots

# Executables (relative to BINARY_DIR)
BACKTRACKING_EXE = "mochila_backtracking"        # Backtracking algorithm executable
BRANCH_AND_BOUND_EXE = "mochila_branch_and_bound" # Branch and bound algorithm executable
DYNAMIC_PROGRAMMING_EXE = "mochila_programacao_dinamica" # Dynamic programming algorithm executable
INSTANCE_GENERATOR_EXE = "gerador_instancias"    # Instance generator executable