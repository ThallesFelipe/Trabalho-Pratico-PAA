"""
Script para execução de experimentos com os algoritmos do Problema da Mochila.

Este script realiza testes de desempenho dos algoritmos de:
- Programação Dinâmica
- Backtracking
- Branch and Bound

Permite variar o número de itens (n) e a capacidade da mochila (W),
gerando gráficos comparativos de tempo de execução e valores máximos encontrados.

Data: Março 2025
"""

import os
import subprocess
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import pandas as pd
import glob
import signal
import concurrent.futures
import sys
import seaborn as sns
import platform

# Adiciona o diretório raiz ao path para importações relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import path converter
from path_converter import convert_to_wsl_path

# Detect if running in WSL
is_wsl = "microsoft" in os.uname().release.lower() if hasattr(os, 'uname') else False

try:
    from config import BINARY_DIR, OUTPUT_DIR, INSTANCES_DIR, RESULTS_DIR, GRAPHS_DIR
    
    # Convert paths to WSL format if running in WSL
    if is_wsl:
        BINARY_DIR = convert_to_wsl_path(BINARY_DIR)
        OUTPUT_DIR = convert_to_wsl_path(OUTPUT_DIR)
        INSTANCES_DIR = convert_to_wsl_path(INSTANCES_DIR)
        RESULTS_DIR = convert_to_wsl_path(RESULTS_DIR)
        GRAPHS_DIR = convert_to_wsl_path(GRAPHS_DIR)
    
    print(f"Diretórios carregados: {BINARY_DIR, OUTPUT_DIR, INSTANCES_DIR, RESULTS_DIR, GRAPHS_DIR}")
except ImportError as e:
    print(f"Erro ao importar as configurações: {e}")
    # Configurações padrão para continuar a execução
    import os
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    BINARY_DIR = os.path.join(PROJECT_ROOT, "bin")
    OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")  
    INSTANCES_DIR = os.path.join(PROJECT_ROOT, "instances")
    RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
    GRAPHS_DIR = os.path.join(PROJECT_ROOT, "graphs")
    print(f"Usando diretórios padrão: {BINARY_DIR, OUTPUT_DIR, INSTANCES_DIR, RESULTS_DIR, GRAPHS_DIR}")

class TimeoutException(Exception):
    """Exceção lançada quando um algoritmo excede o tempo limite de execução."""
    pass

def timeout_handler(signum, frame):
    """Manipulador de sinal para timeout."""
    raise TimeoutException("Tempo limite excedido")

class ExecutorExperimentos:
    """Classe para execução e análise de experimentos com algoritmos do Problema da Mochila."""
    
    def __init__(self, diretorio_binarios=None, diretorio_instancias=None, 
                 diretorio_resultados=None, diretorio_graficos=None):
        """Inicializa o executor com os diretórios necessários."""
        # Configuração de diretórios
        self.eh_windows = platform.system() == "Windows"
        
        # Obter diretório raiz do projeto
        projeto_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
        # Configurar diretórios padrão se não informados
        self.diretorio_binarios = diretorio_binarios or os.path.join(projeto_raiz, "bin")
        self.diretorio_instancias = diretorio_instancias or os.path.join(projeto_raiz, "output", "instances")
        self.diretorio_resultados = diretorio_resultados or os.path.join(projeto_raiz, "output", "results")
        self.diretorio_graficos = diretorio_graficos or os.path.join(self.diretorio_resultados, "graficos")
        
        # Criar diretórios se não existirem
        for diretorio in [self.diretorio_resultados, self.diretorio_graficos]:
            os.makedirs(diretorio, exist_ok=True)
            
        # Verificar existência dos diretórios necessários
        if not os.path.exists(self.diretorio_binarios):
            print(f"AVISO: Diretório de binários '{self.diretorio_binarios}' não encontrado!")
        
        if not os.path.exists(self.diretorio_instancias):
            print(f"AVISO: Diretório de instâncias '{self.diretorio_instancias}' não encontrado!")
            os.makedirs(self.diretorio_instancias, exist_ok=True)
            print(f"Diretório de instâncias criado em '{self.diretorio_instancias}'")
        
        # Dicionário para armazenar resultados dos algoritmos
        self.resultados = {
            'run_dynamic_programming': [],  # Programação Dinâmica
            'run_backtracking': [],         # Backtracking
            'run_branch_and_bound': []      # Branch and Bound
        }
        
        # Verifica o sistema operacional
        self.eh_windows = os.name == 'nt'
        # Detecta WSL
        self.eh_wsl = "microsoft" in os.uname().release.lower() if hasattr(os, 'uname') else False
        
        # Carrega caminhos da configuração
        self.diretorio_binarios = BINARY_DIR if BINARY_DIR else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "bin"))
        self.diretorio_saida = OUTPUT_DIR if OUTPUT_DIR else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
        self.diretorio_instancias = INSTANCES_DIR if INSTANCES_DIR else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "instances"))
        self.diretorio_resultados = RESULTS_DIR if RESULTS_DIR else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
        self.diretorio_graficos = GRAPHS_DIR if GRAPHS_DIR else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "graphs"))
        
        # Convert paths for WSL if needed
        if self.eh_wsl:
            self.diretorio_binarios = convert_to_wsl_path(self.diretorio_binarios)
            self.diretorio_saida = convert_to_wsl_path(self.diretorio_saida)
            self.diretorio_instancias = convert_to_wsl_path(self.diretorio_instancias)
            self.diretorio_resultados = convert_to_wsl_path(self.diretorio_resultados)
            self.diretorio_graficos = convert_to_wsl_path(self.diretorio_graficos)
        
        print(f"Usando diretórios: {self.diretorio_binarios, self.diretorio_saida, self.diretorio_instancias, self.diretorio_resultados, self.diretorio_graficos}")
        
        # Cria diretórios necessários se não existirem
        for diretorio in [self.diretorio_saida, self.diretorio_instancias, self.diretorio_resultados, self.diretorio_graficos]:
            if diretorio:  # Só cria o diretório se o caminho não for vazio
                os.makedirs(diretorio, exist_ok=True)
    
    def executar_algoritmo(self, algoritmo, arquivo_instancia, timeout=30):
        """Executa um algoritmo específico em uma instância e retorna o tempo e valor."""
        
        # Determina o executável a ser usado
        executavel = os.path.join(self.diretorio_binarios, algoritmo)
        if self.eh_windows and not executavel.endswith('.exe'):
            executavel += '.exe'
        
        # Verifica se o executável existe
        if not os.path.exists(executavel):
            print(f"Executável '{executavel}' não encontrado!")
            return None, None
        
        # Configura handler de timeout para sistemas Unix
        if not self.eh_windows:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
        
        try:
            print(f"Executando {algoritmo} em {arquivo_instancia}")
            
            # Inicia medição de tempo
            tempo_inicio = time.time()
            
            # Executa o processo com tratamento diferenciado para Windows
            if self.eh_windows:
                try:
                    resultado = subprocess.run([executavel, arquivo_instancia], 
                                          capture_output=True, text=True, timeout=timeout)
                except subprocess.TimeoutExpired:
                    print(f"  - {algoritmo} excedeu o tempo limite de {timeout} segundos")
                    return None, None
            else:
                resultado = subprocess.run([executavel, arquivo_instancia], 
                                      capture_output=True, text=True)
                signal.alarm(0)  # Desativa o alarme após a execução
            
            # Calcula o tempo de execução
            tempo_execucao = time.time() - tempo_inicio
            
            # Verifica se a execução foi bem-sucedida
            if resultado.returncode != 0:
                print(f"  - {algoritmo} falhou com código {resultado.returncode}")
                print(f"  - Erro: {resultado.stderr}")
                return None, None
            
            # Analisa a saída para extrair o valor máximo
            linhas_saida = resultado.stdout.strip().split('\n')
            valor_maximo = None

            # Procura por "Valor máximo:" na saída
            for linha in linhas_saida:
                if "Valor máximo:" in linha:
                    try:
                        valor_maximo = int(linha.split(":")[-1].strip())
                        break
                    except ValueError:
                        print(f"  - {algoritmo} formato de saída inválido: '{linha}'")
                        print(f"  - Saída completa: {resultado.stdout}")
                        return None, None

            # Verificação adicional
            if valor_maximo is None:
                print(f"  - {algoritmo} não retornou um valor máximo")
                print(f"  - Saída completa: {resultado.stdout}")
                if resultado.stderr:
                    print(f"  - Erro: {resultado.stderr}")
                return None, None
            
            return tempo_execucao, valor_maximo
        
        except (subprocess.TimeoutExpired, TimeoutException):
            if not self.eh_windows:
                signal.alarm(0)  # Desativa o alarme em caso de timeout
            print(f"  - {algoritmo} excedeu o tempo limite de {timeout} segundos")
            return None, None
        
        except Exception as e:
            if not self.eh_windows:
                signal.alarm(0)  # Desativa o alarme em caso de erro
            print(f"  - {algoritmo} erro inesperado: {str(e)}")
            return None, None
    
    def executar_variando_n(self, valores_n=[10, 20, 30, 40, 50], W=50, num_instancias=5):
        """Executa experimentos variando o número de itens."""
        resultados = []
        
        # Para cada valor de n
        for n in valores_n:
            # Para cada instância
            for instancia in range(1, num_instancias + 1):
                # Constrói o caminho do arquivo de instância
                arquivo_instancia = os.path.join(self.diretorio_instancias, 
                                               f"instancia_n{n}_W{W}_{instancia}.txt")
                
                # Verifica se o arquivo existe
                if not os.path.exists(arquivo_instancia):
                    print(f"Arquivo {arquivo_instancia} não encontrado, pulando...")
                    continue
                
                # Define algoritmos a executar baseado no tamanho de n
                algoritmos = ['run_dynamic_programming', 'run_branch_and_bound']
                
                # Determina limite seguro para backtracking
                limite_seguro_backtracking = 100
                if n <= limite_seguro_backtracking:
                    algoritmos.append('run_backtracking')
                else:
                    print(f"  Pulando backtracking para n={n} (> {limite_seguro_backtracking})")
                    resultados.append({
                        'n': n,
                        'W': W,
                        'algoritmo': 'run_backtracking',
                        'instancia': instancia,
                        'tempo': None,
                        'valor': None
                    })
                
                # Executa cada algoritmo
                for algoritmo in algoritmos:
                    tempo_execucao, valor = self.executar_algoritmo(algoritmo, arquivo_instancia)
                    
                    resultados.append({
                        'n': n,
                        'W': W,
                        'algoritmo': algoritmo,
                        'instancia': instancia,
                        'tempo': tempo_execucao,
                        'valor': valor
                    })
        
        # Salva resultados em CSV
        df_resultados = pd.DataFrame(resultados)
        df_resultados.to_csv(os.path.join(self.diretorio_resultados, 'resultados_variando_n.csv'), 
                           index=False)
        
        # Analisa e gera gráficos dos resultados
        self.analisar_resultados(df_resultados, parametro_variavel='n')
        
        return df_resultados
    
    def executar_variando_W(self, valores_W=[20, 40, 60, 80, 100], n=30, num_instancias=5):
        """
        Executa experimentos variando a capacidade da mochila (W).
        
        Args:
            valores_W (list): Lista de valores de W a serem testados.
            n (int): Número de itens fixo para todos os testes.
            num_instancias (int): Número de instâncias aleatórias a gerar para cada configuração.
            
        Returns:
            DataFrame: DataFrame pandas com os resultados.
        """
        # Similar ao executar_variando_n, mas variando W
        resultados = []
        
        for W in valores_W:
            print(f"\nExecutando experimentos com n={n}, W={W}")
            
            # Verifica se o diretório de instâncias existe ou cria-o
            nome_diretorio = os.path.join(self.diretorio_instancias, f"instancias_n{n}_W{W}")
            if not os.path.exists(nome_diretorio):
                os.makedirs(nome_diretorio, exist_ok=True)
                # Executa gerador de instâncias
                self.executar_gerador_instancias(num_instancias, n, W)
            
            # Executa cada instância
            for instancia in range(1, num_instancias + 1):
                arquivo_instancia = os.path.join(self.diretorio_instancias, 
                                               f"instancias_n{n}_W{W}/instancia_{instancia}.txt")
                
                if not os.path.exists(arquivo_instancia):
                    print(f"Arquivo {arquivo_instancia} não encontrado, pulando...")
                    continue
                
                # Para n grande, pular backtracking
                algoritmos = ['run_dynamic_programming', 'run_branch_and_bound']
                if n <= 100:
                    algoritmos.append('run_backtracking')
                
                # Testa cada algoritmo
                for algoritmo in algoritmos:
                    tempo_execucao, valor = self.executar_algoritmo(algoritmo, arquivo_instancia)
                    
                    resultados.append({
                        'W': W,
                        'n': n,
                        'algoritmo': algoritmo,
                        'instancia': instancia,
                        'tempo': tempo_execucao,
                        'valor': valor
                    })
        
        # Salva resultados em CSV
        df_resultados = pd.DataFrame(resultados)
        df_resultados.to_csv(os.path.join(self.diretorio_resultados, 'resultados_variando_W.csv'), 
                           index=False)
        
        # Analisa e gera gráficos dos resultados
        self.analisar_resultados(df_resultados, parametro_variavel='W')
        
        return df_resultados
    
    def analisar_resultados(self, df_resultados, parametro_variavel='n'):
        """
        Analisa resultados e gera gráficos comparativos.
        
        Args:
            df_resultados (DataFrame): DataFrame com resultados dos experimentos.
            parametro_variavel (str): Parâmetro variado no experimento ('n' ou 'W').
        """
        if df_resultados.empty:
            print(f"Sem resultados para analisar (param={parametro_variavel})")
            return
            
        # Extrai valores únicos do parâmetro e algoritmos
        valores_parametro = sorted(df_resultados[parametro_variavel].unique())
        algoritmos = sorted(df_resultados['algoritmo'].unique())
        
        # Inicializa listas para tempos médios e intervalos de confiança
        tempos_medios = []
        intervalos_confianca = []
        
        # Calcula estatísticas para cada algoritmo
        for algoritmo in algoritmos:
            medias_algoritmo = []
            ic_algoritmo = []
            
            for valor_param in valores_parametro:
                # Filtra resultados para este algoritmo e valor do parâmetro
                dados_filtrados = df_resultados[(df_resultados['algoritmo'] == algoritmo) & 
                                            (df_resultados[parametro_variavel] == valor_param)]
                
                if dados_filtrados.empty:
                    medias_algoritmo.append(np.nan)
                    ic_algoritmo.append(np.nan)
                    continue
                
                # Remove valores None/NaN
                tempos = dados_filtrados['tempo'].dropna().values
                
                if len(tempos) == 0:
                    medias_algoritmo.append(np.nan)
                    ic_algoritmo.append(np.nan)
                    continue
                    
                # Calcula a média
                media = np.mean(tempos)
                
                # Verifica se há amostras suficientes para intervalo de confiança
                if len(tempos) <= 1:
                    medias_algoritmo.append(media)
                    ic_algoritmo.append(0)  # Sem intervalo com uma única amostra
                    continue
                
                # Calcula o intervalo de confiança de 95%
                ic = stats.t.interval(0.95, len(tempos)-1, loc=media, scale=stats.sem(tempos))
                medias_algoritmo.append(media)
                ic_algoritmo.append((ic[1] - ic[0]) / 2)
            
            tempos_medios.append(medias_algoritmo)
            intervalos_confianca.append(ic_algoritmo)
        
        # Gera gráfico de tempo de execução
        plt.figure(figsize=(10, 6))
        for i, algoritmo in enumerate(algoritmos):
            indices_validos = [j for j, x in enumerate(tempos_medios[i]) if not np.isnan(x)]
            if not indices_validos:
                continue
                
            x_valores = [valores_parametro[j] for j in indices_validos]
            y_valores = [tempos_medios[i][j] for j in indices_validos]
            erros = [intervalos_confianca[i][j] for j in indices_validos]
            
            plt.errorbar(x_valores, y_valores, yerr=erros, 
                         fmt='o-', label=algoritmo, capsize=5)
        
        plt.xlabel(f'Valor de {parametro_variavel}')
        plt.ylabel('Tempo médio de execução (s)')
        plt.title(f'Tempo médio de execução variando {parametro_variavel}')
        plt.legend()
        plt.grid(True)
        if len(valores_parametro) > 1:
            plt.xscale('log', base=2)
            plt.yscale('log')
        plt.savefig(os.path.join(self.diretorio_graficos, f'tempo_vs_{parametro_variavel}.png'))
        plt.close()
        
        # Gera gráfico de valores máximos
        plt.figure(figsize=(10, 6))
        for algoritmo in algoritmos:
            valores_algoritmo = []
            for valor_param in valores_parametro:
                dados_filtrados = df_resultados[(df_resultados['algoritmo'] == algoritmo) & 
                                            (df_resultados[parametro_variavel] == valor_param)]
                
                if dados_filtrados.empty or dados_filtrados['valor'].isna().all():
                    valores_algoritmo.append(np.nan)
                    continue
                
                valores_algoritmo.append(dados_filtrados['valor'].mean())
            
            indices_validos = [i for i, x in enumerate(valores_algoritmo) if not np.isnan(x)]
            if not indices_validos:
                continue
                
            x_valores = [valores_parametro[i] for i in indices_validos]
            y_valores = [valores_algoritmo[i] for i in indices_validos]
            
            plt.plot(x_valores, y_valores, 'o-', label=algoritmo)
        
        plt.xlabel(f'Valor de {parametro_variavel}')
        plt.ylabel('Valor máximo encontrado')
        plt.title(f'Valor máximo encontrado variando {parametro_variavel}')
        plt.legend()
        plt.grid(True)
        if len(valores_parametro) > 1:
            plt.xscale('log', base=2)
        plt.savefig(os.path.join(self.diretorio_graficos, f'valor_vs_{parametro_variavel}.png'))
        plt.close()
    
    def gerar_graficos_comparativos(self, df_resultados):
        """Gera gráficos mais informativos para comparação dos algoritmos."""
        # Definir estilo visual consistente
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # Configuração para melhor legibilidade
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 12
        
        # 1. Gráfico comparativo principal com barras de erro
        for param_variavel in ['n', 'W']:
            # Agrupar dados por parâmetro variável e algoritmo
            agrupado = df_resultados.groupby([param_variavel, 'algoritmo'])['tempo'].agg(['mean', 'std']).reset_index()
            
            # Criar figura com tamanho adequado
            plt.figure(figsize=(14, 8))
            
            # Lista de algoritmos para cores consistentes
            algoritmos = df_resultados['algoritmo'].unique()
            cores = plt.cm.tab10(np.linspace(0, 1, len(algoritmos)))
            
            # Plotar cada algoritmo com barras de erro
            for i, alg in enumerate(algoritmos):
                dados_alg = agrupado[agrupado['algoritmo'] == alg]
                plt.errorbar(dados_alg[param_variavel], dados_alg['mean'], 
                             yerr=dados_alg['std'], fmt='o-', 
                             linewidth=2, capsize=5, 
                             label=alg.replace('run_', ''), 
                             color=cores[i])
            
            # Adicionar anotações para valores importantes
            for i, alg in enumerate(algoritmos):
                dados_alg = agrupado[agrupado['algoritmo'] == alg]
                # Anotar apenas alguns pontos importantes para não sobrecarregar
                for j, row in dados_alg.iterrows():
                    if j % 2 == 0:  # Anotar apenas pontos alternados
                        plt.text(row[param_variavel], row['mean']*1.05, 
                                 f"{row['mean']:.4f}s", 
                                 ha='center', fontsize=9, color=cores[i])
            
            # Melhorar layout e legendas
            plt.title(f'Comparação de Tempo de Execução por {param_variavel.upper()}', fontsize=16, fontweight='bold')
            plt.xlabel(f'Valor de {param_variavel}', fontsize=14)
            plt.ylabel('Tempo médio (segundos)', fontsize=14)
            plt.grid(True, alpha=0.3, linestyle='--')
            plt.legend(title='Algoritmo', fontsize=12, loc='best')
            
            # Ajustar escala do eixo Y para melhor visualização
            plt.yscale('log')
            plt.tight_layout()
            
            # Salvar com alta resolução
            plt.savefig(os.path.join(self.diretorio_graficos, f'comparacao_tempo_{param_variavel}.png'), dpi=300)
            plt.close()
        
        # 2. Gráfico de boxplot para distribuição dos tempos
        plt.figure(figsize=(14, 8))
        sns.boxplot(x='algoritmo', y='tempo', hue='algoritmo', 
                    data=df_resultados, palette='tab10')
        plt.title('Distribuição dos Tempos de Execução por Algoritmo', fontsize=16, fontweight='bold')
        plt.xlabel('Algoritmo', fontsize=14)
        plt.ylabel('Tempo (segundos)', fontsize=14)
        plt.yscale('log')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.diretorio_graficos, 'distribuicao_tempos.png'), dpi=300)
        plt.close()
    
    def executar_gerador_instancias(self, num_instancias, n, W):
        """
        Executa o gerador de instâncias para criar casos de teste.
        
        Args:
            num_instancias (int): Número de instâncias a gerar.
            n (int): Número de itens em cada instância.
            W (int): Capacidade da mochila.
        """
        # Cria diretório para instâncias desta configuração
        nome_diretorio = os.path.join(self.diretorio_instancias, f"instancias_n{n}_W{W}")
        os.makedirs(nome_diretorio, exist_ok=True)
        
        # Seleciona o executável conforme sistema operacional
        if self.eh_windows:
            gerador = os.path.join(self.diretorio_binarios, "generate_instances.exe")
        else:
            gerador = os.path.join(self.diretorio_binarios, "generate_instances")
        
        # Define variáveis de ambiente para o gerador
        env = os.environ.copy()
        env["INSTANCES_DIR"] = self.diretorio_instancias
        
        # Executa o gerador de instâncias
        try:
            resultado = subprocess.run(
                [gerador, str(num_instancias), str(n), str(W)], 
                capture_output=True, 
                text=True, 
                env=env
            )
            if resultado.returncode != 0:
                print(f"  Erro ao gerar instâncias: {resultado.stderr}")
            else:
                print(f"  Instâncias geradas com sucesso")
        except Exception as e:
            print(f"  Erro ao gerar instâncias: {str(e)}")
    
    def realizar_teste_t_pareado(self, df_resultados):
        """Realiza teste t pareado entre algoritmos e apresenta de forma mais clara."""
        from scipy import stats
        import numpy as np
        from tabulate import tabulate
        
        # Add robust error handling
        if df_resultados is None or df_resultados.empty:
            print("Sem dados suficientes para realizar teste t pareado.")
            return
            
        # Check if required columns exist
        required_columns = ['algoritmo', 'tempo', 'n', 'W']
        for col in required_columns:
            if col not in df_resultados.columns:
                print(f"Erro: Coluna '{col}' não encontrada no DataFrame.")
                print(f"Colunas disponíveis: {list(df_resultados.columns)}")
                return
        
        algoritmos = df_resultados['algoritmo'].unique()
        
        # Create results table
        tabela_resultados = []
        cabecalho = ["Algoritmo A", "Algoritmo B", "Média A (s)", "Média B (s)", 
                     "Diferença (%)", "p-valor", "Melhor"]
        
        print("\n" + "="*80)
        print("RESULTADOS DO TESTE T PAREADO (95% DE CONFIANÇA)")
        print("="*80)
        
        # For each algorithm pair
        for i in range(len(algoritmos)):
            for j in range(i+1, len(algoritmos)):
                alg1 = algoritmos[i]
                alg2 = algoritmos[j]
                
                # For each combination of parameters (n, W)
                for n in df_resultados['n'].unique():
                    for w in df_resultados['W'].unique():
                        # Filter data for the same parameters and instances
                        df_filtrado = df_resultados[(df_resultados['n'] == n) & 
                                                   (df_resultados['W'] == w)]
                        
                        # Check if results exist for both algorithms
                        if alg1 not in df_filtrado['algoritmo'].values or alg2 not in df_filtrado['algoritmo'].values:
                            continue
                            
                        # Get times for each algorithm
                        tempos_alg1 = df_filtrado[df_filtrado['algoritmo'] == alg1]['tempo'].values
                        tempos_alg2 = df_filtrado[df_filtrado['algoritmo'] == alg2]['tempo'].values
                        
                        # Ensure both have the same number of instances
                        min_len = min(len(tempos_alg1), len(tempos_alg2))
                        if min_len <= 1:
                            continue
                            
                        tempos_alg1 = tempos_alg1[:min_len]
                        tempos_alg2 = tempos_alg2[:min_len]
                        
                        try:
                            # Perform paired t-test with error handling
                            t_stat, p_valor = stats.ttest_rel(tempos_alg1, tempos_alg2)
                            
                            # Calculate means and percent difference
                            media_a = np.mean(tempos_alg1)
                            media_b = np.mean(tempos_alg2)
                            
                            # Handle division by zero
                            if media_a == 0:
                                diff_percent = float('inf') if media_b > 0 else 0
                            else:
                                diff_percent = ((media_b - media_a) / media_a) * 100
                            
                            # Determine the better algorithm
                            if p_valor < 0.05:  # Statistically significant
                                melhor = alg1.replace('run_', '') if media_a < media_b else alg2.replace('run_', '')
                                resultado = f"{melhor} (95% conf.)"
                            else:
                                resultado = "Empate estatístico"
                            
                            # Add row to results table
                            tabela_resultados.append([
                                alg1.replace('run_', ''),
                                alg2.replace('run_', ''),
                                f"{media_a:.6f}",
                                f"{media_b:.6f}",
                                f"{diff_percent:.2f}%",
                                f"{p_valor:.6f}",
                                resultado
                            ])
                        except Exception as e:
                            print(f"Erro ao realizar teste para {alg1} vs {alg2} (n={n}, W={w}): {str(e)}")
        
        # Print formatted table
        print(tabulate(tabela_resultados, headers=cabecalho, tablefmt="grid"))
        print("\n")
        
        # Save results to a CSV file for reference
        with open(os.path.join(self.diretorio_resultados, 'resultados_teste_t.csv'), 'w') as f:
            f.write(','.join(cabecalho) + '\n')
            for linha in tabela_resultados:
                f.write(','.join([str(item) for item in linha]) + '\n')
    
    def gerar_resumo_resultados(self, df_resultados):
        """Gera um resumo claro e conciso dos resultados dos experimentos."""
        import pandas as pd
        from tabulate import tabulate
        
        # Criar diretório para relatórios se não existir
        os.makedirs(os.path.join(self.diretorio_resultados, 'relatorios'), exist_ok=True)
        
        # 1. Resumo por algoritmo (independente de parâmetros)
        resumo_algoritmos = df_resultados.groupby('algoritmo')['tempo'].agg(
            ['count', 'min', 'max', 'mean', 'std', 'median']
        ).reset_index()
        
        # Formatar colunas para melhor legibilidade
        resumo_formatado = resumo_algoritmos.copy()
        resumo_formatado['min'] = resumo_formatado['min'].map('{:.6f}'.format)
        resumo_formatado['max'] = resumo_formatado['max'].map('{:.6f}'.format)
        resumo_formatado['mean'] = resumo_formatado['mean'].map('{:.6f}'.format)
        resumo_formatado['std'] = resumo_formatado['std'].map('{:.6f}'.format)
        resumo_formatado['median'] = resumo_formatado['median'].map('{:.6f}'.format)
        
        # Renomear algoritmos para melhor apresentação
        resumo_formatado['algoritmo'] = resumo_formatado['algoritmo'].str.replace('run_', '')
        
        # Renomear colunas para o relatório
        resumo_formatado.columns = ['Algoritmo', 'Execuções', 'Tempo Mínimo (s)', 
                                   'Tempo Máximo (s)', 'Tempo Médio (s)', 
                                   'Desvio Padrão (s)', 'Mediana (s)']
        
        # Escrever relatório de resumo geral
        with open(os.path.join(self.diretorio_resultados, 'relatorios', 'resumo_geral.md'), 'w') as f:
            f.write("# Resumo dos Resultados - Problema da Mochila\n\n")
            f.write("## Estatísticas Gerais por Algoritmo\n\n")
            f.write(tabulate(resumo_formatado, headers='keys', tablefmt='pipe', showindex=False))
            f.write("\n\n")
            
            # Identificar o algoritmo mais rápido em média
            idx_mais_rapido = resumo_algoritmos['mean'].idxmin()
            alg_mais_rapido = resumo_algoritmos.iloc[idx_mais_rapido]['algoritmo'].replace('run_', '')
            tempo_medio = resumo_algoritmos.iloc[idx_mais_rapido]['mean']
            
            f.write(f"### Conclusão Preliminar\n\n")
            f.write(f"- O algoritmo mais rápido em média foi: **{alg_mais_rapido}** com tempo médio de {tempo_medio:.6f} segundos.\n")
            f.write(f"- Esta é uma avaliação preliminar considerando todos os tamanhos de instância juntos.\n")
            f.write(f"- Para uma análise mais precisa, consulte os resultados dos testes estatísticos pareados.\n\n")
        
        # 2. Resumo por tamanho de instância (n e W)
        for param in ['n', 'W']:
            # Gerar resumo
            resumo_param = df_resultados.groupby([param, 'algoritmo'])['tempo'].mean().unstack().reset_index()
            
            # Garantir que todas as colunas estejam presentes (mesmo que não haja dados)
            for alg in df_resultados['algoritmo'].unique():
                if alg not in resumo_param.columns:
                    resumo_param[alg] = float('nan')
            
            # Formatação para o relatório
            with open(os.path.join(self.diretorio_resultados, 'relatorios', f'resumo_por_{param}.md'), 'w') as f:
                f.write(f"# Resumo dos Resultados por {param.upper()}\n\n")
                f.write("## Tempo Médio de Execução (segundos)\n\n")
                
                # Renomear colunas para melhor apresentação
                colunas_renomeadas = {col: col.replace('run_', '') for col in resumo_param.columns if col != param}
                resumo_param = resumo_param.rename(columns=colunas_renomeadas)
                
                f.write(tabulate(resumo_param, headers='keys', tablefmt='pipe', showindex=False))
                f.write("\n\n")
                
                # Adicionar análise detalhada por valor do parâmetro
                f.write("## Análise Detalhada\n\n")
                
                for val in sorted(df_resultados[param].unique()):
                    f.write(f"### {param.upper()} = {val}\n\n")
                    
                    # Filtrar resultados para este valor do parâmetro
                    df_filtrado = df_resultados[df_resultados[param] == val]
                    
                    # Encontrar o algoritmo mais rápido para este parâmetro
                    media_por_alg = df_filtrado.groupby('algoritmo')['tempo'].mean()
                    alg_mais_rapido = media_por_alg.idxmin().replace('run_', '')
                    tempo_medio = media_por_alg.min()
                    
                    f.write(f"- Algoritmo mais rápido: **{alg_mais_rapido}**\n")
                    f.write(f"- Tempo médio: {tempo_medio:.6f} segundos\n\n")
        
        print(f"Resumos gerados com sucesso! Verifique os arquivos em: {os.path.join(self.diretorio_resultados, 'relatorios')}")

    def gerar_visualizacoes_avancadas(self):
        """Gera visualizações avançadas adicionais baseadas nos resultados dos experimentos."""
        import pandas as pd
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
        
        print("\nGerando visualizações avançadas...")
        
        # Carregar dados
        df_n_path = os.path.join(self.diretorio_resultados, "resultados_variando_n.csv")
        df_W_path = os.path.join(self.diretorio_resultados, "resultados_variando_W.csv")
        
        if not os.path.exists(df_n_path) or not os.path.exists(df_W_path):
            print("Arquivos de resultados não encontrados. Execute os experimentos primeiro.")
            return
            
        df_n = pd.read_csv(df_n_path)
        df_W = pd.read_csv(df_W_path)
        
        # Configuração de estilo
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_palette("colorblind")
        
        # 1. Gráfico de tempo médio por algoritmo e tamanho n
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df_n, x="n", y="tempo", hue="algoritmo", marker="o", err_style="bars")
        plt.title("Tempo de Execução por Tamanho da Entrada (n)")
        plt.xlabel("Número de Itens (n)")
        plt.ylabel("Tempo (s)")
        plt.yscale("log")
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(self.diretorio_graficos, "tempo_vs_n_avancado.png"), dpi=300)
        plt.close()
        
        # 2. Gráfico de tempo médio por algoritmo e capacidade W
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df_W, x="W", y="tempo", hue="algoritmo", marker="o", err_style="bars")
        plt.title("Tempo de Execução vs. Capacidade da Mochila (W)", fontsize=14)
        plt.xlabel("Capacidade (W)")
        plt.ylabel("Tempo (s)")
        plt.yscale("log")
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(self.diretorio_graficos, "tempo_vs_W_avancado.png"), dpi=300)
        plt.close()
        
        # 3. Heatmap para comparação de algoritmos
        pivot_data = df_n.pivot_table(
            index="n", 
            columns="algoritmo", 
            values="tempo", 
            aggfunc="mean"
        )
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot_data, annot=True, fmt=".5f", cmap="YlGnBu")
        plt.title("Comparativo de Tempo de Execução por Tamanho do Problema", fontsize=14)
        plt.tight_layout()
        plt.savefig(os.path.join(self.diretorio_graficos, "heatmap_comparativo.png"), dpi=300)
        plt.close()
        
        print(f"Visualizações avançadas geradas com sucesso em: {self.diretorio_graficos}")

def main():
    """Função principal para coordenar a execução dos experimentos."""
    executor = ExecutorExperimentos()
    
    # Verifica se existem resultados salvos
    arquivo_resultados_n = os.path.join(executor.diretorio_resultados, 'resultados_variando_n.csv')
    arquivo_resultados_W = os.path.join(executor.diretorio_resultados, 'resultados_variando_W.csv')
    
    # Experimentos variando n
    if os.path.exists(arquivo_resultados_n):
        print(f"Carregando resultados existentes de {arquivo_resultados_n}")
        df_resultados_n = pd.read_csv(arquivo_resultados_n)
    else:
        print("Executando experimentos variando n")
        df_resultados_n = executor.executar_variando_n()
    
    # Experimentos variando W
    if os.path.exists(arquivo_resultados_W):
        print(f"Carregando resultados existentes de {arquivo_resultados_W}")
        df_resultados_W = pd.read_csv(arquivo_resultados_W)
    else:
        print("Executando experimentos variando W")
        df_resultados_W = executor.executar_variando_W()
    
    # Gera gráficos a partir dos resultados
    executor.analisar_resultados(df_resultados_n, parametro_variavel='n')
    executor.analisar_resultados(df_resultados_W, parametro_variavel='W')
    
    # Realiza análise estatística para comparar algoritmos
    print("\n===== Análise Estatística: Comparação entre Algoritmos =====")
    print("\nResultados para experimentos variando n:")
    executor.realizar_teste_t_pareado(df_resultados_n)
    
    print("\nResultados para experimentos variando W:")
    executor.realizar_teste_t_pareado(df_resultados_W)
    
    # Gera resumos dos resultados
    executor.gerar_resumo_resultados(df_resultados_n)
    executor.gerar_resumo_resultados(df_resultados_W)
    
    # Gera visualizações avançadas
    executor.gerar_visualizacoes_avancadas()
    
    print("\nExperimentos concluídos e resultados analisados!")
    print(f"Gráficos salvos em: {executor.diretorio_graficos}")
    print(f"Resultados CSV salvos em: {executor.diretorio_resultados}")


if __name__ == "__main__":
    main()