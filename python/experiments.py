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

# Adicionar após as importações iniciais:
def verificar_dependencias():
    """Verifica e instala dependências necessárias se não estiverem presentes."""
    try:
        import pkg_resources
        pacotes_necessarios = ['pandas', 'numpy', 'matplotlib', 'seaborn', 'openpyxl', 'scipy', 'tabulate']
        pacotes_instalar = []
        
        for pacote in pacotes_necessarios:
            try:
                pkg_resources.get_distribution(pacote)
            except pkg_resources.DistributionNotFound:
                pacotes_instalar.append(pacote)
        
        if pacotes_instalar:
            print(f"Instalando pacotes necessários: {', '.join(pacotes_instalar)}")
            import subprocess
            for pacote in pacotes_instalar:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pacote])
            print("Dependências instaladas com sucesso!")
    except Exception as e:
        print(f"Aviso: Verificação automática de dependências falhou: {e}")

# Chamar a função no início do script
verificar_dependencias()

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
        # Configuração de sistema
        self.eh_windows = platform.system() == "Windows"
        self.eh_wsl = "microsoft" in os.uname().release.lower() if hasattr(os, 'uname') else False
        
        # Carregar diretórios das configurações ou usar padrões
        self.diretorio_binarios = diretorio_binarios or BINARY_DIR
        self.diretorio_saida = OUTPUT_DIR
        self.diretorio_instancias = diretorio_instancias or INSTANCES_DIR
        self.diretorio_resultados = diretorio_resultados or RESULTS_DIR
        self.diretorio_graficos = diretorio_graficos or GRAPHS_DIR
        
        # Convert paths for WSL if needed
        if self.eh_wsl:
            self.diretorio_binarios = convert_to_wsl_path(self.diretorio_binarios)
            self.diretorio_saida = convert_to_wsl_path(self.diretorio_saida)
            self.diretorio_instancias = convert_to_wsl_path(self.diretorio_instancias)
            self.diretorio_resultados = convert_to_wsl_path(self.diretorio_resultados)
            self.diretorio_graficos = convert_to_wsl_path(self.diretorio_graficos)
        
        print(f"Usando diretórios: {self.diretorio_binarios}, {self.diretorio_instancias}, {self.diretorio_resultados}, {self.diretorio_graficos}")
        
        # Criar diretórios necessários se não existirem
        for diretorio in [self.diretorio_saida, self.diretorio_instancias, self.diretorio_resultados, self.diretorio_graficos]:
            if diretorio:  # Só cria se o caminho não for vazio
                os.makedirs(diretorio, exist_ok=True)
        
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
    
    def inicializar_arquivos_csv(self):
        """
        Inicializa os arquivos CSV com os cabeçalhos corretos se eles não existirem
        ou estiverem vazios.
        """
        import os
        
        # Definir caminhos dos arquivos
        arquivo_n = os.path.join(self.diretorio_resultados, 'resultados_variando_n.csv')
        arquivo_W = os.path.join(self.diretorio_resultados, 'resultados_variando_W.csv')
        
        # Verificar e inicializar arquivo para variação de n
        if not os.path.exists(arquivo_n) or os.path.getsize(arquivo_n) == 0:
            print(f"Inicializando arquivo {arquivo_n}")
            with open(arquivo_n, 'w') as f:
                f.write("n,W,algoritmo,instancia,tempo,valor\n")
        
        # Verificar e inicializar arquivo para variação de W
        if not os.path.exists(arquivo_W) or os.path.getsize(arquivo_W) == 0:
            print(f"Inicializando arquivo {arquivo_W}")
            with open(arquivo_W, 'w') as f:
                f.write("W,n,algoritmo,instancia,tempo,valor\n")
        
        print("Arquivos CSV inicializados com sucesso.")

    def executar_algoritmo(self, algoritmo, arquivo_instancia, timeout=60):
        """Executa um algoritmo específico em uma instância e retorna o tempo e valor."""
        # Determina o executável a ser usado
        executavel = os.path.join(self.diretorio_binarios, algoritmo)
        if self.eh_windows and not executavel.endswith('.exe'):
            executavel += '.exe'
        
        # Verifica se o executável existe
        if not os.path.exists(executavel):
            print(f"ERRO: Executável '{executavel}' não encontrado!")
            return None, None
        
        try:
            print(f"Executando {algoritmo} em {arquivo_instancia}")
            
            # Configura handler de timeout para sistemas Unix
            if not self.eh_windows:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout)
            
            # Inicia medição de tempo
            tempo_inicio = time.time()
            
            # Executa o processo com tratamento diferenciado para Windows
            try:
                resultado = subprocess.run(
                    [executavel, arquivo_instancia], 
                    capture_output=True, 
                    text=True, 
                    timeout=timeout
                )
                
                if not self.eh_windows:
                    signal.alarm(0)  # Desativa o alarme após a execução
                    
            except subprocess.TimeoutExpired:
                print(f"  - {algoritmo} excedeu o tempo limite de {timeout} segundos")
                return None, None
            
            # Calcula o tempo de execução
            tempo_execucao = time.time() - tempo_inicio
            
            # Verifica se a execução foi bem-sucedida
            if resultado.returncode != 0:
                print(f"  - {algoritmo} falhou com código {resultado.returncode}")
                if resultado.stderr:
                    print(f"  - Erro: {resultado.stderr}")
                return None, None
            
            # Analisa a saída para extrair o valor máximo
            valor_maximo = None
            for linha in resultado.stdout.strip().split('\n'):
                if "Valor máximo:" in linha:
                    try:
                        valor_maximo = int(linha.split(":")[-1].strip())
                        break
                    except ValueError:
                        print(f"  - Formato de saída inválido: '{linha}'")
                        continue
            
            if valor_maximo is None:
                print(f"  - Não foi possível obter o valor máximo da saída")
                return None, None
                
            return tempo_execucao, valor_maximo
            
        except (subprocess.TimeoutExpired, TimeoutException):
            if not self.eh_windows:
                signal.alarm(0)
            print(f"  - {algoritmo} excedeu o tempo limite de {timeout} segundos")
            return None, None
        except Exception as e:
            if not self.eh_windows:
                signal.alarm(0)
            print(f"  - Erro inesperado: {str(e)}")
            return None, None
    
    def executar_variando_n(self, valores_n=[10, 20, 30, 40, 50], W=50, num_instancias=5):
        """Executa experimentos variando o número de itens."""
        import os
        import pandas as pd
        
        resultados = []
        algoritmos = ['run_dynamic_programming', 'run_backtracking', 'run_branch_and_bound']
        
        for n in valores_n:
            print(f"Executando testes para n={n}, W={W}, {num_instancias} instâncias")
            
            # Gera instâncias para este valor de n
            instancias_geradas = self.executar_gerador_instancias(num_instancias, n, W)
            
            if not instancias_geradas:
                print(f"Não foi possível gerar instâncias para n={n}, W={W}. Pulando.")
                continue
            
            # Procura pelas instâncias geradas
            diretorio_instancias = os.path.join(self.diretorio_instancias, f"instancias_n{n}_W{W}")
            arquivos_instancias = [
                f for f in os.listdir(diretorio_instancias) 
                if f.startswith("instancia_") and f.endswith(".txt")
            ]
            
            for i, nome_arquivo in enumerate(arquivos_instancias[:num_instancias], 1):
                instancia = i
                arquivo_instancia = os.path.join(diretorio_instancias, nome_arquivo)
                
                print(f"  Testando instância {instancia} ({arquivo_instancia})")
                
                # Testa cada algoritmo
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
        if resultados:
            df_resultados = pd.DataFrame(resultados)
            arquivo_saida = os.path.join(self.diretorio_resultados, 'resultados_variando_n.csv')
            
            # Append to existing file if it exists and has header
            if os.path.exists(arquivo_saida) and os.path.getsize(arquivo_saida) > 0:
                df_existente = pd.read_csv(arquivo_saida)
                df_combinado = pd.concat([df_existente, df_resultados], ignore_index=True)
                df_combinado.to_csv(arquivo_saida, index=False)
                print(f"Resultados adicionados ao arquivo existente: {arquivo_saida}")
            else:
                df_resultados.to_csv(arquivo_saida, index=False)
                print(f"Resultados salvos em novo arquivo: {arquivo_saida}")
            
            # Analisa e gera gráficos dos resultados
            self.analisar_resultados(df_resultados, parametro_variavel='n')
            
            return df_resultados
        else:
            print("Nenhum resultado obtido para variação de n.")
            return pd.DataFrame()
    
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
        import os
        import pandas as pd
        
        resultados = []
        algoritmos = ['run_dynamic_programming', 'run_backtracking', 'run_branch_and_bound']
        
        for W in valores_W:
            print(f"Executando testes para W={W}, n={n}, {num_instancias} instâncias")
            
            # Gera instâncias para este valor de W
            instancias_geradas = self.executar_gerador_instancias(num_instancias, n, W)
            
            if not instancias_geradas:
                print(f"Não foi possível gerar instâncias para n={n}, W={W}. Pulando.")
                continue
            
            # Procura pelas instâncias geradas
            diretorio_instancias = os.path.join(self.diretorio_instancias, f"instancias_n{n}_W{W}")
            arquivos_instancias = [
                f for f in os.listdir(diretorio_instancias) 
                if f.startswith("instancia_") and f.endswith(".txt")
            ]
            
            for i, nome_arquivo in enumerate(arquivos_instancias[:num_instancias], 1):
                instancia = i
                arquivo_instancia = os.path.join(diretorio_instancias, nome_arquivo)
                
                print(f"  Testando instância {instancia} ({arquivo_instancia})")
                
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
        if resultados:
            df_resultados = pd.DataFrame(resultados)
            arquivo_saida = os.path.join(self.diretorio_resultados, 'resultados_variando_W.csv')
            
            # Append to existing file if it exists and has header
            if os.path.exists(arquivo_saida) and os.path.getsize(arquivo_saida) > 0:
                df_existente = pd.read_csv(arquivo_saida)
                df_combinado = pd.concat([df_existente, df_resultados], ignore_index=True)
                df_combinado.to_csv(arquivo_saida, index=False)
                print(f"Resultados adicionados ao arquivo existente: {arquivo_saida}")
            else:
                df_resultados.to_csv(arquivo_saida, index=False)
                print(f"Resultados salvos em novo arquivo: {arquivo_saida}")
            
            # Analisa e gera gráficos dos resultados
            self.analisar_resultados(df_resultados, parametro_variavel='W')
            
            return df_resultados
        else:
            print("Nenhum resultado obtido para variação de W.")
            return pd.DataFrame()
    
    def analisar_resultados(self, df_resultados, parametro_variavel='n'):
        """
        Analisa os resultados dos experimentos e gera gráficos.
        
        Args:
            df_resultados: DataFrame com os resultados dos experimentos.
            parametro_variavel: Parâmetro que foi variado nos experimentos ('n' ou 'W').
        """
        print("\n===== ANÁLISE DE RESULTADOS =====")
        
        # Verificar se o DataFrame está vazio
        if df_resultados.empty:
            print("Nenhum resultado para analisar.")
            return
        
        # Garantir que os tipos de dados estejam corretos
        df_resultados['tempo'] = pd.to_numeric(df_resultados['tempo'], errors='coerce')
        df_resultados[parametro_variavel] = pd.to_numeric(df_resultados[parametro_variavel], errors='coerce')
        
        # Verificação para ver se há dados válidos após conversão
        if df_resultados['tempo'].isna().all():
            print("Erro: Nenhum tempo válido para análise após conversão de tipos")
            return
        
        # Extrair algoritmos e valores do parâmetro variável
        algoritmos = df_resultados['algoritmo'].unique()
        valores_parametro = sorted(df_resultados[parametro_variavel].unique())
        
        print(f"\nAnalisando resultados variando {parametro_variavel}...")
        print(f"Valores de {parametro_variavel}: {valores_parametro}")
        print(f"Algoritmos: {algoritmos}")
        
        # Inicializa listas para tempos médios e intervalos de confiança
        tempos_medios = []
        intervalos_confianca = []
        valores_maximos = []
        
        # Tabela para resumo dos resultados
        tabela_resumo = []
        cabecalho_resumo = ["Algoritmo", f"{parametro_variavel.upper()}", "Tempo Médio (s)", "IC 95%", "Valor Máximo"]
        
        # Configurar estilo para os gráficos
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams['font.size'] = 12
        plt.rcParams['figure.figsize'] = (12, 8)
        
        # Calcula estatísticas para cada algoritmo
        for algoritmo in algoritmos:
            medias_algoritmo = []
            ic_algoritmo = []
            valores_algoritmo = []
            
            for valor_param in valores_parametro:
                # Filtra resultados para este algoritmo e valor do parâmetro
                dados_filtrados = df_resultados[(df_resultados['algoritmo'] == algoritmo) & 
                                            (df_resultados[parametro_variavel] == valor_param)]
                
                if dados_filtrados.empty:
                    medias_algoritmo.append(np.nan)
                    ic_algoritmo.append(np.nan)
                    valores_algoritmo.append(np.nan)
                    continue
                
                # Remove valores None/NaN
                tempos = dados_filtrados['tempo'].dropna().values
                valores = dados_filtrados['valor'].dropna().values if 'valor' in dados_filtrados.columns else np.array([0])
                
                if len(tempos) == 0:
                    medias_algoritmo.append(np.nan)
                    ic_algoritmo.append(np.nan)
                    valores_algoritmo.append(np.nan)
                    continue
                    
                # Calcula a média
                media = np.mean(tempos)
                
                # Verifica se há amostras suficientes para intervalo de confiança
                if len(tempos) <= 1:
                    medias_algoritmo.append(media)
                    ic_algoritmo.append(0)
                else:
                    # Calcula intervalo de confiança de 95%
                    intervalo = 1.96 * np.std(tempos, ddof=1) / np.sqrt(len(tempos))
                    medias_algoritmo.append(media)
                    ic_algoritmo.append(intervalo)
                
                # Valor máximo médio
                valor_medio = np.mean(valores) if len(valores) > 0 else np.nan
                valores_algoritmo.append(valor_medio)
                
                # Adicionar à tabela de resumo
                tabela_resumo.append([
                    algoritmo.replace('run_', ''),
                    valor_param,
                    f"{media:.6f}",
                    f"±{ic_algoritmo[-1]:.6f}" if not np.isnan(ic_algoritmo[-1]) else "N/A",
                    f"{valor_medio:.1f}" if not np.isnan(valor_medio) else "N/A"
                ])
            
            tempos_medios.append(medias_algoritmo)
            intervalos_confianca.append(ic_algoritmo)
            valores_maximos.append(valores_algoritmo)
        
        # Mostrar tabela de resumo
        print("\nResumo dos Resultados:")
        print("-" * 80)
        print(f"{cabecalho_resumo[0]:<15} {cabecalho_resumo[1]:<10} {cabecalho_resumo[2]:<20} {cabecalho_resumo[3]:<15} {cabecalho_resumo[4]:<15}")
        print("-" * 80)
        for linha in tabela_resumo:
            print(f"{linha[0]:<15} {linha[1]:<10} {linha[2]:<20} {linha[3]:<15} {linha[4]:<15}")
        print("-" * 80)
        
        # Gerar gráfico de tempos
        plt.figure(figsize=(10, 6))
        for i, algoritmo in enumerate(algoritmos):
            # Identificar índices de valores não-NaN
            indices_validos = [j for j, val in enumerate(tempos_medios[i]) if not np.isnan(val)]
            
            if not indices_validos:
                continue
                
            x_valores = [valores_parametro[j] for j in indices_validos]
            y_valores = [tempos_medios[i][j] for j in indices_validos]
            erros = [intervalos_confianca[i][j] for j in indices_validos]
            
            plt.errorbar(x_valores, y_valores, yerr=erros, fmt='o-', capsize=5, 
                        linewidth=2, label=algoritmo.replace('run_', ''))
        
        plt.xlabel(f'Valor de {parametro_variavel}')
        plt.ylabel('Tempo médio (segundos)')
        plt.title(f'Tempo de execução variando {parametro_variavel}')
        plt.legend()
        plt.grid(True)
        
        # Usar escala logarítmica se houver mais de um valor de parâmetro
        if len(valores_parametro) > 1:
            plt.xscale('log', base=2)
            plt.yscale('log')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.diretorio_graficos, f'tempo_vs_{parametro_variavel}.png'))
        plt.close()
        
        # Gerar gráfico de valores máximos (se houver)
        if 'valor' in df_resultados.columns:
            plt.figure(figsize=(10, 6))
            for i, algoritmo in enumerate(algoritmos):
                # Identificar índices de valores não-NaN
                indices_validos = [j for j, val in enumerate(valores_maximos[i]) if not np.isnan(val)]
                
                if not indices_validos:
                    continue
                    
                x_valores = [valores_parametro[j] for j in indices_validos]
                y_valores = [valores_maximos[i][j] for j in indices_validos]
                
                plt.plot(x_valores, y_valores, 'o-', linewidth=2, markersize=8, 
                        label=algoritmo.replace('run_', ''))
            
            plt.xlabel(f'Valor de {parametro_variavel}')
            plt.ylabel('Valor máximo encontrado')
            plt.title(f'Valor máximo encontrado variando {parametro_variavel}')
            plt.legend()
            plt.grid(True)
            
            if len(valores_parametro) > 1:
                plt.xscale('log', base=2)
            
            plt.tight_layout()
            plt.savefig(os.path.join(self.diretorio_graficos, f'valor_vs_{parametro_variavel}.png'))
            plt.close()
        
        print(f"Análise concluída. Gráficos salvos em: {self.diretorio_graficos}")
    
    def gerar_graficos_comparativos(self, df_resultados):
        """Gera gráficos mais informativos para comparação dos algoritmos."""
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
        
        # Definir estilo visual consistente
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams['figure.figsize'] = (14, 10)
        plt.rcParams['font.size'] = 12
        
        # Mapeamento de nomes de algoritmos para exibição mais amigável
        mapa_nomes = {
            'run_dynamic_programming': 'Programação Dinâmica',
            'run_backtracking': 'Backtracking',
            'run_branch_and_bound': 'Branch and Bound'
        }
        
        # Cores consistentes para os algoritmos
        cores_algoritmos = {
            'run_dynamic_programming': '#1f77b4',  # azul
            'run_backtracking': '#ff7f0e',         # laranja
            'run_branch_and_bound': '#2ca02c'      # verde
        }
        
        # Verificar dados
        if df_resultados is None or df_resultados.empty:
            print("Sem dados para gerar gráficos comparativos.")
            return
        
        # Criar cópia local para manipulação
        df = df_resultados.copy()
        
        # Garantir que os tipos estão corretos
        df['tempo'] = pd.to_numeric(df['tempo'], errors='coerce')
        
        # Para cada parâmetro variável (n e W)
        for param in ['n', 'W']:
            if param not in df.columns:
                continue
                
            df[param] = pd.to_numeric(df[param], errors='coerce')
            
            # 1. Gráfico de tempo médio por parâmetro com barras de erro
            plt.figure(figsize=(14, 10))
            
            # Agrupar por parâmetro e algoritmo, calcular média e desvio padrão
            agrupado = df.groupby([param, 'algoritmo']).agg({
                'tempo': ['mean', 'std', 'count']
            }).reset_index()
            
            agrupado.columns = [param, 'algoritmo', 'tempo_medio', 'tempo_std', 'contagem']
            
            # Plotar cada algoritmo
            for alg in df['algoritmo'].unique():
                dados_alg = agrupado[agrupado['algoritmo'] == alg]
                if dados_alg.empty:
                    continue
                    
                # Calcular o erro padrão (para barras de erro)
                dados_alg = dados_alg.copy()
                dados_alg.loc[:, 'erro'] = dados_alg['tempo_std'] / np.sqrt(dados_alg['contagem'])
                
                plt.errorbar(
                    dados_alg[param],
                    dados_alg['tempo_medio'],
                    yerr=dados_alg['erro'],
                    fmt='o-',
                    linewidth=3,
                    capsize=6,
                    markersize=10,
                    label=mapa_nomes.get(alg, alg),
                    color=cores_algoritmos.get(alg)
                )
                
                # Adicionar rótulos para pontos-chave
                for i, row in dados_alg.iterrows():
                    if i % 2 == 0 or i == len(dados_alg) - 1:  # Rotular pontos alternados e o último
                        plt.text(
                            row[param] * 1.02,
                            row['tempo_medio'] * 1.05,
                            f"{row['tempo_medio']:.4f}s",
                            fontsize=10,
                            fontweight='bold',
                            ha='left'
                        )
            
            # Configurações do gráfico
            plt.title(f'Comparação de Desempenho - Variando {param.upper()}', fontsize=18, fontweight='bold')
            plt.xlabel(f'{"Número de Itens (n)" if param == "n" else "Capacidade da Mochila (W)"}', fontsize=14)
            plt.ylabel('Tempo de Execução (segundos)', fontsize=14)
            plt.grid(True, alpha=0.3, linestyle='--')
            plt.legend(fontsize=12, title='Algoritmos', title_fontsize=14)
            
            # Ajustar escala para melhor visualização
            if len(agrupado[param].unique()) > 1:
                plt.xscale('log', base=2)
            plt.yscale('log')
            
            plt.tight_layout()
            plt.savefig(os.path.join(self.diretorio_graficos, f'comparativo_tempo_{param}.png'), dpi=300)
            plt.close()
            
            # 2. Gráfico de boxplot para comparação da distribuição de tempos
            plt.figure(figsize=(14, 8))
            sns.boxplot(
                x=param, 
                y='tempo', 
                hue='algoritmo',
                data=df, 
                palette=cores_algoritmos
            )
            plt.title(f'Distribuição dos Tempos por {param.upper()}', fontsize=16, fontweight='bold')
            plt.xlabel(f'{"Número de Itens (n)" if param == "n" else "Capacidade da Mochila (W)"}', fontsize=14)
            plt.ylabel('Tempo (segundos)', fontsize=14)
            plt.yscale('log')
            plt.legend(title='Algoritmo', fontsize=12)
            plt.tight_layout()
            plt.savefig(os.path.join(self.diretorio_graficos, f'boxplot_{param}.png'), dpi=300)
            plt.close()
            
            # 3. Gráfico de linhas para comparar crescimento de tempo
            plt.figure(figsize=(14, 8))
            sns.lineplot(
                x=param, 
                y='tempo', 
                hue='algoritmo',
                data=df, 
                palette=cores_algoritmos,
                err_style='band',
                errorbar=('ci', 95)
            )
            plt.title(f'Crescimento do Tempo de Execução com {param.upper()}', fontsize=16, fontweight='bold')
            plt.xlabel(f'{"Número de Itens (n)" if param == "n" else "Capacidade da Mochila (W)"}', fontsize=14)
            plt.ylabel('Tempo (segundos)', fontsize=14)
            plt.yscale('log')
            if len(df[param].unique()) > 1:
                plt.xscale('log', base=2)
            plt.grid(True, alpha=0.3, linestyle='--')
            plt.legend(title='Algoritmo', fontsize=12)
            plt.tight_layout()
            plt.savefig(os.path.join(self.diretorio_graficos, f'crescimento_{param}.png'), dpi=300)
            plt.close()
        
        # 4. Gráfico de barras para comparação global entre algoritmos
        plt.figure(figsize=(12, 8))
        comparacao_global = df.groupby('algoritmo')['tempo'].agg(['mean', 'std', 'count']).reset_index()
        comparacao_global['erro'] = comparacao_global['std'] / np.sqrt(comparacao_global['count'])
        
        # Ordenar algoritmos pela média de tempo (do mais rápido ao mais lento)
        comparacao_global = comparacao_global.sort_values('mean')
        
        # Converter nomes de algoritmos
        comparacao_global['nome_amigavel'] = comparacao_global['algoritmo'].map(mapa_nomes)
        
        # Plot de barras com erro
        plt.bar(
            comparacao_global['nome_amigavel'],
            comparacao_global['mean'],
            yerr=comparacao_global['erro'],
            capsize=8,
            color=[cores_algoritmos.get(alg) for alg in comparacao_global['algoritmo']],
            alpha=0.8
        )
        
        # Adicionar valores nas barras
        for i, row in comparacao_global.iterrows():
            plt.text(
                i, 
                row['mean'] * 0.5, 
                f"{row['mean']:.4f}s",
                ha='center',
                color='white',
                fontweight='bold',
                fontsize=12
            )
        
        plt.title('Comparação Global de Desempenho', fontsize=16, fontweight='bold')
        plt.ylabel('Tempo Médio (segundos)', fontsize=14)
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.savefig(os.path.join(self.diretorio_graficos, 'comparacao_global.png'), dpi=300)
        plt.close()
        
        # 5. Gráfico de distribuição dos tempos por algoritmo
        plt.figure(figsize=(14, 8))
        sns.violinplot(
            x='algoritmo', 
            y='tempo', 
            hue='algoritmo',
            data=df,
            palette=cores_algoritmos,
            inner='quartile',
            legend=False
        )
        
        # Converter nomes no eixo X
        plt.xticks(
            range(len(df['algoritmo'].unique())),
            [mapa_nomes.get(alg, alg) for alg in df['algoritmo'].unique()]
        )
        
        plt.title('Distribuição dos Tempos de Execução por Algoritmo', fontsize=16, fontweight='bold')
        plt.xlabel('Algoritmo', fontsize=14)
        plt.ylabel('Tempo (segundos)', fontsize=14)
        plt.yscale('log')
        plt.tight_layout()
        plt.savefig(os.path.join(self.diretorio_graficos, 'distribuicao_tempos.png'), dpi=300)
        plt.close()
        
        print(f"Gráficos comparativos gerados com sucesso em: {self.diretorio_graficos}")
    
    def executar_gerador_instancias(self, num_instancias, n, W, force_regenerate=False):
        """
        Executa o gerador de instâncias ou usa instâncias existentes.
        
        Args:
            num_instancias: Número de instâncias a serem geradas
            n: Número de itens
            W: Capacidade da mochila
            force_regenerate: Se True, força a regeneração mesmo se as instâncias já existirem
            
        Returns:
            bool: True se as instâncias estão disponíveis, False caso contrário
        """
        import os
        import subprocess
        
        # Diretório onde as instâncias serão/estão armazenadas
        diretorio_saida = os.path.join(self.diretorio_instancias, f"instancias_n{n}_W{W}")
        os.makedirs(diretorio_saida, exist_ok=True)
        
        # Verifica se já existem instâncias suficientes
        arquivos_existentes = [f for f in os.listdir(diretorio_saida) 
                             if f.startswith("instancia_") and f.endswith(".txt")]
        
        # Se já temos instâncias suficientes e não estamos forçando a regeneração, use as existentes
        if len(arquivos_existentes) >= num_instancias and not force_regenerate:
            print(f"Usando {num_instancias} instâncias existentes em {diretorio_saida}")
            return True
            
        # Configurar a variável de ambiente para o gerador saber onde salvar
        env = os.environ.copy()
        env["INSTANCES_DIR"] = self.diretorio_instancias
        
        # Executável do gerador de instâncias
        executavel = os.path.join(self.diretorio_binarios, "generate_instances")
        if self.eh_windows and not executavel.endswith('.exe'):
            executavel += '.exe'
        
        if not os.path.exists(executavel):
            print(f"ERRO: Gerador de instâncias '{executavel}' não encontrado!")
            return False
        
        try:
            print(f"Gerando {num_instancias} instâncias com n={n}, W={W}...")
            resultado = subprocess.run(
                [executavel, str(num_instancias), str(n), str(W)],
                capture_output=True,
                text=True,
                check=True,
                env=env
            )
            
            # Verificar se as instâncias foram geradas
            arquivos_gerados = [f for f in os.listdir(diretorio_saida) 
                              if f.startswith("instancia_") and f.endswith(".txt")]
            
            if len(arquivos_gerados) >= num_instancias:
                print(f"Geradas com sucesso {len(arquivos_gerados)} instâncias em {diretorio_saida}")
                return True
            else:
                print(f"AVISO: Esperava {num_instancias} instâncias, mas foram geradas apenas {len(arquivos_gerados)}")
                return len(arquivos_gerados) > 0
                
        except subprocess.CalledProcessError as e:
            print(f"ERRO ao executar gerador de instâncias: {e}")
            if e.stdout: print(f"Saída: {e.stdout}")
            if e.stderr: print(f"Erro: {e.stderr}")
            return False
        except Exception as e:
            print(f"ERRO inesperado ao gerar instâncias: {e}")
            return False
    
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
        
        # Check if the DataFrame is empty
        if df_resultados.empty:
            print("Warning: Empty DataFrame passed to gerar_resumo_resultados. Skipping summary generation.")
            return
        
        # Check if required columns exist
        required_columns = ['algoritmo', 'tempo']
        missing_columns = [col for col in required_columns if col not in df_resultados.columns]
        if missing_columns:
            print(f"Warning: DataFrame is missing required columns: {missing_columns}. Available columns: {df_resultados.columns.tolist()}")
            print("Skipping summary generation.")
            return
        
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
        
        print("Gerando visualizações avançadas...")
        
        # Leitura segura dos arquivos de resultados
        try:
            # Verificar existência dos arquivos
            arquivo_resultados_n = os.path.join(self.diretorio_resultados, 'resultados_variando_n.csv')
            arquivo_resultados_W = os.path.join(self.diretorio_resultados, 'resultados_variando_W.csv')
            
            df_n = None
            df_W = None
            
            # Carregar arquivo de resultados para n
            if os.path.exists(arquivo_resultados_n) and os.path.getsize(arquivo_resultados_n) > 0:
                try:
                    df_n = pd.read_csv(arquivo_resultados_n)
                    if df_n.empty or 'algoritmo' not in df_n.columns:
                        print(f"Arquivo {arquivo_resultados_n} existe mas não contém dados válidos.")
                        df_n = None
                except Exception as e:
                    print(f"Erro ao ler {arquivo_resultados_n}: {e}")
                    df_n = None
            
            # Carregar arquivo de resultados para W
            if os.path.exists(arquivo_resultados_W) and os.path.getsize(arquivo_resultados_W) > 0:
                try:
                    df_W = pd.read_csv(arquivo_resultados_W)
                    if df_W.empty or 'algoritmo' not in df_W.columns:
                        print(f"Arquivo {arquivo_resultados_W} existe mas não contém dados válidos.")
                        df_W = None
                except Exception as e:
                    print(f"Erro ao ler {arquivo_resultados_W}: {e}")
                    df_W = None
            
            # Verificar se há dados para processar
            if df_n is None and df_W is None:
                print("Nenhum dado válido para gerar visualizações avançadas.")
                return
            
            # Combinar os dados disponíveis
            df_combined = pd.concat([df for df in [df_n, df_W] if df is not None], ignore_index=True)
            
            if df_combined.empty or 'algoritmo' not in df_combined.columns:
                print("Dados combinados insuficientes para gerar visualizações.")
                return
            
            # Resto do código para gerar visualizações com df_combined
            # ...
            
            # Por exemplo, gerar heatmap se houver dados suficientes:
            if 'algoritmo' in df_combined.columns and 'n' in df_combined.columns and 'tempo' in df_combined.columns:
                pivot_data = pd.pivot_table(
                    df_combined,
                    index="algoritmo",
                    columns="n",
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
            else:
                print("Dados insuficientes para gerar o heatmap comparativo.")
                
        except Exception as e:
            print(f"Erro ao gerar visualizações avançadas: {e}")

def main():
    """Função principal para coordenar a execução dos experimentos com algoritmos do Problema da Mochila."""
    import os
    import pandas as pd
    import time
    import concurrent.futures
    
    print("\n" + "="*80)
    print("EXPERIMENTOS COM ALGORITMOS DO PROBLEMA DA MOCHILA")
    print("="*80)
    print("\nIniciando execução de experimentos e análises...")
    
    # Registrar tempo de início para medir o tempo total de execução
    tempo_inicio = time.time()
    
    # Inicializar executor de experimentos
    executor = ExecutorExperimentos()
    
    # Inicializar arquivos CSV com cabeçalhos corretos
    executor.inicializar_arquivos_csv()
    
    # Definir configurações avançadas dos experimentos
    config = {
        'valores_n': [10, 20, 30, 40, 50, 60],           # Valores de n a serem testados
        'valores_W': [20, 40, 60, 80, 100, 120],         # Valores de W a serem testados
        'num_instancias': 5,                             # Número de instâncias por configuração
        'timeout_algoritmo': 120,                        # Timeout em segundos para cada execução
        'W_fixo': 50,                                    # W fixo para experimentos variando n
        'n_fixo': 30                                     # n fixo para experimentos variando W
    }
    
    print(f"\nConfigurações dos experimentos:")
    print(f"- Valores de n: {config['valores_n']}")
    print(f"- Valores de W: {config['valores_W']}")
    print(f"- Instâncias por configuração: {config['num_instancias']}")
    print(f"- Timeout por algoritmo: {config['timeout_algoritmo']} segundos")
    
    # Verificar diretórios de trabalho
    print(f"\nDiretórios utilizados:")
    print(f"- Binários: {executor.diretorio_binarios}")
    print(f"- Instâncias: {executor.diretorio_instancias}")
    print(f"- Resultados: {executor.diretorio_resultados}")
    print(f"- Gráficos: {executor.diretorio_graficos}")
    
    # Verifica se existem resultados salvos
    arquivo_resultados_n = os.path.join(executor.diretorio_resultados, 'resultados_variando_n.csv')
    arquivo_resultados_W = os.path.join(executor.diretorio_resultados, 'resultados_variando_W.csv')
    
    df_resultados_n = None
    df_resultados_W = None
    
    # Função auxiliar para carregar ou gerar resultados
    def carregar_ou_gerar(arquivo, funcao_executar, *args):
        if os.path.exists(arquivo) and os.path.getsize(arquivo) > 0:
            print(f"Carregando resultados existentes de {arquivo}")
            try:
                df = pd.read_csv(arquivo)
                if df.empty or 'algoritmo' not in df.columns:
                    print(f"Arquivo {arquivo} existe mas tem dados inválidos. Executando novos experimentos.")
                    return funcao_executar(*args)
                else:
                    print(f"Dados carregados com sucesso: {len(df)} registros.")
                    return df
            except Exception as e:
                print(f"Erro ao carregar {arquivo}: {e}")
                print("Executando novos experimentos...")
                return funcao_executar(*args)
        else:
            print(f"Arquivo {arquivo} não encontrado. Executando experimentos...")
            return funcao_executar(*args)
    
    # Execução paralela dos experimentos, se possível
    print("\n" + "-"*80)
    print("FASE 1: EXECUÇÃO DOS EXPERIMENTOS")
    print("-"*80)
    
    try:
        # Experimentos variando n
        print("\nExecutando experimentos variando n...")
        df_resultados_n = carregar_ou_gerar(
            arquivo_resultados_n, 
            executor.executar_variando_n,
            config['valores_n'],
            config['W_fixo'],
            config['num_instancias']
        )
        
        # Experimentos variando W
        print("\nExecutando experimentos variando W...")
        df_resultados_W = carregar_ou_gerar(
            arquivo_resultados_W, 
            executor.executar_variando_W,
            config['valores_W'],
            config['n_fixo'],
            config['num_instancias']
        )
        
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário. Salvando resultados parciais...")
    except Exception as e:
        print(f"\nErro durante execução dos experimentos: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Análise de resultados (se existirem dados)
    print("\n" + "-"*80)
    print("FASE 2: ANÁLISE DOS RESULTADOS")
    print("-"*80)
    
    dados_disponiveis = []
    if df_resultados_n is not None and not df_resultados_n.empty:
        print("\nAnalisando resultados dos experimentos variando n...")
        executor.analisar_resultados(df_resultados_n, parametro_variavel='n')
        dados_disponiveis.append("n")
    
    if df_resultados_W is not None and not df_resultados_W.empty:
        print("\nAnalisando resultados dos experimentos variando W...")
        executor.analisar_resultados(df_resultados_W, parametro_variavel='W')
        dados_disponiveis.append("W")
    
    # Análise estatística e visualizações avançadas
    if dados_disponiveis:
        print("\n" + "-"*80)
        print("FASE 3: ANÁLISE ESTATÍSTICA E VISUALIZAÇÕES AVANÇADAS")
        print("-"*80)
        
        if "n" in dados_disponiveis:
            print("\nRealizando testes estatísticos para experimentos variando n...")
            executor.realizar_teste_t_pareado(df_resultados_n)
            executor.gerar_resumo_resultados(df_resultados_n)
            executor.gerar_graficos_comparativos(df_resultados_n)
        
        if "W" in dados_disponiveis:
            print("\nRealizando testes estatísticos para experimentos variando W...")
            executor.realizar_teste_t_pareado(df_resultados_W)
            executor.gerar_resumo_resultados(df_resultados_W)
            executor.gerar_graficos_comparativos(df_resultados_W)
        
        print("\nGerando visualizações avançadas combinadas...")
        executor.gerar_visualizacoes_avancadas()
    else:
        print("\nNenhum dado disponível para análise estatística.")
    
    # Finalização
    tempo_total = time.time() - tempo_inicio
    minutos = int(tempo_total // 60)
    segundos = int(tempo_total % 60)
    
    print("\n" + "="*80)
    print("EXPERIMENTOS CONCLUÍDOS")
    print("="*80)
    print(f"Tempo total de execução: {minutos} minutos e {segundos} segundos")
    print(f"Gráficos salvos em: {executor.diretorio_graficos}")
    print(f"Resultados CSV salvos em: {executor.diretorio_resultados}")
    print(f"Relatórios detalhados em: {os.path.join(executor.diretorio_resultados, 'relatorios')}")
    
    if dados_disponiveis:
        print("\nResultados disponíveis para análise:")
        if "n" in dados_disponiveis:
            print(f"- Experimentos variando n: {len(df_resultados_n)} registros")
        if "W" in dados_disponiveis:
            print(f"- Experimentos variando W: {len(df_resultados_W)} registros")
    
    print("\nPara visualizações mais avançadas, execute o script:")
    print(f"python {os.path.join('scripts', 'generate_visualizations.py')}")
    
    # Salvar uma cópia dos resultados em formato Excel para facilitar a análise
    try:
        import openpyxl
        excel_file = os.path.join(executor.diretorio_resultados, 'resultados_combinados.xlsx')
        with pd.ExcelWriter(excel_file) as writer:
            if "n" in dados_disponiveis:
                df_resultados_n.to_excel(writer, sheet_name='Variando_n', index=False)
            if "W" in dados_disponiveis:
                df_resultados_W.to_excel(writer, sheet_name='Variando_W', index=False)
        print(f"\nResultados também foram salvos em formato Excel: {excel_file}")
    except ImportError:
        print("\nResultados disponíveis apenas em CSV. Para salvar em Excel, execute:")
        print("pip install openpyxl")
    except Exception as e:
        print(f"\nErro ao salvar resultados em Excel: {e}")
    
    print("\nFim da execução.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.")
    except Exception as e:
        print(f"\nErro fatal: {e}")
        import traceback
        traceback.print_exc()