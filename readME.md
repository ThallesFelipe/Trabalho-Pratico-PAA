Este repositório contém uma implementação e análise experimental de algoritmos para o clássico Problema da Mochila (Knapsack Problem). O trabalho compara três algoritmos diferentes em termos de desempenho e eficiência.

![Knapsack Problem](https://upload.wikimedia.org/wikipedia/commons/f/fd/Knapsack.svg)

## 📋 Índice

- Sobre o Projeto
- Algoritmos Implementados
- Estrutura do Projeto
- Requisitos
- Configuração do Ambiente
- Como Executar
- Analisando os Resultados
- Exemplos
- Limitações
- Autores

## 📝 Sobre o Projeto

Este trabalho prático tem como objetivo implementar e analisar experimentalmente três algoritmos diferentes para o Problema da Mochila:

1. **Programação Dinâmica**: Abordagem bottom-up com matriz de memorização
2. **Backtracking**: Implementação com poda para otimização
3. **Branch and Bound**: Algoritmo com limitantes e fila de prioridade

O projeto inclui ferramentas para geração de instâncias, execução de experimentos e análise estatística dos resultados obtidos.

## 🧮 Algoritmos Implementados

### Programação Dinâmica
- **Complexidade de tempo**: O(n·W) 
- **Complexidade de espaço**: O(n·W)
- **Implementação**: dynamic_programming.h e dynamic_programming.cpp

### Backtracking
- **Complexidade de tempo**: O(2^n) no pior caso
- **Complexidade de espaço**: O(n)
- **Implementação**: backtracking.h e backtracking.cpp

### Branch and Bound
- **Complexidade de tempo**: O(2^n) no pior caso, geralmente melhor na prática
- **Complexidade de espaço**: O(n)
- **Implementação**: branch_and_bound.h e branch_and_bound.cpp

## 📁 Estrutura do Projeto

```
.
├── CMakeLists.txt              # Script de configuração do CMake
├── config.py                   # Configurações para os scripts Python
├── include/                    # Arquivos de cabeçalho C++
│   ├── knapsack/               # Interfaces dos algoritmos da mochila
│   └── utils/                  # Utilitários C++
├── output/                     # Diretório para resultados
│   ├── graphs/                 # Gráficos gerados
│   ├── instances/              # Instâncias de teste
│   └── results/                # Resultados dos experimentos
├── python/                     # Scripts Python
│   ├── experiments.py          # Principal script de experimentos
│   ├── path_converter.py       # Utilitário para caminhos de arquivos
│   └── test_instances.py       # Testes de instâncias
├── run_analysis.py             # Script principal para análise
├── scripts/                    # Scripts de utilitários
│   ├── enhanced_visualizations.py  # Visualizações avançadas
│   ├── generate_visualizations.py  # Geração de gráficos
│   └── run_experiments_mac.sh      # Script para Mac
└── src/                        # Código-fonte C++
    ├── algorithms/             # Implementações dos algoritmos
    ├── main/                   # Programas principais
    └── utils/                  # Utilitários C++
```

## 🔧 Requisitos

### Para compilação C++:
- GCC/G++ 7.0+ ou Clang 6.0+ com suporte a C++17
- CMake 3.10+
- Make ou um sistema de build compatível

### Para experimentos e análise (Python):
- Python 3.8+
- Pandas 1.0+
- NumPy 1.18+
- Matplotlib 3.2+
- Seaborn 0.11+
- SciPy 1.4+
- Tabulate 0.8+

## 🛠️ Configuração do Ambiente

### 1. Instalação das dependências C++

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install build-essential cmake
```

#### macOS:
```bash
brew install cmake gcc
```

#### Windows:
Instale o [MinGW-w64](https://www.mingw-w64.org/downloads/) ou [MSYS2](https://www.msys2.org/) para GCC, e [CMake](https://cmake.org/download/).

### 2. Instalação das dependências Python

```bash
pip install numpy pandas matplotlib seaborn scipy tabulate
```

### 3. Clone o repositório

```bash
git clone https://github.com/seu-usuario/Trabalho-Pratico-PAA.git
cd Trabalho-Pratico-PAA
```

### 4. Compile o código C++

```bash
mkdir -p build
cd build
cmake ..
make
```

Isso criará os executáveis necessários na pasta bin.

## ▶️ Como Executar

Existem três principais formas de executar os experimentos:

### 1. Execução direta dos algoritmos individuais

```bash
# A partir da raiz do projeto
./build/bin/run_dynamic_programming output/instances/instancia_teste.txt
./build/bin/run_backtracking output/instances/instancia_teste.txt
./build/bin/run_branch_and_bound output/instances/instancia_teste.txt
```

### 2. Execução completa dos experimentos

```bash
# A partir da raiz do projeto
python run_analysis.py
```

Este script coordena:
1. Geração de instâncias de teste
2. Execução dos algoritmos em todas as instâncias
3. Análise de resultados e geração de estatísticas
4. Criação de visualizações

### 3. Execução em ambiente macOS

```bash
# A partir da raiz do projeto
chmod +x scripts/run_experiments_mac.sh
./scripts/run_experiments_mac.sh
```

## 📊 Analisando os Resultados

Após a execução, os resultados são salvos em:

- **CSV de resultados**: `output/results/*.csv`
- **Relatórios detalhados**: relatorios
- **Gráficos**: graphs

### Principais visualizações:

1. **Tempo vs n**: Análise do tempo de execução variando o número de itens
2. **Tempo vs W**: Análise do tempo de execução variando a capacidade
3. **Comparações estatísticas**: Testes t pareados entre algoritmos
4. **Análise assintótica**: Ajustes de curvas para validar complexidade teórica

Para gerar visualizações adicionais:

```bash
python scripts/generate_visualizations.py
```

## 📋 Exemplos

### Formato das instâncias de entrada

Um arquivo de instância tem o seguinte formato:
```
W
p1 v1
p2 v2
...
pn vn
```

Onde:
- `W` é a capacidade da mochila
- `pi` é o peso do item i
- `vi` é o valor do item i

Exemplo (`output/instances/instancia_teste.txt`):
```
100
10 60
20 100
30 120
40 160
50 200
```

### Formato de saída

O programa produz tanto saída no console quanto em arquivos CSV. Um exemplo de saída no console:

```
Algoritmo: Branch and Bound
Valor máximo: 420
Itens selecionados: 2 3 5
Tempo de execução: 0.000022 segundos
Resultados salvos em: output/results/branch_and_bound_results.csv
```

## ⚠️ Limitações

- O algoritmo de Backtracking pode ser impraticável para instâncias com muitos itens (n > 40) devido à sua complexidade exponencial.
- Os testes estatísticos assumem distribuição normal dos tempos de execução.
- Em sistemas Windows, o sinal de timeout não funciona como em sistemas Unix, então os timeouts podem não ser respeitados.

## 👥 Autores

- David Souza do Nascimento - 19.2.4029
- Luiz Henrique de Carvalho - 21.2.4106
- Thalles Felipe Rodrigues de Almeida Santos - 21.2.4130

---

Para qualquer dúvida ou problema, abra uma issue no repositório ou entre em contato com os autores.