#!/bin/bash
#
# Script para execução automática de experimentos no Linux
#

echo "===== Verificando pré-requisitos ====="

# Função para verificar e instalar pacotes
check_and_install() {
    if ! command -v $1 &> /dev/null; then
        echo "$1 não encontrado. Instalando..."
        sudo apt-get update && sudo apt-get install -y $2
        if [ $? -ne 0 ]; then
            echo "Falha ao instalar $2. Por favor, instale manualmente."
            exit 1
        fi
    fi
}

# Verificar compilador e ferramentas de build
check_and_install g++ g++
check_and_install cmake cmake
check_and_install make make

# Verificar Python e pacotes
check_and_install python3 python3
check_and_install pip3 python3-pip

# Instalar pacotes Python necessários
echo "Instalando pacotes Python necessários..."
pip3 install numpy matplotlib scipy pandas seaborn streamlit

# Definir diretórios do projeto
PROJETO_RAIZ=$(pwd)
DIRETORIO_BUILD="${PROJETO_RAIZ}/build"
DIRETORIO_BINARIOS="${PROJETO_RAIZ}/build/bin"  # Changed from /bin to /build/bin
DIRETORIO_INSTANCIAS="${PROJETO_RAIZ}/output/instances"
DIRETORIO_RESULTADOS="${PROJETO_RAIZ}/output/results"
DIRETORIO_GRAFICOS="${PROJETO_RAIZ}/output/graphs"

# Criar diretórios se não existirem
mkdir -p "${DIRETORIO_BUILD}"
mkdir -p "${DIRETORIO_BINARIOS}"
mkdir -p "${DIRETORIO_INSTANCIAS}"
mkdir -p "${DIRETORIO_RESULTADOS}"
mkdir -p "${DIRETORIO_GRAFICOS}"

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
# Change directory to where the executables actually are
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

# Gerar instâncias de teste
echo "===== Gerando instâncias de teste ====="
"${DIRETORIO_BINARIOS}/generate_instances" 5 10 10

# Testar instâncias
echo "===== Testando as instâncias ====="
python3 "${PROJETO_RAIZ}/python/test_instances.py"

echo "===== Executando os experimentos ====="
echo "Este processo pode levar algum tempo..."
python3 "${PROJETO_RAIZ}/python/experiments.py"

echo "===== Gerando visualizações adicionais ====="
cd "${PROJETO_RAIZ}/scripts"
python3 generate_visualizations.py

echo "===== Processo completo! ====="
echo "Os resultados dos experimentos estão disponíveis em:"
echo "- Arquivos CSV: ${DIRETORIO_RESULTADOS}"
echo "- Gráficos: ${DIRETORIO_GRAFICOS}"
echo ""