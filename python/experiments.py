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

# Adiciona o diretório raiz ao path para importações relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from config import BINARY_DIR, OUTPUT_DIR, INSTANCES_DIR, RESULTS_DIR, GRAPHS_DIR
    print(f"Diretórios carregados: {BINARY_DIR}, {OUTPUT_DIR}, {INSTANCES_DIR}, {RESULTS_DIR}, {GRAPHS_DIR}")
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
    print(f"Usando diretórios padrão: {BINARY_DIR}, {OUTPUT_DIR}, {INSTANCES_DIR}, {RESULTS_DIR}, {GRAPHS_DIR}")

class TimeoutException(Exception):
    """Exceção lançada quando um algoritmo excede o tempo limite de execução."""
    pass

def timeout_handler(signum, frame):
    """Manipulador de sinal para timeout."""
    raise TimeoutException("Tempo limite excedido")

class ExecutorExperimentos:
    """Classe para execução e análise de experimentos com algoritmos do Problema da Mochila."""
    
    def __init__(self):
        """Inicializa o executor de experimentos com as configurações necessárias."""
        # Dicionário para armazenar resultados dos algoritmos
        self.resultados = {
            'run_dynamic_programming': [],  # Programação Dinâmica
            'run_backtracking': [],         # Backtracking
            'run_branch_and_bound': []      # Branch and Bound
        }
        
        # Verifica o sistema operacional
        self.eh_windows = os.name == 'nt'
        
        # Carrega caminhos da configuração
        self.diretorio_binarios = BINARY_DIR if BINARY_DIR else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "bin"))
        self.diretorio_saida = OUTPUT_DIR if OUTPUT_DIR else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
        self.diretorio_instancias = INSTANCES_DIR if INSTANCES_DIR else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "instances"))
        self.diretorio_resultados = RESULTS_DIR if RESULTS_DIR else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
        self.diretorio_graficos = GRAPHS_DIR if GRAPHS_DIR else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "graphs"))
        
        print(f"Usando diretórios: {self.diretorio_binarios}, {self.diretorio_saida}, {self.diretorio_instancias}, {self.diretorio_resultados}, {self.diretorio_graficos}")
        
        # Cria diretórios necessários se não existirem
        for diretorio in [self.diretorio_saida, self.diretorio_instancias, self.diretorio_resultados, self.diretorio_graficos]:
            if diretorio:  # Só cria o diretório se o caminho não for vazio
                os.makedirs(diretorio, exist_ok=True)
    
    def executar_algoritmo(self, algoritmo, arquivo_instancia, timeout=60):
        """
        Executa um algoritmo em uma instância específica e mede seu desempenho.
        
        Args:
            algoritmo (str): Nome do executável do algoritmo.
            arquivo_instancia (str): Caminho para o arquivo de instância.
            timeout (int): Tempo limite em segundos para execução.
            
        Returns:
            tuple: (tempo_execucao, valor_maximo) ou (None, None) em caso de erro.
        """
        # Determina o caminho do executável conforme o sistema operacional
        if self.eh_windows:
            executavel = os.path.join(self.diretorio_binarios, f"{algoritmo}.exe")
        else:
            executavel = os.path.join(self.diretorio_binarios, algoritmo)
        
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
                resultado = subprocess.run([executavel, arquivo_instancia], 
                                      capture_output=True, text=True, timeout=timeout)
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
            for linha in linhas_saida:
                if "Valor máximo:" in linha:
                    try:
                        valor_maximo = int(linha.split(":")[-1].strip())
                        break
                    except ValueError:
                        print(f"  - {algoritmo} formato de saída inválido")
                        return None, None
            
            if valor_maximo is None:
                print(f"  - {algoritmo} não retornou um valor máximo")
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
    
    def executar_variando_n(self, valores_n=[100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600], W=100, num_instancias=20):
        """
        Executa experimentos variando o número de itens (n).
        
        Args:
            valores_n (list): Lista de valores de n a serem testados.
            W (int): Capacidade da mochila fixa para todos os testes.
            num_instancias (int): Número de instâncias aleatórias a gerar para cada configuração.
            
        Returns:
            DataFrame: DataFrame pandas com os resultados.
        """
        # Inicializa lista para armazenar resultados
        resultados = []
        
        for n in valores_n:
            print(f"\nExecutando testes com n={n}, W={W}")
            
            # Cria diretório para instâncias dessa configuração
            nome_diretorio = os.path.join(self.diretorio_instancias, f"instancias_n{n}_W{W}")
            if not os.path.exists(nome_diretorio):
                # Gera instâncias novas
                print(f"Gerando {num_instancias} instâncias com n={n}, W={W}")
                self.executar_gerador_instancias(num_instancias, n, W)
        
            # Executa cada instância
            for instancia in range(1, num_instancias + 1):
                arquivo_instancia = os.path.join(self.diretorio_instancias, 
                                               f"instancias_n{n}_W{W}/instancia_{instancia}.txt")
                
                if not os.path.exists(arquivo_instancia):
                    print(f"Arquivo {arquivo_instancia} não encontrado, pulando...")
                    continue
                
                # Testa cada algoritmo
                for algoritmo in self.resultados.keys():
                    # Pula backtracking para n grande para evitar timeout
                    if algoritmo == 'run_backtracking' and n > 100:
                        print(f"  Pulando {algoritmo} para n={n} (muito grande)")
                        resultados.append({
                            'n': n,
                            'W': W,
                            'algoritmo': algoritmo,
                            'instancia': instancia,
                            'tempo': None,
                            'valor': None
                        })
                        continue
                    
                    # Executa o algoritmo e registra os resultados
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
    
    def executar_variando_W(self, valores_W=[100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600], n=400, num_instancias=20):
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
        """
        Realiza teste t pareado com 95% de confiança para comparar algoritmos.
        
        Args:
            df_resultados (DataFrame): DataFrame com resultados dos experimentos.
        """
        algoritmos = sorted(df_resultados['algoritmo'].unique())
        
        # Para cada par de algoritmos
        for i in range(len(algoritmos)):
            for j in range(i+1, len(algoritmos)):
                alg1 = algoritmos[i]
                alg2 = algoritmos[j]
                
                # Filtra resultados para instâncias que têm dados para ambos algoritmos
                instancias_alg1 = set(df_resultados[df_resultados['algoritmo'] == alg1]['instancia'])
                instancias_alg2 = set(df_resultados[df_resultados['algoritmo'] == alg2]['instancia'])
                instancias_comuns = instancias_alg1.intersection(instancias_alg2)
                
                tempos_alg1 = []
                tempos_alg2 = []
                
                for inst in instancias_comuns:
                    tempo1 = df_resultados[(df_resultados['algoritmo'] == alg1) & 
                                        (df_resultados['instancia'] == inst)]['tempo'].values[0]
                    tempo2 = df_resultados[(df_resultados['algoritmo'] == alg2) & 
                                        (df_resultados['instancia'] == inst)]['tempo'].values[0]
                    
                    if not pd.isna(tempo1) and not pd.isna(tempo2):
                        tempos_alg1.append(tempo1)
                        tempos_alg2.append(tempo2)
                
                if len(tempos_alg1) > 1:  # Necessário pelo menos 2 amostras para o teste t
                    t_stat, p_valor = stats.ttest_rel(tempos_alg1, tempos_alg2)
                    
                    print(f"\nComparação entre {alg1} e {alg2}:")
                    print(f"  Média {alg1}: {np.mean(tempos_alg1):.6f} s")
                    print(f"  Média {alg2}: {np.mean(tempos_alg2):.6f} s")
                    print(f"  Estatística t: {t_stat:.4f}")
                    print(f"  p-valor: {p_valor:.6f}")
                    
                    if p_valor < 0.05:  # 95% de confiança
                        melhor = alg1 if np.mean(tempos_alg1) < np.mean(tempos_alg2) else alg2
                        print(f"  Resultado: {melhor} é estatisticamente melhor (95% de confiança)")
                    else:
                        print(f"  Resultado: Empate estatístico (95% de confiança)")

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
    
    print("\nExperimentos concluídos e resultados analisados!")
    print(f"Gráficos salvos em: {executor.diretorio_graficos}")
    print(f"Resultados CSV salvos em: {executor.diretorio_resultados}")


if __name__ == "__main__":
    main()