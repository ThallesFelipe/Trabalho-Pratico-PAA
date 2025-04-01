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
    
    # Configurações
    config = {
        'valores_n': [20, 40, 60, 80],  
        'valores_W': [40, 60, 80, 100],  
        'num_instancias': 4,                                              
        'timeout_algoritmo': 300,                                          
        'W_fixo': 80,                                                     
        'n_fixo': 40                                                      
    }
    
    # Inicializar executor
    executor = ExecutorExperimentos()
    executor.timeout_algoritmo = config['timeout_algoritmo']  # Aplicar o timeout das configurações
    
    # Inicializar arquivos CSV
    executor.inicializar_arquivos_csv()
    
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
        # CORREÇÃO 2: Usar o método correto para resumo estatístico
        executor.gerar_resumo_resultados(df_n)  # Substituído pela função correta

    if df_W is not None and not df_W.empty:
        executor.analisar_resultados(df_W, parametro_variavel='W')
        executor.realizar_teste_t_pareado(df_W)
        # CORREÇÃO 2: Usar o método correto para resumo estatístico
        executor.gerar_resumo_resultados(df_W)  # Substituído pela função correta
    
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