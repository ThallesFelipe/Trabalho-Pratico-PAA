# Análise Experimental de Algoritmos para o Problema da Mochila

![Linguagem](https://img.shields.io/badge/C%2B%2B-17-blue.svg)
![Linguagem](https://img.shields.io/badge/Python-3.x-blue.svg)
![Build](https://img.shields.io/badge/Build-CMake-green.svg)

Este repositório contém a implementação e a análise de desempenho de três algoritmos clássicos para resolver o **Problema da Mochila 0/1**. O projeto foi desenvolvido como parte da disciplina de Projeto e Análise de Algoritmos, com o objetivo de comparar experimentalmente a eficiência das seguintes abordagens:

1. **Programação Dinâmica**
2. **Backtracking**
3. **Branch and Bound**

O framework de experimentação é automatizado com scripts Python, que gerenciam a geração de instâncias, a execução dos algoritmos (compilados em C++ para performance) e a coleta e análise estatística dos resultados.

## Autor

* Thalles Felipe Rodrigues de Almeidad Santos - 21.2.4130

## Tecnologias Utilizadas

* **C++17:** Para a implementação de alta performance dos algoritmos.
* **CMake:** Para a automação do processo de compilação do código C++.
* **Python:** Para orquestrar os experimentos, analisar os dados e gerar visualizações.
* **Bibliotecas Python:**
  * `pandas` para manipulação de dados.
  * `numpy` para cálculos numéricos.
  * `matplotlib` e `seaborn` para a geração de gráficos.
  * `scipy` para a realização de testes estatísticos (Teste T).
  * `tabulate` para a criação de tabelas formatadas.

## Estrutura do Projeto

```text
.
├── CMakeLists.txt              # Arquivo de configuração do build com CMake
├── run_analysis.py             # Script principal para executar toda a análise
├── output/                     # Diretório para todos os artefatos gerados
│   ├── instances/              # Instâncias de teste geradas
│   ├── results/                # Resultados dos experimentos em CSV e relatórios
│   └── graphs/                 # Gráficos comparativos de desempenho
├── src/                        # Código-fonte em C++
│   ├── algorithms/             # Implementação dos algoritmos da mochila
│   └── main/                   # Executáveis para cada algoritmo
├── include/                    # Arquivos de cabeçalho C++
│   └── knapsack/
├── python/                     # Módulos Python
│   └── experiments.py          # Lógica principal para execução e análise dos experimentos
└── scripts/                    # Scripts auxiliares
```

## Algoritmos Implementados

### 1. Programação Dinâmica

A solução baseada em programação dinâmica ([`src/algorithms/dynamic_programming.cpp`](src/algorithms/dynamic_programming.cpp)) utiliza uma tabela (matriz) para armazenar os valores máximos para todas as combinações de subconjuntos de itens e capacidades parciais. É uma abordagem *bottom-up* que garante a otimalidade com complexidade de tempo pseudo-polinomial de **O(n·W)**.

### 2. Backtracking

O algoritmo de backtracking ([`src/algorithms/backtracking.cpp`](src/algorithms/backtracking.cpp)) explora recursivamente o espaço de soluções. Em cada passo, ele decide se inclui ou não o item atual na mochila. A busca é podada se a adição de um item excede a capacidade da mochila. A complexidade de pior caso é **O(2^n)**.

### 3. Branch and Bound

Esta é uma otimização do backtracking ([`src/algorithms/branch_and_bound.cpp`](src/algorithms/branch_and_bound.cpp)). Além da poda por capacidade, ele calcula um *limite superior* (upper bound) para o valor máximo que pode ser obtido a partir de um nó na árvore de busca. Se o limite superior de um nó não for melhor que a melhor solução encontrada até o momento, o ramo inteiro é podado. A implementação utiliza uma fila de prioridade para explorar os nós mais promissores primeiro, melhorando a eficiência da poda. A complexidade de pior caso também é **O(2^n)**, mas o desempenho em casos médios é significativamente melhor que o backtracking puro.

## Pré-requisitos

Antes de começar, certifique-se de que você tem os seguintes softwares instalados:

* Um compilador C++ moderno (GCC, Clang, MSVC).
* CMake (versão 3.10 ou superior).
* Python 3.8 ou superior.

Instale as dependências Python necessárias executando:

```sh
pip install pandas numpy matplotlib seaborn scipy tabulate
```

## Como Compilar

O projeto utiliza CMake para gerenciar a compilação. Siga os passos abaixo para compilar os executáveis dos algoritmos:

1. Crie um diretório de build:

   ```sh
   mkdir build
   ```

2. Navegue até o diretório de build e execute o CMake:

   ```sh
   cd build
   cmake ..
   ```

3. Compile o projeto:

   ```sh
   cmake --build .
   ```

   Os executáveis serão gerados no diretório `build/bin/`.

## Como Executar os Experimentos

O processo completo de análise (geração de instâncias, execução dos algoritmos, análise de dados e geração de gráficos) é gerenciado pelo script principal [`run_analysis.py`](run_analysis.py).

Para executar, simplesmente rode o seguinte comando na raiz do projeto:

```sh
python run_analysis.py
```

As configurações dos experimentos, como os valores de `n` (número de itens) e `W` (capacidade da mochila) a serem testados, podem ser ajustadas diretamente no dicionário `config` dentro do arquivo [`run_analysis.py`](run_analysis.py).

## Saídas do Experimento

Após a execução, os seguintes artefatos serão gerados no diretório `output/`:

* **`output/instances/`**: Arquivos `.txt` contendo as instâncias geradas para os testes.
* **`output/results/`**:
  * `resultados_variando_n.csv`: Dados brutos dos experimentos com `n` variável.
  * `resultados_variando_W.csv`: Dados brutos dos experimentos com `W` variável.
  * `resultados_combinados.xlsx`: Planilha Excel com os resultados para fácil análise.
  * `relatorios/`: Relatórios em Markdown com resumos estatísticos e conclusões.
* **`output/graphs/`**: Gráficos em formato `.png` que comparam o tempo de execução e outras métricas dos algoritmos, facilitando a visualização do desempenho.
