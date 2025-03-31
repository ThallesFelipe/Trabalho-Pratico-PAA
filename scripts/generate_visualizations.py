import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
import numpy as np

# Adicionar diretório raiz ao path para importar config.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from python.config import RESULTS_DIR, GRAPHS_DIR

# Configuração de estilo
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("colorblind")

# Garantir que o diretório de gráficos exista
os.makedirs(GRAPHS_DIR, exist_ok=True)

# Carregar dados com parse dates=False para garantir que tempo seja lido corretamente
print("Carregando dados...")
df_n = pd.read_csv(os.path.join(RESULTS_DIR, "resultados_variando_n.csv"), 
                  names=["n", "W", "algoritmo", "instancia", "tempo", "valor"])
df_W = pd.read_csv(os.path.join(RESULTS_DIR, "resultados_variando_W.csv"),
                  names=["n", "W", "algoritmo", "instancia", "tempo", "valor"])

# Garantir que as colunas numéricas sejam do tipo correto
print("Processando dados...")
try:
    # Converter tempo para float - se for string com valores concatenados, 
    # pegamos apenas o primeiro valor
    for df in [df_n, df_W]:
        # Verificar se tempo já é numérico
        if df['tempo'].dtype == object:
            # Se for string, tenta extrair o primeiro número
            df['tempo'] = df['tempo'].astype(str).str.extract(r'(\d+\.\d+)').astype(float)
        
        # Garantir que outras colunas também sejam numéricas
        df['n'] = pd.to_numeric(df['n'], errors='coerce')
        df['W'] = pd.to_numeric(df['W'], errors='coerce')
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    
    print(f"Dados processados. Formato tempo: {df_n['tempo'].dtype}")
except Exception as e:
    print(f"Erro ao processar dados: {e}")
    # Exibir algumas linhas para debug
    print("Exemplo de valores na coluna tempo:")
    print(df_n['tempo'].head())

# 1. Gráfico de tempo médio por algoritmo e tamanho n
plt.figure(figsize=(10, 6))
sns.lineplot(data=df_n, x="n", y="tempo", hue="algoritmo", marker="o", err_style="bars")
plt.title("Tempo de Execução por Tamanho da Entrada (n)")
plt.xlabel("Número de Itens (n)")
plt.ylabel("Tempo (s)")
plt.yscale("log")
plt.grid(True, alpha=0.3)
plt.savefig(os.path.join(GRAPHS_DIR, "tempo_vs_n.png"), dpi=300)
plt.close()

# 2. Gráfico de tempo médio por algoritmo e capacidade W
plt.figure(figsize=(10, 6))
sns.lineplot(data=df_W, x="W", y="tempo", hue="algoritmo", marker="o", err_style="bars")
plt.title("Tempo de Execução vs. Capacidade da Mochila (W)", fontsize=14)
plt.xlabel("Capacidade da Mochila (W)", fontsize=12)
plt.ylabel("Tempo Médio (segundos)", fontsize=12)
plt.yscale("log")
plt.tight_layout()
plt.savefig(os.path.join(GRAPHS_DIR, "tempo_vs_W.png"), dpi=300)
plt.close()

# 3. Boxplot para mostrar variabilidade dos algoritmos
plt.figure(figsize=(10, 6))
algorithm_names = {
    'run_dynamic_programming': 'Programação Dinâmica',
    'run_branch_and_bound': 'Branch and Bound',
    'run_backtracking': 'Backtracking'
}

# Filter out any rows where algoritmo is 'algoritmo' (header row)
df_n = df_n[df_n['algoritmo'] != 'algoritmo']

df_n['algoritmo_nome'] = df_n['algoritmo'].map(algorithm_names)

# Add debugging to see what values we have and ensure mapping works
print("Valores únicos na coluna 'algoritmo':", df_n['algoritmo'].unique())
print("Valores únicos após mapeamento:", df_n['algoritmo_nome'].unique())

# Check if any NaN values were introduced by the mapping
if df_n['algoritmo_nome'].isnull().any():
    print("AVISO: Alguns algoritmos não foram mapeados corretamente!")
    # Fall back to using original algorithm names if mapping failed
    df_n['algoritmo_nome'] = df_n['algoritmo_nome'].fillna(df_n['algoritmo'])

# Apply the same filtering and mapping to df_W
df_W = df_W[df_W['algoritmo'] != 'algoritmo']
df_W['algoritmo_nome'] = df_W['algoritmo'].map(algorithm_names)

sns.boxplot(data=df_n, x="algoritmo_nome", y="tempo")
plt.title("Variabilidade no Tempo de Execução por Algoritmo", fontsize=14)
plt.xlabel("Algoritmo", fontsize=12)
plt.ylabel("Tempo (segundos)", fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(GRAPHS_DIR, "variabilidade_algoritmos.png"), dpi=300)

# 4. Heatmap de comparação de desempenho para diferentes valores de n e W
try:
    # Agregação explícita para evitar problemas de tipo
    print("Criando pivot table...")
    # Primeiro agrupa e calcula a média para garantir valores numéricos
    agg_data = df_n.groupby(['n', 'algoritmo'])['tempo'].mean().reset_index()
    
    # Depois cria o pivot com os dados já agregados
    pivot_data = agg_data.pivot(
        index="n", 
        columns="algoritmo", 
        values="tempo"
    )
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_data, annot=True, fmt=".5f", cmap="YlGnBu")
    plt.title("Comparativo de Tempo de Execução por Tamanho do Problema", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHS_DIR, "heatmap_comparativo.png"), dpi=300)
    plt.close()
except Exception as e:
    print(f"Erro ao gerar heatmap: {e}")

print(f"Visualizações geradas com sucesso! Gráficos salvos em: {GRAPHS_DIR}")