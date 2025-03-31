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

# Definir estilo global para todos os gráficos
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'figure.figsize': (12, 8),
    'font.size': 13,
    'axes.titlesize': 18,
    'axes.labelsize': 15,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 12,
    'font.family': 'DejaVu Sans',
    'axes.grid': True,
    'grid.alpha': 0.5,
    'axes.spines.top': False,
    'axes.spines.right': False
})

# Paletas de cores consistentes
PALETTE = "viridis"
ALGORITMO_COLORS = {
    'Programação Dinâmica': '#1f77b4',  # azul
    'Backtracking': '#ff7f0e',          # laranja
    'Branch and Bound': '#2ca02c'       # verde
}

# Adicionar dicionário de tradução para nomes mais amigáveis
ALGORITMO_NAMES = {
    'run_dynamic_programming': 'Programação Dinâmica',
    'run_backtracking': 'Backtracking',
    'run_branch_and_bound': 'Branch and Bound',
    # Versões sem o prefixo 'run_'
    'dynamic_programming': 'Programação Dinâmica',
    'backtracking': 'Backtracking',
    'branch_and_bound': 'Branch and Bound'
}

def verificar_arquivo_csv(arquivo):
    """Verifica se o arquivo CSV existe e não está vazio."""
    return os.path.exists(arquivo) and os.path.getsize(arquivo) > 0

def limpar_e_converter_dados(df):
    """Limpa e converte os dados para os tipos corretos."""
    if df is None or df.empty:
        return df
    
    df = df.copy()
    
    # Converter tempo para float
    if 'tempo' in df.columns:
        df['tempo'] = pd.to_numeric(df['tempo'], errors='coerce')
    
    # Converter outras colunas numéricas
    for col in ['n', 'W', 'valor']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Remover linhas com tempo NaN
    df = df.dropna(subset=['tempo'])
    
    # Converter nomes de algoritmos para formato legível
    if 'algoritmo' in df.columns:
        algoritmo_map = {
            'run_dynamic_programming': 'Programação Dinâmica',
            'run_backtracking': 'Backtracking',
            'run_branch_and_bound': 'Branch and Bound',
            'dynamic_programming': 'Programação Dinâmica',
            'backtracking': 'Backtracking',
            'branch_and_bound': 'Branch and Bound'
        }
        df['algoritmo'] = df['algoritmo'].map(algoritmo_map).fillna(df['algoritmo'])
    
    return df

def gerar_grafico_tempo_por_parametro(df, parametro_variavel):
    """Gera gráfico de tempo de execução em função do parâmetro variado."""
    plt.figure(figsize=(12, 8))
    
    # Agrupar por parâmetro e algoritmo, calcular estatísticas
    stats_df = df.groupby([parametro_variavel, 'algoritmo'])['tempo'].agg(
        ['mean', 'std', 'count']
    ).reset_index()
    
    # Calcular intervalo de confiança de 95%
    stats_df['erro'] = stats_df['std'] / np.sqrt(stats_df['count']) * 1.96
    
    # Plotar gráfico para cada algoritmo
    for algoritmo in df['algoritmo'].unique():
        dados_alg = stats_df[stats_df['algoritmo'] == algoritmo]
        plt.errorbar(
            dados_alg[parametro_variavel],
            dados_alg['mean'],
            yerr=dados_alg['erro'],
            marker='o',
            capsize=5,
            label=ALGORITMO_NAMES.get(algoritmo, algoritmo)
        )
    
    # Configurações do gráfico
    plt.title(f'Tempo de Execução vs {parametro_variavel.upper()}')
    plt.xlabel(f'{"Número de itens (n)" if parametro_variavel == "n" else "Capacidade da mochila (W)"}')
    plt.ylabel('Tempo de execução (segundos)')
    plt.yscale('log')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Salvar o gráfico
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHS_DIR, f'tempo_por_{parametro_variavel}.png'), dpi=300)
    plt.close()

def gerar_grafico_valor_por_parametro(df, parametro_variavel):
    """Gera gráfico de valor máximo encontrado em função do parâmetro variado."""
    if df is None or df.empty or 'valor' not in df.columns:
        return
    
    plt.figure(figsize=(12, 8))
    
    # Agrupar dados
    agrupado = df.groupby([parametro_variavel, 'algoritmo']).agg(
        valor_medio=('valor', 'mean'),
        valor_max=('valor', 'max')
    ).reset_index()
    
    # Plotar para cada algoritmo
    for alg in agrupado['algoritmo'].unique():
        dados = agrupado[agrupado['algoritmo'] == alg]
        plt.plot(
            dados[parametro_variavel], 
            dados['valor_medio'],
            'o-',
            linewidth=2.5, 
            markersize=8,
            label=alg,
            color=ALGORITMO_COLORS.get(alg, None)
        )
    
    # Configurar o gráfico
    titulo = 'Valor Ótimo por Número de Itens (n)' if parametro_variavel == 'n' else 'Valor Ótimo por Capacidade da Mochila (W)'
    plt.title(titulo)
    plt.xlabel('Número de itens (n)' if parametro_variavel == 'n' else 'Capacidade da mochila (W)')
    plt.ylabel('Valor máximo encontrado')
    
    # Usar escala log se tiver múltiplos valores
    if len(agrupado[parametro_variavel].unique()) > 1:
        plt.xscale('log', base=2)
    
    plt.legend(title="Algoritmos")
    plt.grid(True, which="both", ls="--", alpha=0.7)
    
    # Salvar figura com alta qualidade
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHS_DIR, f'valor_vs_{parametro_variavel}.png'), dpi=300)
    plt.close()

def gerar_grafico_eficiencia(df_combinado):
    """Gera gráfico de eficiência (valor/tempo) para comparar algoritmos."""
    if df_combinado is None or df_combinado.empty or 'valor' not in df_combinado.columns:
        return
    
    # Calcular métrica de eficiência
    df_combinado['eficiencia'] = df_combinado['valor'] / df_combinado['tempo']
    
    plt.figure(figsize=(10, 8))
    
    sns.boxplot(
        x='algoritmo', 
        y='eficiencia', 
        hue='algoritmo',
        data=df_combinado,
        palette=ALGORITMO_COLORS,
        legend=False
    )
    
    plt.title('Eficiência dos Algoritmos (Valor/Tempo)')
    plt.xlabel('Algoritmo')
    plt.ylabel('Eficiência (valor/segundo)')
    plt.yscale('log')
    
    # Adicionar valores médios nas caixas
    medias = df_combinado.groupby('algoritmo')['eficiencia'].mean()
    for i, alg in enumerate(medias.index):
        plt.text(
            i, 
            medias[alg] * 1.1,
            f'Média: {medias[alg]:.1f}',
            ha='center',
            fontsize=10,
            fontweight='bold'
        )
    
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHS_DIR, 'eficiencia_algoritmos.png'), dpi=300)
    plt.close()

def gerar_grafico_comparativo_parametros(df):
    """Gera gráfico de barras comparando algoritmos para diferentes combinações de parâmetros."""
    if df is None or df.empty or 'n' not in df.columns or 'W' not in df.columns:
        return
    
    # Selecionar combinações relevantes de parâmetros
    parametros = df[['n', 'W']].drop_duplicates().sort_values(['n', 'W'])
    
    # Limitar a até 5 combinações para legibilidade
    if len(parametros) > 5:
        # Selecionar alguns pontos representativos
        indices = np.linspace(0, len(parametros)-1, 5, dtype=int)
        parametros = parametros.iloc[indices]
    
    # Coletar dados para o gráfico
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
                'tempo': tempo_medio,
                'parametros': f"n={int(n_val)}\nW={int(w_val)}"
            })
    
    if not dados_plot:
        return
    
    df_plot = pd.DataFrame(dados_plot)
    
    plt.figure(figsize=(14, 8))
    ax = sns.barplot(
        x='parametros',
        y='tempo',
        hue='algoritmo',
        data=df_plot,
        palette=ALGORITMO_COLORS
    )
    
    # Configurar o gráfico
    plt.title('Comparação de Tempo de Execução por Parâmetros')
    plt.xlabel('Parâmetros de Entrada')
    plt.ylabel('Tempo médio (segundos)')
    plt.yscale('log')
    
    # Adicionar valores nas barras
    for container in ax.containers:
        ax.bar_label(container, fmt='%.2e', fontsize=9)
    
    plt.legend(title="Algoritmos")
    
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHS_DIR, 'comparacao_parametros.png'), dpi=300)
    plt.close()

def gerar_heatmap_tempos(df):
    """Gera um heatmap mostrando o tempo médio de execução para diferentes valores de n e W."""
    if df is None or df.empty or 'n' not in df.columns or 'W' not in df.columns:
        return
    
    # Criar um heatmap para cada algoritmo
    for algoritmo in df['algoritmo'].unique():
        df_alg = df[df['algoritmo'] == algoritmo]
        
        # Criar pivot table para o heatmap
        pivot = pd.pivot_table(
            df_alg,
            values='tempo',
            index='n',
            columns='W',
            aggfunc='mean'
        )
        
        if pivot.empty or pivot.size < 4:
            continue
            
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            pivot,
            annot=True,
            fmt=".3f",
            cmap="YlGnBu",
            linewidths=0.5,
            cbar_kws={'label': 'Tempo (s)'}
        )
        
        plt.title(f'Tempo de Execução - {algoritmo}')
        plt.xlabel('Capacidade da mochila (W)')
        plt.ylabel('Número de itens (n)')
        
        plt.tight_layout()
        plt.savefig(os.path.join(GRAPHS_DIR, f'heatmap_{algoritmo.replace(" ", "_").lower()}.png'), dpi=300)
        plt.close()

def gerar_grafico_speedup(df, parametro_base='n'):
    """Gera gráfico de speedup relativo entre os algoritmos."""
    if df is None or df.empty or parametro_base not in df.columns:
        return
    
    # Agrupar tempos médios por parâmetro e algoritmo
    tempos_medios = df.groupby([parametro_base, 'algoritmo'])['tempo'].mean().reset_index()
    
    # Pivotar para ter algoritmos como colunas
    tempos_pivot = tempos_medios.pivot(index=parametro_base, columns='algoritmo', values='tempo')
    
    # Verificar se temos pelo menos dois algoritmos
    if tempos_pivot.shape[1] < 2:
        return
    
    # Escolher o algoritmo mais lento como base para speedup
    algoritmo_base = tempos_pivot.mean().idxmax()
    
    # Calcular speedup
    for algoritmo in tempos_pivot.columns:
        if algoritmo != algoritmo_base:
            tempos_pivot[f'Speedup {algoritmo}'] = tempos_pivot[algoritmo_base] / tempos_pivot[algoritmo]
    
    # Criar gráfico de speedup
    plt.figure(figsize=(12, 8))
    
    # Plotar apenas as colunas de speedup
    speedup_cols = [col for col in tempos_pivot.columns if col.startswith('Speedup')]
    for col in speedup_cols:
        alg = col.replace('Speedup ', '')
        plt.plot(
            tempos_pivot.index,
            tempos_pivot[col],
            'o-',
            linewidth=2.5,
            markersize=8,
            label=f"{alg} vs {algoritmo_base}",
            color=ALGORITMO_COLORS.get(alg, None)
        )
    
    plt.axhline(y=1, color='red', linestyle='--', alpha=0.7, label=f'Baseline ({algoritmo_base})')
    
    # Configurar gráfico
    titulo = f'Speedup Relativo por {parametro_base.upper()}'
    plt.title(titulo)
    plt.xlabel(f'{"Número de itens (n)" if parametro_base == "n" else "Capacidade da mochila (W)"}')
    plt.ylabel('Speedup (x vezes mais rápido)')
    
    if len(tempos_pivot.index) > 1:
        plt.xscale('log', base=2)
    
    plt.grid(True, which="both", ls="--", alpha=0.7)
    plt.legend(title="Comparação")
    
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHS_DIR, f'speedup_{parametro_base}.png'), dpi=300)
    plt.close()

# Adicionar esta função para gerar gráficos de análise assintótica
def gerar_grafico_analise_assintotica(df, algoritmo):
    """Gera gráfico para análise assintótica (n vs tempo) para um algoritmo específico."""
    if df.empty or 'n' not in df.columns or 'tempo' not in df.columns:
        print(f"Dados insuficientes para análise assintótica de {algoritmo}")
        return
        
    dados_alg = df[df['algoritmo'] == algoritmo].copy()
    if dados_alg.empty:
        print(f"Sem dados para o algoritmo {algoritmo}")
        return
    
    # Agrupar por n e calcular média
    dados_agrupados = dados_alg.groupby('n')['tempo'].mean().reset_index()
    
    # Check if we have enough data points for curve fitting
    if len(dados_agrupados) < 3:
        print(f"Dados insuficientes para ajuste de curvas para {algoritmo} (mínimo 3 pontos, encontrado {len(dados_agrupados)})")
        
        # Still plot the scatter points
        plt.figure(figsize=(10, 7))
        plt.scatter(dados_agrupados['n'], dados_agrupados['tempo'], marker='o', s=60, label='Dados reais')
        plt.title(f'Análise Assintótica - {ALGORITMO_NAMES.get(algoritmo, algoritmo)} (Dados insuficientes)')
        plt.xlabel('Número de itens (n)')
        plt.ylabel('Tempo de execução (segundos)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Salvar gráfico
        nome_arquivo = f'analise_assintotica_{algoritmo.replace("run_", "")}.png'
        plt.savefig(os.path.join(GRAPHS_DIR, nome_arquivo), dpi=300)
        plt.close()
        return
        
    # Continue with curve fitting if we have enough data points
    from scipy.optimize import curve_fit
    
    def linear(x, a, b):
        return a * x + b
        
    def quadratica(x, a, b, c):
        return a * x**2 + b * x + c
    
    def exponencial(x, a, b):
        return a * np.exp(b * x)
    
    x_data = dados_agrupados['n'].values
    y_data = dados_agrupados['tempo'].values
    x_line = np.linspace(min(x_data), max(x_data), 100)
    
    try:
        # Ajuste linear
        params_lin, _ = curve_fit(linear, x_data, y_data)
        plt.plot(x_line, linear(x_line, *params_lin), 'r-', label=f'Linear: {params_lin[0]:.4f}n + {params_lin[1]:.4f}')
        
        # Ajuste quadrático
        params_quad, _ = curve_fit(quadratica, x_data, y_data)
        plt.plot(x_line, quadratica(x_line, *params_quad), 'g-', 
                label=f'Quadrática: {params_quad[0]:.4e}n² + {params_quad[1]:.4e}n + {params_quad[2]:.4e}')
        
        # Ajuste exponencial (se os dados permitirem)
        if all(y > 0 for y in y_data):
            params_exp, _ = curve_fit(exponencial, x_data, y_data, maxfev=2000)
            plt.plot(x_line, exponencial(x_line, *params_exp), 'b-', 
                    label=f'Exponencial: {params_exp[0]:.4e}·e^({params_exp[1]:.4e}·n)')
    except Exception as e:
        print(f"Erro no ajuste de curvas para {algoritmo}: {e}")
    
    # Formatar gráfico
    plt.title(f'Análise Assintótica - {ALGORITMO_NAMES.get(algoritmo, algoritmo)}')
    plt.xlabel('Número de itens (n)')
    plt.ylabel('Tempo de execução (segundos)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Salvar gráfico
    nome_arquivo = f'analise_assintotica_{algoritmo.replace("run_", "")}.png'
    plt.savefig(os.path.join(GRAPHS_DIR, nome_arquivo), dpi=300)
    plt.close()

def main():
    """Função principal para gerar todas as visualizações."""
    print("Iniciando geração de visualizações...")
    
    # Verificar se os arquivos de resultados existem
    arquivos = [
        os.path.join(RESULTS_DIR, 'resultados_variando_n.csv'),
        os.path.join(RESULTS_DIR, 'resultados_variando_W.csv')
    ]
    
    dados_disponiveis = []
    
    # Carregar dados de experimentos variando n
    df_n = None
    if verificar_arquivo_csv(arquivos[0]):
        df_n = pd.read_csv(arquivos[0])
        df_n = limpar_e_converter_dados(df_n)
        dados_disponiveis.append('n')
        print(f"Dados carregados do arquivo {arquivos[0]}: {len(df_n)} registros")
    
    # Carregar dados de experimentos variando W
    df_W = None
    if verificar_arquivo_csv(arquivos[1]):
        df_W = pd.read_csv(arquivos[1])
        df_W = limpar_e_converter_dados(df_W)
        dados_disponiveis.append('W')
        print(f"Dados carregados do arquivo {arquivos[1]}: {len(df_W)} registros")
    
    # Gerar visualizações
    if 'n' in dados_disponiveis:
        print("Gerando gráficos para experimentos variando n...")
        gerar_grafico_tempo_por_parametro(df_n, 'n')
        gerar_grafico_valor_por_parametro(df_n, 'n')
        
        # Gerar gráficos de análise assintótica para cada algoritmo
        algoritmos = df_n['algoritmo'].unique()
        for alg in algoritmos:
            gerar_grafico_analise_assintotica(df_n, alg)
    
    if 'W' in dados_disponiveis:
        print("Gerando gráficos para experimentos variando W...")
        gerar_grafico_tempo_por_parametro(df_W, 'W')
        gerar_grafico_valor_por_parametro(df_W, 'W')
    
    if df_n is not None and df_W is not None:
        print("Gerando gráfico comparativo de parâmetros...")
        gerar_grafico_comparativo_parametros(pd.concat([df_n, df_W]))
    
    print("Geração de visualizações concluída!")

if __name__ == "__main__":
    main()