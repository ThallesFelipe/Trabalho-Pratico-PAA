#!/usr/bin/env python3
"""
Script completo para execução dos experimentos e análises do Trabalho Prático de PAA.
Este script coordena:
1. Geração de instâncias de teste
2. Execução dos algoritmos em todas as instâncias
3. Análise de resultados e geração de estatísticas
4. Criação de visualizações
"""

import os
import sys
import time
from pathlib import Path

# Adicionar diretórios ao path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "python"))

# Importar os módulos necessários
from python.experiments import ExecutorExperimentos
import scripts.generate_visualizations as visualizations

def main():
    print("="*80)
    print("ANÁLISE EXPERIMENTAL DE ALGORITMOS PARA O PROBLEMA DA MOCHILA")
    print("="*80)
    
    # Inicializar executor
    executor = ExecutorExperimentos()
    
    # Inicializar arquivos CSV
    executor.inicializar_arquivos_csv()
    
    # Configurações
    config = {
        'valores_n': [10, 20, 30, 40, 50],          # Valores de n
        'valores_W': [50, 100, 150, 200, 250],      # Valores de W
        'num_instancias': 5,                        # Instâncias por configuração
        'timeout_algoritmo': 180,                   # Timeout por algoritmo
        'W_fixo': 100,                              # W fixo para testes com n variável
        'n_fixo': 30                                # n fixo para testes com W variável
    }
    
    print("\nCONFIGURAÇÕES DO EXPERIMENTO:")
    print(f"- Valores de n: {config['valores_n']}")
    print(f"- Valores de W: {config['valores_W']}")
    print(f"- Instâncias por configuração: {config['num_instancias']}")
    print(f"- Timeout: {config['timeout_algoritmo']} segundos")
    
    # Fase 1: Experimentos variando n
    print("\n" + "-"*80)
    print("FASE 1: EXPERIMENTOS VARIANDO N")
    print("-"*80)
    df_n = executor.executar_variando_n(
        valores_n=config['valores_n'], 
        W=config['W_fixo'], 
        num_instancias=config['num_instancias']
    )
    
    # Fase 2: Experimentos variando W
    print("\n" + "-"*80)
    print("FASE 2: EXPERIMENTOS VARIANDO W")
    print("-"*80)
    df_W = executor.executar_variando_W(
        valores_W=config['valores_W'], 
        n=config['n_fixo'], 
        num_instancias=config['num_instancias']
    )
    
    # Fase 3: Análise estatística
    print("\n" + "-"*80)
    print("FASE 3: ANÁLISE ESTATÍSTICA")
    print("-"*80)
    if df_n is not None and not df_n.empty:
        executor.analisar_resultados(df_n, parametro_variavel='n')
        executor.realizar_teste_t_pareado(df_n)
        executor.realizar_analise_estatistica(df_n)
    
    if df_W is not None and not df_W.empty:
        executor.analisar_resultados(df_W, parametro_variavel='W')
        executor.realizar_teste_t_pareado(df_W)
        executor.realizar_analise_estatistica_completa(df_W)
    
    # Fase 4: Geração de visualizações
    print("\n" + "-"*80)
    print("FASE 4: GERAÇÃO DE VISUALIZAÇÕES")
    print("-"*80)
    visualizations.main()
    
    print("\n" + "="*80)
    print("EXPERIMENTO CONCLUÍDO")
    print("="*80)
    print(f"\nResultados salvos em: {executor.diretorio_resultados}")
    print(f"Visualizações salvas em: {executor.diretorio_graficos}")

if __name__ == "__main__":
    start_time = time.time()
    try:
        main()
        elapsed = time.time() - start_time
        print(f"\nTempo total de execução: {elapsed/60:.2f} minutos")
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.")
    except Exception as e:
        import traceback
        print(f"\nErro durante a execução: {e}")
        traceback.print_exc()