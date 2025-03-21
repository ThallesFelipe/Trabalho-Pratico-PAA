"""
Módulo para teste de instâncias do Problema da Mochila com diferentes algoritmos.

Este script testa cada instância do problema da mochila em um diretório específico
usando os algoritmos implementados (Programação Dinâmica, Backtracking e Branch and Bound).

Data: Março 2025
"""

import subprocess
import glob
import os
import sys

def testar_instancias(algoritmo, diretorio):
    """
    Testa um algoritmo específico com todas as instâncias em um diretório.
    
    Args:
        algoritmo (str): Nome do executável do algoritmo a ser testado
        diretorio (str): Caminho do diretório contendo as instâncias
    """
    print(f"\nTestando {algoritmo} em todas as instâncias do diretório {diretorio}\n")
    print("-" * 60)
    
    # Obtém todas as instâncias do diretório em ordem alfabética
    caminho_instancias = os.path.join(diretorio, "instancia_*.txt")
    instancias = sorted(glob.glob(caminho_instancias))
    
    if not instancias:
        print(f"Nenhuma instância encontrada em {diretorio}")
        return
    
    # Testa cada instância com o algoritmo especificado
    for instancia in instancias:
        print(f"Testando {instancia}...")
        
        # Determina o caminho do executável com base no sistema operacional
        executavel = algoritmo
        if sys.platform == 'win32':
            executavel += '.exe'
        
        # Executa o algoritmo com a instância atual
        comando = [os.path.join('.', executavel), instancia]
        resultado = subprocess.run(comando, capture_output=True, text=True)
        
        # Exibe o resultado
        print(resultado.stdout)
        
        # Se houver erro, exibe-o
        if resultado.stderr:
            print("Erro encontrado:")
            print(resultado.stderr)
            
        print("-" * 60)

def main():
    """
    Função principal que coordena os testes de todos os algoritmos.
    """
    # Configurações do teste
    diretorio_instancias = os.environ.get("INSTANCES_DIR", "output/instances")
    diretorio_teste = os.path.join(diretorio_instancias, "instancias_n10_W10")
    
    # Lista de algoritmos a serem testados (nomes atualizados)
    algoritmos = ["run_dynamic_programming", "run_backtracking", "run_branch_and_bound"]
    
    # Testa cada algoritmo com as instâncias
    for algoritmo in algoritmos:
        testar_instancias(algoritmo, diretorio_teste)
        
    print("Todos os testes foram concluídos.")

if __name__ == "__main__":
    main()