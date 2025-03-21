# Projeto de Análise de Algoritmos para o Problema da Mochila

![C++](https://img.shields.io/badge/language-C%2B%2B-blue)
![CMake](https://img.shields.io/badge/build-CMake-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## Descrição

Este projeto implementa e analisa três algoritmos diferentes para resolver o clássico **Problema da Mochila**: Programação Dinâmica, Backtracking e Branch and Bound. O objetivo é comparar o desempenho destes algoritmos em termos de tempo de execução e eficiência para diferentes tamanhos de instâncias.

O Problema da Mochila é um problema de otimização combinatória onde, dados um conjunto de itens com pesos e valores, deve-se determinar o número de cada item a incluir em uma coleção para que o peso total seja menor ou igual a um limite e o valor total seja maximizado.

## Estrutura do Projeto

```
/
├── include/               # Arquivos de cabeçalho
│   ├── knapsack/          # Interfaces dos algoritmos
│   └── utils/             # Utilitários para o projeto
├── src/                   # Código fonte
│   ├── algorithms/        # Implementação dos algoritmos
│   ├── main/              # Programas principais
│   └── utils/             # Utilitários e ferramentas
├── scripts/               # Scripts para automação
├── output/                # Diretório para saída de resultados
│   ├── instances/         # Instâncias geradas
│   ├── results/           # Resultados de experimentos
│   └── graphs/            # Gráficos gerados
├── python/                # Scripts Python para análise
└── build/                 # Diretório de build (gerado)
```

## Pré-requisitos

Para compilar e executar este projeto, você precisará:

- Compilador C++ com suporte a C++17 (GCC 7+ ou equivalente)
- CMake 3.10 ou superior
- Python 3.6 ou superior (para análise de resultados)
- Bibliotecas Python: numpy, matplotlib, scipy, pandas

## Instalação

### Linux/WSL

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/projeto-mochila.git
cd projeto-mochila

# Criar e configurar o diretório de build
mkdir -p build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release

# Compilar o projeto
make

# Executar os testes (opcional)
make test
```

### macOS

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/projeto-mochila.git
cd projeto-mochila

# Instalar dependências (se necessário)
brew install cmake

# Script automatizado de compilação
chmod +x scripts/run_experiments_mac.sh
./scripts/run_experiments_mac.sh
```

### Windows (com WSL)

Recomendamos usar WSL para desenvolvimento em Windows. Siga as instruções para Linux acima.

## Uso

### Geração de Instâncias

Para gerar instâncias do problema:

```bash
./build/bin/generate_instances [número_instâncias] [tamanho_máximo] [capacidade_máxima]
```

Exemplo:
```bash
./build/bin/generate_instances 5 20 100
```

### Execução dos Algoritmos

Para executar um algoritmo específico:

```bash
./build/bin/run_dynamic_programming [caminho_para_instância]
./build/bin/run_backtracking [caminho_para_instância]
./build/bin/run_branch_and_bound [caminho_para_instância]
```

Exemplo:
```bash
./build/bin/run_dynamic_programming output/instances/instancia_n20_W25/instancia_1.txt
```

### Execução de Experimentos

Para executar todos os experimentos e gerar gráficos comparativos:

```bash
python3 python/experiments.py
```

## Funcionalidades

- **Múltiplas Abordagens**: Implementações de Programação Dinâmica, Backtracking e Branch and Bound
- **Geração de Instâncias**: Criação automatizada de instâncias com parâmetros configuráveis
- **Análise de Desempenho**: Medição e comparação de tempos de execução
- **Visualização de Resultados**: Geração de gráficos para análise comparativa
- **Scripts Automatizados**: Facilitação do processo de compilação e execução

## Detalhes dos Algoritmos

### Programação Dinâmica

Utiliza uma abordagem bottom-up para construir soluções ótimas a partir de subproblemas menores, com complexidade de tempo O(nW), onde n é o número de itens e W é a capacidade da mochila.

### Backtracking

Explora todas as combinações possíveis de inclusão/exclusão de itens, com podas para reduzir o espaço de busca. Complexidade de tempo no pior caso: O(2^n).

### Branch and Bound

Utiliza limites superiores para podar ramos da árvore de busca que não levarão a soluções ótimas, melhorando o desempenho em relação ao backtracking puro.

## Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas alterações (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.