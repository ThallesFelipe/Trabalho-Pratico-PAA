#!/bin/bash
#
# Script para execução automática de experimentos em sistemas Linux
# 
# Este script realiza as seguintes operações:
# 1. Verifica e instala dependências necessárias
# 2. Compila os programas C++ do projeto usando CMake
# 3. Configura permissões dos executáveis
# 4. Executa os experimentos via Python
#
# Data: Março 2025

echo "===== Verificando pré-requisitos ====="
# Verificar compilador g++
if ! command -v g++ &> /dev/null; then
    echo "g++ não encontrado. Instalando..."
    sudo apt-get update
    sudo apt-get install -y g++
fi

# Verificar CMake
if ! command -v cmake &> /dev/null; then
    echo "CMake não encontrado. Instalando..."
    sudo apt-get update
    sudo apt-get install -y cmake
fi

# Verificar Python e pacotes necessários
if ! command -v python3 &> /dev/null; then
    echo "Python3 não encontrado. Instalando..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip
fi

# Instalar pacotes Python necessários
echo "Instalando pacotes Python necessários..."
pip3 install numpy matplotlib scipy pandas

# Definir diretórios
PROJETO_RAIZ=$(pwd)
DIRETORIO_BUILD="${PROJETO_RAIZ}/build"
DIRETORIO_BINARIOS="${DIRETORIO_BUILD}/bin"
DIRETORIO_INSTANCIAS="${PROJETO_RAIZ}/output/instances"
DIRETORIO_RESULTADOS="${PROJETO_RAIZ}/output/results"

# Criar diretórios necessários
mkdir -p "${DIRETORIO_BUILD}"
mkdir -p "${DIRETORIO_INSTANCIAS}"
mkdir -p "${DIRETORIO_RESULTADOS}"

echo "===== Compilando o projeto usando CMake ====="
# Mudar para o diretório de build e compilar
cd "${DIRETORIO_BUILD}"
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)

# Verificar se a compilação foi bem-sucedida
if [ $? -ne 0 ]; then
    echo "Erro na compilação dos programas. Abortando."
    exit 1
fi

echo "===== Tornando os executáveis acessíveis ====="
# Ajustar nomes dos executáveis de acordo com a atualização do projeto
cd "${DIRETORIO_BINARIOS}"
chmod +x run_dynamic_programming
chmod +x run_backtracking
chmod +x run_branch_and_bound
chmod +x generate_instances

# Exportar variáveis de ambiente para que os programas possam encontrar os diretórios
export INSTANCES_DIR="${DIRETORIO_INSTANCIAS}"
export RESULTS_DIR="${DIRETORIO_RESULTADOS}"

# Voltar para o diretório raiz
cd "${PROJETO_RAIZ}"

# Descomentar para gerar instâncias de teste
# echo "===== Gerando instâncias de teste ====="
# "${DIRETORIO_BINARIOS}/generate_instances" 5 10 10

# Descomentar para testar as instâncias
# echo "===== Testando as instâncias ====="
# python3 "${PROJETO_RAIZ}/python/test_instances.py"

echo "===== Executando os experimentos ====="
echo "Este processo pode levar algum tempo..."
python3 "${PROJETO_RAIZ}/python/experiments.py"

echo "===== Processo completo! ====="
echo "Os resultados dos experimentos estão nos arquivos CSV e gráficos gerados em ${DIRETORIO_RESULTADOS}."