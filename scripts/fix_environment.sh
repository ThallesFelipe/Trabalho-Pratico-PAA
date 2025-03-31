#!/bin/bash
# filepath: c:\Users\thall\Documents\GitHub\Trabalho-Pratico-PAA\fix_environment.sh

echo "===== Fixing Experimental Environment ====="

# 1. Define correct paths
PROJETO_RAIZ=$(pwd)
DIRETORIO_BUILD="${PROJETO_RAIZ}/build"
DIRETORIO_BINARIOS="${DIRETORIO_BUILD}/bin"
DIRETORIO_OUTPUT="${PROJETO_RAIZ}/output"
DIRETORIO_INSTANCIAS="${DIRETORIO_OUTPUT}/instances"
DIRETORIO_RESULTADOS="${DIRETORIO_OUTPUT}/results"
DIRETORIO_GRAFICOS="${DIRETORIO_OUTPUT}/graphs"

# 2. Create necessary directories with error checking
echo "Creating required directories..."
for DIR in "${DIRETORIO_OUTPUT}" "${DIRETORIO_INSTANCIAS}" "${DIRETORIO_RESULTADOS}" "${DIRETORIO_GRAFICOS}"; do
    mkdir -p "$DIR"
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create directory: $DIR"
        exit 1
    fi
done

# 3. Rebuild the project with error checking
echo "Rebuilding the project..."
if [ -d "${DIRETORIO_BUILD}" ]; then
    rm -rf "${DIRETORIO_BUILD}"
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to remove existing build directory"
        exit 1
    fi
fi

mkdir -p "${DIRETORIO_BUILD}"
cd "${DIRETORIO_BUILD}" || { echo "ERROR: Failed to change to build directory"; exit 1; }
cmake .. || { echo "ERROR: CMake configuration failed"; exit 1; }
make -j4 || { echo "ERROR: Build failed"; exit 1; }

# 4. Verify executables exist
echo "Verifying executables..."
if [ -f "${DIRETORIO_BINARIOS}/run_dynamic_programming" ] && \
   [ -f "${DIRETORIO_BINARIOS}/run_backtracking" ] && \
   [ -f "${DIRETORIO_BINARIOS}/run_branch_and_bound" ] && \
   [ -f "${DIRETORIO_BINARIOS}/generate_instances" ]; then
    echo "All executables found successfully!"
    chmod +x "${DIRETORIO_BINARIOS}/run_dynamic_programming"
    chmod +x "${DIRETORIO_BINARIOS}/run_backtracking"
    chmod +x "${DIRETORIO_BINARIOS}/run_branch_and_bound"
    chmod +x "${DIRETORIO_BINARIOS}/generate_instances"
else
    echo "ERROR: Some executables are missing!"
    ls -la "${DIRETORIO_BINARIOS}"
    exit 1
fi

# 5. Generate a test instance to verify everything works
echo "Generating test instance..."
"${DIRETORIO_BINARIOS}/generate_instances" 1 10 10

# 6. Run a simple test on all algorithms
echo "Testing algorithms on the generated instance..."
for algorithm in run_dynamic_programming run_backtracking run_branch_and_bound; do
    test_file=$(find "${DIRETORIO_INSTANCIAS}" -name "*.txt" | head -n 1)
    if [ -n "$test_file" ]; then
        echo "Testing $algorithm on $test_file"
        "${DIRETORIO_BINARIOS}/$algorithm" "$test_file"
    else
        echo "No test file found!"
        exit 1
    fi
done

# 7. Generate initial experiment data files
echo "Generating initial experiment data files..."
cd "${PROJETO_RAIZ}"

# Create basic CSV headers to prevent empty file errors
echo "n,W,algoritmo,instancia,tempo,valor" > "${DIRETORIO_RESULTADOS}/resultados_variando_n.csv"
echo "W,n,algoritmo,instancia,tempo,valor" > "${DIRETORIO_RESULTADOS}/resultados_variando_W.csv"

# Run small initial experiment to populate files
echo "Running small initial experiment..."
# Generate a few instances for initial experimentation
"${DIRETORIO_BINARIOS}/generate_instances" 3 10 20
for i in {1..3}; do
    instance_file="${DIRETORIO_INSTANCIAS}/instancias_n10_W20/instancia_${i}.txt"
    if [ -f "$instance_file" ]; then
        for algorithm in run_dynamic_programming run_backtracking run_branch_and_bound; do
            echo "Testing ${algorithm} on instance ${i}..."
            start_time=$(date +%s.%N)
            result=$("${DIRETORIO_BINARIOS}/${algorithm}" "$instance_file")
            end_time=$(date +%s.%N)
            execution_time=$(echo "$end_time - $start_time" | bc)
            value=$(echo "$result" | grep -o "Valor máximo: [0-9]*" | awk '{print $3}')
            
            # Append to n-varying results
            echo "10,20,${algorithm},${i},${execution_time},${value}" >> "${DIRETORIO_RESULTADOS}/resultados_variando_n.csv"
            
            # Append to W-varying results
            echo "20,10,${algorithm},${i},${execution_time},${value}" >> "${DIRETORIO_RESULTADOS}/resultados_variando_W.csv"
        done
    fi
done

echo "===== Environment check complete ====="
echo "Initial data files created. You can now run the full experiments with ./scripts/run_experiments_linux.sh"