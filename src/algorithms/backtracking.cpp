/**
 * @file backtracking.cpp
 * @brief Implementação do algoritmo de Backtracking para o Problema da Mochila.
 *
 * Este arquivo contém a implementação do algoritmo de Backtracking para resolver
 * o Problema da Mochila, incluindo uma versão otimizada com técnicas de poda.
 */

#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <algorithm>
#include <limits>
#include "knapsack/backtracking.h"

/**
 * @brief Estrutura para representar um item no problema da mochila.
 */
struct Item
{
    int peso;     ///< Peso do item
    int valor;    ///< Valor do item
    double razao; ///< Razão valor/peso para ordenação
    int indice;   ///< Índice original no vetor de entrada
};

/**
 * @brief Implementação recursiva do algoritmo de backtracking.
 *
 * @param indice Índice do item atual sendo considerado
 * @param peso_atual Peso atual acumulado na mochila
 * @param valor_atual Valor atual acumulado na mochila
 * @param itens Vetor de itens ordenados por razão valor/peso
 * @param capacidade Capacidade máxima da mochila
 * @param selecao_atual Vetor de índices dos itens atualmente selecionados
 * @param valor_maximo Melhor valor encontrado até o momento (atualizado por referência)
 * @param melhor_selecao Melhor seleção de itens encontrada (atualizada por referência)
 * @param valor_restante Soma dos valores dos itens ainda não considerados
 */
void backtrack(int indice, int peso_atual, int valor_atual, const std::vector<Item> &itens,
               int capacidade, std::vector<int> &selecao_atual,
               int &valor_maximo, std::vector<int> &melhor_selecao, int valor_restante)
{
    // Poda: se o valor atual + valor remanescente não superar o melhor valor encontrado
    if (valor_atual + valor_restante <= valor_maximo)
        return;

    // Poda: se ultrapassar a capacidade
    if (peso_atual > capacidade)
        return;

    // Caso base: todos os itens foram considerados
    if (indice == static_cast<int>(itens.size()))
    {
        if (valor_atual > valor_maximo)
        {
            valor_maximo = valor_atual;
            melhor_selecao = selecao_atual;
        }
        return;
    }

    // Incluir este item (apenas se não exceder a capacidade)
    if (peso_atual + itens[indice].peso <= capacidade)
    {
        selecao_atual.push_back(itens[indice].indice);
        backtrack(indice + 1, peso_atual + itens[indice].peso, valor_atual + itens[indice].valor,
                  itens, capacidade, selecao_atual, valor_maximo, melhor_selecao,
                  valor_restante - itens[indice].valor);
        selecao_atual.pop_back();
    }

    // Pular este item
    backtrack(indice + 1, peso_atual, valor_atual, itens, capacidade,
              selecao_atual, valor_maximo, melhor_selecao, valor_restante - itens[indice].valor);
}

bool pode_alcancar_melhor_valor(int valor_atual, int valor_restante, int valor_maximo) {
    // Verificação rápida antes de fazer cálculos mais intensivos
    if (valor_atual + valor_restante <= valor_maximo) 
        return false;
    return true;
}

/**
 * @brief Implementação otimizada do algoritmo de backtracking usando vetores de bits.
 *
 * @param indice Índice do item atual sendo considerado
 * @param peso_atual Peso atual acumulado na mochila
 * @param valor_atual Valor atual acumulado na mochila
 * @param itens Vetor de itens ordenados por razão valor/peso
 * @param capacidade Capacidade máxima da mochila
 * @param selecao_atual Vetor de booleanos indicando quais itens estão selecionados
 * @param valor_maximo Melhor valor encontrado até o momento (atualizado por referência)
 * @param melhor_selecao Melhor seleção de itens encontrada (atualizada por referência)
 * @param valor_restante Soma dos valores dos itens ainda não considerados
 */
void backtrack_otimizado(int indice, int peso_atual, int valor_atual,
                     const std::vector<Item> &itens, int capacidade,
                     std::vector<bool> &selecao_atual, int &valor_maximo,
                     std::vector<bool> &melhor_selecao, int valor_restante)
{
    // Otimização: verificação rápida antes de fazer outras operações
    if (!pode_alcancar_melhor_valor(valor_atual, valor_restante, valor_maximo))
        return;

    // Poda: se ultrapassar a capacidade
    if (peso_atual > capacidade)
        return;

    // Caso base: todos os itens foram considerados
    if (indice == static_cast<int>(itens.size()))
    {
        if (valor_atual > valor_maximo)
        {
            valor_maximo = valor_atual;
            melhor_selecao = selecao_atual;
        }
        return;
    }

    // Incluir este item (apenas se não exceder a capacidade)
    if (peso_atual + itens[indice].peso <= capacidade)
    {
        selecao_atual[itens[indice].indice] = true;
        backtrack_otimizado(indice + 1, peso_atual + itens[indice].peso,
                        valor_atual + itens[indice].valor,
                        itens, capacidade, selecao_atual, valor_maximo,
                        melhor_selecao, valor_restante - itens[indice].valor);
        selecao_atual[itens[indice].indice] = false;
    }

    // Pular item - corrigindo o valor do parâmetro valor_restante
    backtrack_otimizado(indice + 1, peso_atual, valor_atual,
                    itens, capacidade, selecao_atual,
                    valor_maximo, melhor_selecao,
                    valor_restante - itens[indice].valor);
}

/**
 * @brief Resolve o Problema da Mochila usando o algoritmo de Backtracking.
 *
 * @param capacidade Capacidade máxima da mochila
 * @param pesos Vetor contendo os pesos de cada item
 * @param valores Vetor contendo os valores de cada item
 * @return std::pair<int, std::vector<int>> Par contendo o valor máximo obtido e os índices dos itens selecionados
 */
std::pair<int, std::vector<int>> knapsack_backtracking(int capacidade, const std::vector<int> &pesos, const std::vector<int> &valores)
{
    int n = pesos.size();

    // Criar e ordenar itens por relação valor/peso (decrescente)
    std::vector<Item> itens(n);
    int valor_total = 0;

    for (int i = 0; i < n; i++)
    {
        itens[i].peso = pesos[i];
        itens[i].valor = valores[i];
        itens[i].razao = static_cast<double>(valores[i]) / pesos[i];
        itens[i].indice = i;
        valor_total += valores[i];
    }

    // Ordenar por relação valor/peso para melhor poda
    std::sort(itens.begin(), itens.end(),
              [](const Item &a, const Item &b)
              { return a.razao > b.razao; });

    // Variáveis para o backtracking
    std::vector<int> selecao_atual;
    std::vector<int> melhor_selecao;
    int valor_maximo = 0;

    // Iniciar o backtracking
    backtrack(0, 0, 0, itens, capacidade, selecao_atual, valor_maximo, melhor_selecao, valor_total);

    // Ordenar a seleção por índice para melhor legibilidade
    std::sort(melhor_selecao.begin(), melhor_selecao.end());

    return {valor_maximo, melhor_selecao};
}