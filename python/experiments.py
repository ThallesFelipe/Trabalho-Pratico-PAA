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
        Executa o gerador de instâncias e verifica se os arquivos foram criados corretamente.
        
        Args:
            num_instancias: Número de instâncias a serem geradas
            n: Número de itens
            W: Capacidade da mochila
        
        Returns:
            bool: True se as instâncias foram geradas com sucesso, False caso contrário
        """
        import subprocess
        import os
        
        # Verifica se o diretório de saída existe
        diretorio_saida = os.path.join(self.diretorio_instancias, f"instancias_n{n}_W{W}")
        os.makedirs(diretorio_saida, exist_ok=True)
        
        # Comando para executar o gerador de instâncias
        comando = [os.path.join(self.diretorio_binarios, "generate_instances"), 
                   str(num_instancias), str(n), str(W)]
        
        try:
            print(f"Executando: {' '.join(comando)}")
            resultado = subprocess.run(comando, 
                                      capture_output=True, 
                                      text=True, 
                                      check=True)
            
            # Verifica se os arquivos foram criados
            arquivos_criados = [f for f in os.listdir(diretorio_saida) 
                               if f.startswith("instancia_") and f.endswith(".txt")]
            
            if len(arquivos_criados) >= num_instancias:
                print(f"Geradas {len(arquivos_criados)} instâncias em {diretorio_saida}")
                return True
            else:
                print(f"Aviso: Foram geradas apenas {len(arquivos_criados)} de {num_instancias} instâncias")
                return len(arquivos_criados) > 0
                
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar gerador de instâncias: {e}")
            print(f"Saída: {e.stdout}")
            print(f"Erro: {e.stderr}")
            return False
        except Exception as e:
            print(f"Erro inesperado ao gerar instâncias: {e}")
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
    """Função principal para coordenar a execução dos experimentos."""
    import os
    import pandas as pd
    
    executor = ExecutorExperimentos()
    
    # Inicializar arquivos CSV antes de começar
    executor.inicializar_arquivos_csv()
    
    # Verifica se existem resultados salvos
    arquivo_resultados_n = os.path.join(executor.diretorio_resultados, 'resultados_variando_n.csv')
    arquivo_resultados_W = os.path.join(executor.diretorio_resultados, 'resultados_variando_W.csv')
    
    df_resultados_n = None
    df_resultados_W = None
    
    # Experimentos variando n
    try:
        if os.path.exists(arquivo_resultados_n) and os.path.getsize(arquivo_resultados_n) > 0:
            print(f"Carregando resultados existentes de {arquivo_resultados_n}")
            df_resultados_n = pd.read_csv(arquivo_resultados_n)
            
            # Verify data integrity
            if df_resultados_n.empty or 'algoritmo' not in df_resultados_n.columns:
                print(f"Arquivo {arquivo_resultados_n} existe mas tem dados inválidos. Executando novos experimentos.")
                df_resultados_n = executor.executar_variando_n()
            else:
                print(f"Dados carregados com sucesso: {len(df_resultados_n)} registros.")
        else:
            print("Executando experimentos variando n")
            df_resultados_n = executor.executar_variando_n()
    except Exception as e:
        print(f"Erro ao processar experimentos variando n: {e}")
        print("Continuando com os outros experimentos...")
    
    # Experimentos variando W
    try:
        if os.path.exists(arquivo_resultados_W) and os.path.getsize(arquivo_resultados_W) > 0:
            print(f"Carregando resultados existentes de {arquivo_resultados_W}")
            df_resultados_W = pd.read_csv(arquivo_resultados_W)
            
            # Verify data integrity
            if df_resultados_W.empty or 'algoritmo' not in df_resultados_W.columns:
                print(f"Arquivo {arquivo_resultados_W} existe mas tem dados inválidos. Executando novos experimentos.")
                df_resultados_W = executor.executar_variando_W()
            else:
                print(f"Dados carregados com sucesso: {len(df_resultados_W)} registros.")
        else:
            print("Executando experimentos variando W")
            df_resultados_W = executor.executar_variando_W()
    except Exception as e:
        print(f"Erro ao processar experimentos variando W: {e}")
    
    # Análise de resultados combinados (se ambos existirem)
    if df_resultados_n is not None and df_resultados_W is not None:
        # Gere análise estatística combinada
        print("\n===== Análise Estatística: Comparação entre Algoritmos =====\n")
        
        print("Resultados para experimentos variando n:")
        executor.realizar_teste_t_pareado(df_resultados_n)
        
        print("\nResultados para experimentos variando W:")
        executor.realizar_teste_t_pareado(df_resultados_W)
        
        # Gere resumos dos resultados
        if not df_resultados_n.empty:
            executor.gerar_resumo_resultados(df_resultados_n)
        
        if not df_resultados_W.empty and 'algoritmo' in df_resultados_W.columns:
            executor.gerar_resumo_resultados(df_resultados_W)
        
        # Gere visualizações avançadas
        print("Gerando visualizações avançadas...")
        executor.gerar_visualizacoes_avancadas()
    
    print("\nExperimentos concluídos e resultados analisados!")
    print(f"Gráficos salvos em: {executor.diretorio_graficos}")
    print(f"Resultados CSV salvos em: {executor.diretorio_resultados}")


if __name__ == "__main__":
    main()