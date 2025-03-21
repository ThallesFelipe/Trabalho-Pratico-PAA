#!/bin/bash
#
# Script para execução automática de experimentos no macOS
# 
# Este script realiza as seguintes operações:
# 1. Verifica e instala dependências necessárias
# 2. Compila os programas C++ do projeto
# 3. Configura permissões dos executáveis
# 4. Executa os experimentos via Python
#
# Data: Março 2025

echo "===== Verificando pré-requisitos ====="
# Verificar compilador g++
if ! command -v g++ &> /dev/null; then
    echo "g++ não encontrado. Instalando..."
    brew install gcc
fi

# Verificar CMake se estiver usando sistema de build CMake
if ! command -v cmake &> /dev/null; then
    echo "CMake não encontrado. Instalando..."
    brew install cmake
fi

# Verificar Python e pacotes necessários
if ! command -v python3 &> /dev/null; then
    echo "Python3 não encontrado. Instalando..."
    brew install python
fi

# Instalar pacotes Python necessários
echo "Instalando pacotes Python necessários..."
pip3 install numpy matplotlib scipy pandas

# Definir diretórios
PROJECT_ROOT=$(pwd)
SRC_DIR="${PROJECT_ROOT}/src/main"
INCLUDE_DIR="${PROJECT_ROOT}/include"
BUILD_DIR="${PROJECT_ROOT}/build"
BIN_DIR="${BUILD_DIR}/bin"

# Criar diretórios de saída se não existirem
mkdir -p "${BUILD_DIR}"
mkdir -p "${BIN_DIR}"

echo "===== Compilando os programas C++ ====="
# Opção 1: Compilação direta (mais simples)
g++ -std=c++17 -O3 -march=native -flto -I"${INCLUDE_DIR}" "${SRC_DIR}/run_dynamic_programming.cpp" "${PROJECT_ROOT}/src/algorithms/dynamic_programming.cpp" -o "${BIN_DIR}/run_dynamic_programming"
g++ -std=c++17 -O3 -march=native -flto -I"${INCLUDE_DIR}" "${SRC_DIR}/run_backtracking.cpp" "${PROJECT_ROOT}/src/algorithms/backtracking.cpp" -o "${BIN_DIR}/run_backtracking"
g++ -std=c++17 -O3 -march=native -flto -I"${INCLUDE_DIR}" "${SRC_DIR}/run_branch_and_bound.cpp" "${PROJECT_ROOT}/src/algorithms/branch_and_bound.cpp" -o "${BIN_DIR}/run_branch_and_bound"
g++ -std=c++17 -O3 -march=native -flto -I"${INCLUDE_DIR}" "${SRC_DIR}/generate_instances.cpp" "${PROJECT_ROOT}/src/utils/instance_generator.cpp" -o "${BIN_DIR}/generate_instances"

# Verificar se a compilação foi bem-sucedida
if [ $? -ne 0 ]; then
    echo "Erro na compilação dos programas. Abortando."
    exit 1
fi

echo "===== Tornando os executáveis acessíveis ====="
chmod +x "${BIN_DIR}/run_dynamic_programming"
chmod +x "${BIN_DIR}/run_backtracking"
chmod +x "${BIN_DIR}/run_branch_and_bound"
chmod +x "${BIN_DIR}/generate_instances"

# Exportar variável de ambiente para que os programas possam encontrar os diretórios
export INSTANCES_DIR="${PROJECT_ROOT}/output/instances"
export RESULTS_DIR="${PROJECT_ROOT}/output/results"

# Criar diretórios para instâncias e resultados
mkdir -p "${INSTANCES_DIR}"
mkdir -p "${RESULTS_DIR}"

# Descomentar para gerar instâncias de teste
# echo "===== Gerando instâncias de teste ====="
# "${BIN_DIR}/generate_instances" 5 10 10

# Descomentar para testar as instâncias
# echo "===== Testando as instâncias ====="
# python3 "${PROJECT_ROOT}/python/test_instances.py"

echo "===== Executando os experimentos ====="
echo "Este processo pode levar algum tempo..."
python3 "${PROJECT_ROOT}/python/experiments.py"

echo "===== Processo completo! ====="
echo "Os resultados dos experimentos estão nos arquivos CSV e gráficos gerados em ${RESULTS_DIR}."