import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Importar configuração
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RESULTS_DIR, GRAPHS_DIR

# Assegurar que o diretório de gráficos existe
os.makedirs(GRAPHS_DIR, exist_ok=True)

def verificar_arquivo_csv(arquivo):
    """Verifica se o arquivo CSV existe e não está vazio."""
    if not os.path.exists(arquivo):
        print(f"Arquivo não encontrado: {arquivo}")
        return False
    
    if os.path.getsize(arquivo) == 0:
        print(f"Arquivo vazio: {arquivo}")
        return False
    
    return True

def limpar_e_converter_dados(df):
    """Limpa e converte os dados para os tipos corretos."""
    if df is None or df.empty:
        return df
    
    # Fazer uma cópia para evitar SettingWithCopyWarning
    df = df.copy()
    
    # Converter tempo para float
    if 'tempo' in df.columns:
        if df['tempo'].dtype == object:
            # Extrair valores numéricos de strings como "0.123456 segundos"
            df['tempo'] = df['tempo'].astype(str).str.extract(r'(\d+\.?\d*)').astype(float)
        else:
            df['tempo'] = pd.to_numeric(df['tempo'], errors='coerce')
    
    # Converter outras colunas numéricas
    for col in ['n', 'W', 'valor']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Remover linhas com NaN
    df = df.dropna(subset=['tempo'])
    
    # Converter nomes de algoritmos para um formato mais legível
    if 'algoritmo' in df.columns:
        df['algoritmo'] = df['algoritmo'].str.replace('run_', '').str.replace('_', ' ').str.title()
    
    return df

def gerar_graficos_tempo(df, parametro_variavel):
    """Gera gráficos de tempo de execução."""
    if df is None or df.empty:
        return
    
    plt.figure(figsize=(12, 8))
    
    # Configurar estilo
    sns.set_style("whitegrid")
    plt.rcParams['font.size'] = 12
    
    # Agrupar dados
    agrupado = df.groupby([parametro_variavel, 'algoritmo'])['tempo'].agg(['mean', 'std']).reset_index()
    
    # Plotar para cada algoritmo
    for algoritmo in agrupado['algoritmo'].unique():
        dados_alg = agrupado[agrupado['algoritmo'] == algoritmo]
        
        x = dados_alg[parametro_variavel]
        y = dados_alg['mean']
        erro = dados_alg['std']
        
        plt.errorbar(x, y, yerr=erro, fmt='o-', linewidth=2, capsize=5, label=algoritmo)
    
    # Configurar gráfico
    plt.xlabel(f'{parametro_variavel.upper()}', fontsize=14)
    plt.ylabel('Tempo de execução (s)', fontsize=14)
    plt.title(f'Tempo de execução vs {parametro_variavel.upper()}', fontsize=16)
    
    if len(agrupado[parametro_variavel].unique()) > 1:
        plt.xscale('log', base=2)
    
    plt.yscale('log')
    plt.grid(True, which="both", ls="--", alpha=0.7)
    plt.legend(fontsize=12)
    
    # Salvar figura
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHS_DIR, f'tempo_vs_{parametro_variavel}.png'), dpi=300)
    plt.close()

def gerar_graficos_valor(df, parametro_variavel):
    """Gera gráficos de valor máximo encontrado."""
    if df is None or df.empty or 'valor' not in df.columns:
        return
    
    plt.figure(figsize=(12, 8))
    
    # Configurar estilo
    sns.set_style("whitegrid")
    plt.rcParams['font.size'] = 12
    
    # Agrupar dados
    agrupado = df.groupby([parametro_variavel, 'algoritmo'])['valor'].agg(['mean']).reset_index()
    
    # Plotar para cada algoritmo
    for algoritmo in agrupado['algoritmo'].unique():
        dados_alg = agrupado[agrupado['algoritmo'] == algoritmo]
        
        x = dados_alg[parametro_variavel]
        y = dados_alg['mean']
        
        plt.plot(x, y, 'o-', linewidth=2, markersize=8, label=algoritmo)
    
    # Configurar gráfico
    plt.xlabel(f'{parametro_variavel.upper()}', fontsize=14)
    plt.ylabel('Valor máximo encontrado', fontsize=14)
    plt.title(f'Valor máximo vs {parametro_variavel.upper()}', fontsize=16)
    
    if len(agrupado[parametro_variavel].unique()) > 1:
        plt.xscale('log', base=2)
    
    plt.grid(True, which="both", ls="--", alpha=0.7)
    plt.legend(fontsize=12)
    
    # Salvar figura
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHS_DIR, f'valor_vs_{parametro_variavel}.png'), dpi=300)
    plt.close()

def gerar_grafico_barras_comparativo(df):
    """Gera um gráfico de barras comparando os algoritmos."""
    if df is None or df.empty:
        return
    
    plt.figure(figsize=(14, 10))
    
    # Configurar estilo
    sns.set_style("whitegrid")
    plt.rcParams['font.size'] = 12
    
    # Criar visualização com base nos parâmetros disponíveis
    if 'n' in df.columns and 'W' in df.columns:
        # Agrupar por n, W e algoritmo
        parametros = df[['n', 'W']].drop_duplicates().sort_values(['n', 'W'])
        
        # Limitar a 5 combinações para legibilidade
        if len(parametros) > 5:
            parametros = parametros.iloc[:5]
        
        # Preparar dados para o gráfico
        dados_plot = []
        
        for _, row in parametros.iterrows():
            n_val, w_val = row['n'], row['W']
            df_filtrado = df[(df['n'] == n_val) & (df['W'] == w_val)]
            
            for alg in df_filtrado['algoritmo'].unique():
                tempo_medio = df_filtrado[df_filtrado['algoritmo'] == alg]['tempo'].mean()
                dados_plot.append({
                    'n': n_val, 
                    'W': w_val, 
                    'algoritmo': alg,
                    'tempo': tempo_medio
                })
        
        df_plot = pd.DataFrame(dados_plot)
        
        # Criar rótulos para o eixo x
        df_plot['parametros'] = df_plot.apply(lambda x: f"n={int(x['n'])}, W={int(x['W'])}", axis=1)
        
        # Plotar gráfico
        sns.barplot(x='parametros', y='tempo', hue='algoritmo', data=df_plot)
        
        plt.title('Comparação de Tempo por Combinação de Parâmetros', fontsize=16)
        plt.xlabel('Parâmetros (n, W)', fontsize=14)
        plt.ylabel('Tempo médio (s)', fontsize=14)
        plt.yscale('log')
        plt.xticks(rotation=45)
        plt.legend(title='Algoritmo')
        plt.grid(True, which="both", ls="--", alpha=0.5)
        
        # Salvar figura
        plt.tight_layout()
        plt.savefig(os.path.join(GRAPHS_DIR, 'comparacao_parametros.png'), dpi=300)
        plt.close()

# Carregar e processar dados
print("Iniciando geração de visualizações...")

# Inicializando DataFrames
df_n = None
df_W = None

# Verificar e carregar resultados de variação de n
arquivo_n = os.path.join(RESULTS_DIR, "resultados_variando_n.csv")
if verificar_arquivo_csv(arquivo_n):
    try:
        df_n = pd.read_csv(arquivo_n)
        df_n = limpar_e_converter_dados(df_n)
        print(f"Dados de variação de n carregados: {len(df_n)} registros")
    except Exception as e:
        print(f"Erro ao processar {arquivo_n}: {e}")

# Verificar e carregar resultados de variação de W
arquivo_W = os.path.join(RESULTS_DIR, "resultados_variando_W.csv")
if verificar_arquivo_csv(arquivo_W):
    try:
        df_W = pd.read_csv(arquivo_W)
        df_W = limpar_e_converter_dados(df_W)
        print(f"Dados de variação de W carregados: {len(df_W)} registros")
    except Exception as e:
        print(f"Erro ao processar {arquivo_W}: {e}")

# Verificar se algum dos DataFrames foi carregado com sucesso
if (df_n is None or df_n.empty) and (df_W is None or df_W.empty):
    print("Nenhum dado válido para gerar visualizações.")
    sys.exit(1)

print("Gerando visualizações...")

# Visualizações para variação de n
if df_n is not None and not df_n.empty:
    gerar_graficos_tempo(df_n, 'n')
    gerar_graficos_valor(df_n, 'n')

# Visualizações para variação de W
if df_W is not None and not df_W.empty:
    gerar_graficos_tempo(df_W, 'W')
    gerar_graficos_valor(df_W, 'W')

# Visualização comparativa combinando dados
df_combinado = pd.concat([df_n, df_W]) if df_n is not None and df_W is not None else (df_n if df_n is not None else df_W)
if df_combinado is not None and not df_combinado.empty:
    gerar_grafico_barras_comparativo(df_combinado)

print(f"Visualizações geradas com sucesso. Arquivos salvos em: {GRAPHS_DIR}")