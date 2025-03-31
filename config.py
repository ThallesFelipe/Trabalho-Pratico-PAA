# Configuration file for Python experiments
# This template is processed by CMake to generate the actual config.py
import os
import sys
import platform
from pathlib import Path

# Função para ajustar caminhos entre Windows e WSL
def ajustar_caminho(caminho):
    """Ajusta o caminho para o formato correto do sistema operacional atual."""
    sistema = platform.system()
    
    # Se estiver no Windows, mas o caminho está no formato WSL
    if sistema == 'Windows' and caminho.startswith('/mnt/'):
        drive = caminho[5]
        resto = caminho[7:].replace('/', '\\')
        return f"{drive}:{resto}"
    
    # Se estiver no Linux/WSL, mas o caminho está no formato Windows
    elif sistema == 'Linux' and ':' in caminho:
        partes = caminho.split(':')
        drive = partes[0].lower()
        resto = partes[1].replace('\\', '/')
        return f"/mnt/{drive}{resto}"
    
    # Retorna o caminho sem alterações se não precisar de ajustes
    return caminho

# Diretório base do projeto
BASE_DIR = str(Path(__file__).parent.absolute())

# Directory locations
BINARY_DIR = ajustar_caminho("c:/Users/thall/Documents/GitHub/Trabalho-Pratico-PAA/build/bin")
OUTPUT_DIR = ajustar_caminho("c:/Users/thall/Documents/GitHub/Trabalho-Pratico-PAA/output")
INSTANCES_DIR = ajustar_caminho("c:/Users/thall/Documents/GitHub/Trabalho-Pratico-PAA/output/instances")
RESULTS_DIR = ajustar_caminho("c:/Users/thall/Documents/GitHub/Trabalho-Pratico-PAA/output/results")
GRAPHS_DIR = ajustar_caminho("c:/Users/thall/Documents/GitHub/Trabalho-Pratico-PAA/output/graphs")

# Criar diretórios se não existirem
for dir_path in [OUTPUT_DIR, INSTANCES_DIR, RESULTS_DIR, GRAPHS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Executables
BACKTRACKING_EXE = "run_backtracking"
BRANCH_AND_BOUND_EXE = "run_branch_and_bound"
DYNAMIC_PROGRAMMING_EXE = "run_dynamic_programming"
INSTANCE_GENERATOR_EXE = "generate_instances"

# Ajustar nome dos executáveis para Windows se necessário
if platform.system() == 'Windows':
    BACKTRACKING_EXE += ".exe"
    BRANCH_AND_BOUND_EXE += ".exe"
    DYNAMIC_PROGRAMMING_EXE += ".exe"
    INSTANCE_GENERATOR_EXE += ".exe"

print(f"Configuração carregada com sucesso.")
print(f"Diretório binário: {BINARY_DIR}")
print(f"Diretório de resultados: {RESULTS_DIR}")