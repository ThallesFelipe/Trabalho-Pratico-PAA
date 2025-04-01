#!/bin/bash
#
# Script aprimorado para execução automática de experimentos no Linux
# Inclui limpeza de dados anteriores, controle de timeout, e possibilidade
# de executar partes específicas do processo
#
# Uso: ./scripts/run_experiments_linux.sh [opções]
# Opções:
#   --clean         Limpa dados anteriores antes de executar
#   --timeout N     Define timeout para algoritmos (segundos, padrão: 180)
#   --small         Executa experimentos com configurações menores (mais rápido)
#   --only-compile  Apenas compila o projeto sem executar experimentos
#   --only-analyze  Apenas analisa resultados existentes sem executar novos experimentos
#   --help          Mostra esta ajuda

# Configurações padrão
CLEAN_PREVIOUS=false
TIMEOUT=180
RUN_SMALL=false
ONLY_COMPILE=false
ONLY_ANALYZE=false

# Processar argumentos da linha de comando
for arg in "$@"; do
  case $arg in
    --clean)
      CLEAN_PREVIOUS=true
      shift
      ;;
    --timeout=*)
      TIMEOUT="${arg#*=}"
      shift
      ;;
    --timeout)
      TIMEOUT=$2
      shift 2
      ;;
    --small)
      RUN_SMALL=true
      shift
      ;;
    --only-compile)
      ONLY_COMPILE=true
      shift
      ;;
    --only-analyze)
      ONLY_ANALYZE=true
      shift
      ;;
    --help)
      echo "Uso: $0 [opções]"
      echo "Opções:"
      echo "  --clean         Limpa dados anteriores antes de executar"
      echo "  --timeout N     Define timeout para algoritmos (segundos, padrão: 180)"
      echo "  --small         Executa experimentos com configurações menores (mais rápido)"
      echo "  --only-compile  Apenas compila o projeto sem executar experimentos"
      echo "  --only-analyze  Apenas analisa resultados existentes sem executar novos experimentos"
      echo "  --help          Mostra esta ajuda"
      exit 0
      ;;
  esac
done

echo "===== Configurações ====="
echo "Limpar dados anteriores: $CLEAN_PREVIOUS"
echo "Timeout para algoritmos: $TIMEOUT segundos"
echo "Execução reduzida: $RUN_SMALL"
echo "Apenas compilar: $ONLY_COMPILE"
echo "Apenas analisar: $ONLY_ANALYZE"
echo "========================="

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
check_and_install bc bc  # Para cálculos no shell

# Verificar Python e pacotes
check_and_install python3 python3
check_and_install pip3 python3-pip

# Instalar pacotes Python necessários
echo "Instalando pacotes Python necessários..."
pip3 install numpy matplotlib scipy pandas seaborn tabulate openpyxl streamlit

# Definir diretórios do projeto
PROJETO_RAIZ=$(pwd)
DIRETORIO_BUILD="${PROJETO_RAIZ}/build"
DIRETORIO_BINARIOS="${PROJETO_RAIZ}/build/bin"
DIRETORIO_INSTANCIAS="${PROJETO_RAIZ}/output/instances"
DIRETORIO_RESULTADOS="${PROJETO_RAIZ}/output/results"
DIRETORIO_GRAFICOS="${PROJETO_RAIZ}/output/graphs"
DIRETORIO_RELATORIOS="${DIRETORIO_RESULTADOS}/relatorios"

# Limpar dados anteriores se solicitado
if [ "$CLEAN_PREVIOUS" = true ]; then
    echo "===== Limpando dados anteriores ====="
    if [ -d "${DIRETORIO_INSTANCIAS}" ]; then
        echo "Removendo instâncias anteriores..."
        rm -rf "${DIRETORIO_INSTANCIAS}"/*
    fi
    if [ -d "${DIRETORIO_RESULTADOS}" ]; then
        echo "Removendo resultados anteriores..."
        rm -rf "${DIRETORIO_RESULTADOS}"/*
    fi
    if [ -d "${DIRETORIO_GRAFICOS}" ]; then
        echo "Removendo gráficos anteriores..."
        rm -rf "${DIRETORIO_GRAFICOS}"/*
    fi
fi

# Criar diretórios se não existirem
mkdir -p "${DIRETORIO_BUILD}"
mkdir -p "${DIRETORIO_BINARIOS}"
mkdir -p "${DIRETORIO_INSTANCIAS}"
mkdir -p "${DIRETORIO_RESULTADOS}"
mkdir -p "${DIRETORIO_GRAFICOS}"
mkdir -p "${DIRETORIO_RELATORIOS}"

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
export GRAPHS_DIR="${DIRETORIO_GRAFICOS}"
export TIMEOUT_ALGORITMO="${TIMEOUT}"

# Sair se solicitado apenas compilação
if [ "$ONLY_COMPILE" = true ]; then
    echo "===== Compilação concluída! ====="
    echo "Para executar os experimentos, rode novamente sem a opção --only-compile"
    exit 0
fi

# Voltar para o diretório raiz
cd "${PROJETO_RAIZ}"

# Pular para análise se solicitado
if [ "$ONLY_ANALYZE" = true ]; then
    echo "===== Pulando geração de instâncias e execução de algoritmos ====="
else
    # Gerar instâncias de teste
    echo "===== Gerando instâncias de teste ====="
    if [ "$RUN_SMALL" = true ]; then
        # Conjunto reduzido de instâncias
        "${DIRETORIO_BINARIOS}/generate_instances" 3 10 20
        "${DIRETORIO_BINARIOS}/generate_instances" 3 15 30
        "${DIRETORIO_BINARIOS}/generate_instances" 3 20 40
    else
        # Conjunto completo de instâncias
        "${DIRETORIO_BINARIOS}/generate_instances" 5 10 20
        "${DIRETORIO_BINARIOS}/generate_instances" 5 20 40
        "${DIRETORIO_BINARIOS}/generate_instances" 5 30 60
        "${DIRETORIO_BINARIOS}/generate_instances" 5 40 80
    fi

    # Testar instâncias
    echo "===== Testando as instâncias ====="
    python3 "${PROJETO_RAIZ}/python/test_instances.py"

    # Configurar python_config.py com os parâmetros atuais
    echo "===== Configurando parâmetros de experimento ====="
    if [ "$RUN_SMALL" = true ]; then
        # Criar um script temporário para modificar valores no experimento
        TEMP_CONFIG="${PROJETO_RAIZ}/temp_config.py"
        # Usar aspas simples para o EOF para evitar interpolação imediata
        cat > "${TEMP_CONFIG}" << 'EOF'
import os
import sys

# Definir o timeout recebido via ambiente
timeout_valor = int(os.environ.get('TIMEOUT_VALUE', '180'))

# Adicionar diretório raiz ao path
sys.path.insert(0, os.environ.get('PROJETO_RAIZ', '.'))

# Criar arquivo de configuração para os experimentos
with open(os.path.join(os.environ.get('PROJETO_RAIZ', '.'), 'experiment_config.py'), 'w') as f:
    f.write("# Configuração automática gerada pelo script\n")
    f.write("valores_n = [10, 15, 20]\n")
    f.write("valores_W = [20, 40, 60]\n")
    f.write("num_instancias = 3\n")
    f.write(f"timeout_algoritmo = {timeout_valor}\n")
    f.write("W_fixo = 50\n")
    f.write("n_fixo = 20\n")
EOF

        # Exportar variáveis para o script Python
        export TIMEOUT_VALUE="${TIMEOUT}"
        export PROJETO_RAIZ="${PROJETO_RAIZ}"

        # Executar o script
        python3 "${TEMP_CONFIG}"
    else
        # Configuração completa
        TEMP_CONFIG="${PROJETO_RAIZ}/temp_config.py"
        # Usar aspas simples para o EOF para evitar interpolação imediata
        cat > "${TEMP_CONFIG}" << 'EOF'
import os
import sys

# Definir o timeout recebido via ambiente
timeout_valor = int(os.environ.get('TIMEOUT_VALUE', '180'))

# Adicionar diretório raiz ao path
sys.path.insert(0, os.environ.get('PROJETO_RAIZ', '.'))

# Criar arquivo de configuração para os experimentos
with open(os.path.join(os.environ.get('PROJETO_RAIZ', '.'), 'experiment_config.py'), 'w') as f:
    f.write("# Configuração automática gerada pelo script\n")
    f.write("valores_n = [10, 20, 30, 40, 50]\n")
    f.write("valores_W = [20, 40, 60, 80, 100]\n")
    f.write("num_instancias = 5\n")
    f.write(f"timeout_algoritmo = {timeout_valor}\n")
    f.write("W_fixo = 50\n")
    f.write("n_fixo = 20\n")
EOF

        # Exportar variáveis para o script Python
        export TIMEOUT_VALUE="${TIMEOUT}"
        export PROJETO_RAIZ="${PROJETO_RAIZ}"

        # Executar o script
        python3 "${TEMP_CONFIG}"
    fi

    # Remover o script temporário
    rm "${TEMP_CONFIG}"

    # Executar os experimentos
    echo "===== Executando os experimentos ====="
    echo "Este processo pode levar algum tempo..."
    echo "Timeout configurado: ${TIMEOUT} segundos por algoritmo"
    
    # Registrar horário de início
    HORA_INICIO=$(date +"%H:%M:%S")
    echo "Início da execução: ${HORA_INICIO}"
    
    # Executar o experimento principal
    python3 "${PROJETO_RAIZ}/run_analysis.py"
    
    # Registrar horário de término
    HORA_FIM=$(date +"%H:%M:%S")
    echo "Término da execução: ${HORA_FIM}"
fi

# Gerar visualizações adicionais
echo "===== Gerando visualizações adicionais ====="
cd "${PROJETO_RAIZ}/scripts"
python3 generate_visualizations.py

# Gerar relatório final aprimorado
echo "===== Gerando relatório final aprimorado ====="
cd "${PROJETO_RAIZ}"
python3 "${PROJETO_RAIZ}/run_enhanced_analysis.py"

echo "===== Processo completo! ====="
echo "Os resultados dos experimentos estão disponíveis em:"
echo "- Arquivos CSV: ${DIRETORIO_RESULTADOS}"
echo "- Relatórios: ${DIRETORIO_RELATORIOS}"
echo "- Gráficos: ${DIRETORIO_GRAFICOS}"
echo "- Relatório final: ${DIRETORIO_RESULTADOS}/relatorio_final.md"
echo ""
echo "Para visualizar os resultados, abra o arquivo relatorio_final.md em um visualizador de Markdown."
echo "Para uma análise mais detalhada, examine os arquivos CSV e gráficos gerados."