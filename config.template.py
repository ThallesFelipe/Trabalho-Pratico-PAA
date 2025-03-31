# Configuration file for Python experiments
# This template is processed by CMake to generate the actual config.py

# Directory locations (these placeholders will be replaced by CMake during configuration)
BINARY_DIR = "@CMAKE_RUNTIME_OUTPUT_DIRECTORY@"  # Location of compiled executables
OUTPUT_DIR = "@DIRETORIO_SAIDA@"                      # Main output directory
INSTANCES_DIR = "@DIRETORIO_INSTANCIAS@"                # Directory for knapsack problem instances
RESULTS_DIR = "@DIRETORIO_RESULTADOS@"                    # Directory for experiment results
GRAPHS_DIR = "@DIRETORIO_GRAFICOS@"                      # Directory for generated graphs/plots

# Executables (relative to BINARY_DIR)
BACKTRACKING_EXE = "run_backtracking"        # Backtracking algorithm executable
BRANCH_AND_BOUND_EXE = "run_branch_and_bound" # Branch and bound algorithm executable
DYNAMIC_PROGRAMMING_EXE = "run_dynamic_programming" # Dynamic programming algorithm executable
INSTANCE_GENERATOR_EXE = "generate_instances"    # Instance generator executable