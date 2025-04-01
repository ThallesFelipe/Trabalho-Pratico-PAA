#!/usr/bin/env python3
"""
Enhanced analysis script for the Knapsack Problem algorithms.
This script runs experiments with more data points and generates improved visualizations.
"""

import os
import sys
import time
from pathlib import Path

# Add directories to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "python"))

# Import required modules
from python.experiments import ExecutorExperimentos

def run_enhanced_analysis():
    print("="*80)
    print("ENHANCED ANALYSIS OF KNAPSACK PROBLEM ALGORITHMS")
    print("="*80)
    
    # Initialize experiment executor
    executor = ExecutorExperimentos()
    
    # Initialize CSV files
    executor.inicializar_arquivos_csv()
    
    # Enhanced configuration with more data points
    config = {
        'valores_n': [10, 15, 20, 25, 30, 35, 40],  # n values
        'valores_W': [20, 40, 60, 80, 100],         # W values
        'num_instancias': 3,                        # Number of instances per configuration
        'timeout_algoritmo': 180,                   # Timeout in seconds
        'W_fixo': 50,                               # Fixed W for n experiments
        'n_fixo': 20                                # Fixed n for W experiments
}
    
    print("\nCONFIGURATION:")
    print(f"- n values: {config['valores_n']}")
    print(f"- W values: {config['valores_W']}")
    print(f"- Instances per configuration: {config['num_instancias']}")
    print(f"- Timeout: {config['timeout_algoritmo']} seconds")
    
    # Phase 1: Run n experiments
    print("\n" + "-"*80)
    print("PHASE 1: RUNNING EXPERIMENTS WITH VARYING n")
    print("-"*80)
    df_n = executor.executar_variando_n(
        valores_n=config['valores_n'], 
        W=config['W_fixo'], 
        num_instancias=config['num_instancias']
    )
    
    # Phase 2: Run W experiments
    print("\n" + "-"*80)
    print("PHASE 2: RUNNING EXPERIMENTS WITH VARYING W")
    print("-"*80)
    df_W = executor.executar_variando_W(
        valores_W=config['valores_W'], 
        n=config['n_fixo'], 
        num_instancias=config['num_instancias']
    )
    
    # Phase 3: Statistical analysis
    print("\n" + "-"*80)
    print("PHASE 3: STATISTICAL ANALYSIS")
    print("-"*80)
    executor.analisar_resultados(df_n, parametro_variavel='n')
    executor.realizar_teste_t_pareado(df_n)
    
    executor.analisar_resultados(df_W, parametro_variavel='W')
    executor.realizar_teste_t_pareado(df_W)
    
    executor.gerar_resumo_resultados(df_n)
    executor.gerar_resumo_resultados(df_W)
    
    # Phase 4: Generate standard visualizations
    print("\n" + "-"*80)
    print("PHASE 4: GENERATING STANDARD VISUALIZATIONS")
    print("-"*80)
    executor.gerar_graficos_comparativos(df_n)
    executor.gerar_graficos_comparativos(df_W)
    
    # Phase 5: Generate enhanced visualizations
    print("\n" + "-"*80)
    print("PHASE 5: GENERATING ENHANCED VISUALIZATIONS")
    print("-"*80)
    # Import and run the enhanced visualizations
    sys.path.insert(0, str(Path(__file__).parent / "scripts"))
    from scripts.enhanced_visualizations import main as generate_enhanced_viz
    generate_enhanced_viz()
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nResults saved in: {executor.diretorio_resultados}")
    print(f"Visualizations saved in: {executor.diretorio_graficos}")

if __name__ == "__main__":
    start_time = time.time()
    try:
        run_enhanced_analysis()
        elapsed = time.time() - start_time
        print(f"\nTotal execution time: {elapsed/60:.2f} minutes")
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()