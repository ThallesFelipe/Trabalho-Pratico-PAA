/**
 * @file dynamic_programming.cpp
 * @brief Implementação dos algoritmos de Programação Dinâmica para o Problema da Mochila.
 *
 * Este arquivo contém duas implementações do algoritmo de Programação Dinâmica:
 * 1. Uma implementação tradicional usando matriz 2D
 * 2. Uma implementação otimizada usando array 1D com mesma funcionalidade
 */

#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <algorithm>
#include "knapsack/dynamic_programming.h"

/**
 * @brief Resolve o problema da mochila usando programação dinâmica com abordagem de matriz 2D.
 *
 * @param capacidade Capacidade máxima da mochila
 * @param pesos Vetor contendo os pesos de cada item
 * @param valores Vetor contendo os valores de cada item
 * @return std::pair<int, std::vector<int>> Par contendo o valor máximo obtido e os índices dos itens selecionados
 */
std::pair<int, std::vector<int>> knapsack_dynamic_programming(int capacidade, const std::vector<int> &pesos, const std::vector<int> &valores)
{
    int n = pesos.size();
    std::vector<std::vector<int>> tabela(n + 1, std::vector<int>(capacidade + 1, 0));

    // Preenche a tabela de programação dinâmica
    for (int i = 1; i <= n; i++)
    {
        for (int w = 0; w <= capacidade; w++)
        {
            // Não incluir o item i
            tabela[i][w] = tabela[i - 1][w];

            // Incluir o item i se ele couber na mochila
            if (pesos[i - 1] <= w)
            {
                tabela[i][w] = std::max(tabela[i][w],
                                        tabela[i - 1][w - pesos[i - 1]] + valores[i - 1]);
            }
        }
    }

    // Reconstruir a solução rastreando os itens selecionados
    std::vector<int> itens_selecionados;
    int w = capacidade;
    for (int i = n; i > 0; i--)
    {
        if (tabela[i][w] != tabela[i - 1][w])
        {
            itens_selecionados.push_back(i - 1); // Indexação base-0
            w -= pesos[i - 1];
        }
    }

    return {tabela[n][capacidade], itens_selecionados};
}

/**
 * @brief Resolve o problema da mochila usando programação dinâmica otimizada com array 1D.
 *
 * Esta implementação é mais eficiente em termos de memória que a versão padrão.
 *
 * @param capacidade Capacidade máxima da mochila
 * @param pesos Vetor contendo os pesos de cada item
 * @param valores Vetor contendo os valores de cada item
 * @return std::pair<int, std::vector<int>> Par contendo o valor máximo obtido e os índices dos itens selecionados
 */
std::pair<int, std::vector<int>> knapsack_dynamic_programming_optimized(int capacidade, const std::vector<int> &pesos, const std::vector<int> &valores)
{
    int n = pesos.size();
    std::vector<int> tabela(capacidade + 1, 0);
    std::vector<std::vector<bool>> selecionado(n + 1, std::vector<bool>(capacidade + 1, false));

    // Preenche a tabela de programação dinâmica com otimização de memória (array 1D)
    for (int i = 1; i <= n; ++i)
    {
        // Processa de trás para frente para evitar usar o mesmo item várias vezes
        for (int w = capacidade; w >= pesos[i - 1]; --w)
        {
            // Verifica se incluir o item atual melhora a solução
            if (valores[i - 1] + tabela[w - pesos[i - 1]] > tabela[w])
            {
                tabela[w] = valores[i - 1] + tabela[w - pesos[i - 1]];
                selecionado[i][w] = true;
            }
        }
    }

    // Reconstrói a solução identificando quais itens foram selecionados
    std::vector<int> itens_selecionados;
    int w = capacidade;
    for (int i = n; i > 0; --i)
    {
        if (selecionado[i][w])
        {
            itens_selecionados.push_back(i - 1); // Indexação base-0
            w -= pesos[i - 1];
        }
    }
    // Inverte para obter os itens na ordem correta (do primeiro ao último)
    std::reverse(itens_selecionados.begin(), itens_selecionados.end());

    return {tabela[capacidade], itens_selecionados};
}