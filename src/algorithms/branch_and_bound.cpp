/**
 * @file branch_and_bound.cpp
 * @brief Implementação do algoritmo Branch and Bound para o Problema da Mochila.
 *
 * Este arquivo contém a implementação do algoritmo Branch and Bound para resolver
 * o Problema da Mochila, utilizando uma abordagem com fila de prioridade e cálculo
 * de limitantes.
 */

#include <iostream>
#include <fstream>
#include <vector>
#include <queue>
#include <algorithm>
#include <limits>
#include "knapsack/branch_and_bound.h"

/**
 * @brief Estrutura para representar um item no problema da mochila.
 */
struct Item
{
    int peso;     ///< Peso do item
    int valor;    ///< Valor do item
    double razao; ///< Razão valor/peso para ordenação
    int indice;   ///< Índice original no vetor de entrada

    /**
     * @brief Construtor de um item.
     *
     * @param p Peso do item
     * @param v Valor do item
     * @param idx Índice original do item
     */
    Item(int p, int v, int idx) : peso(p), valor(v), razao(static_cast<double>(v) / p), indice(idx) {}
};

/**
 * @brief Estrutura para representar um nó na árvore de busca Branch and Bound.
 */
struct No
{
    int nivel;                      ///< Nível na árvore de decisão
    int lucro;                      ///< Lucro acumulado até o momento
    int peso;                       ///< Peso acumulado até o momento
    double limitante;               ///< Estimativa de limitante superior
    std::vector<bool> selecionados; ///< Itens selecionados neste nó

    /**
     * @brief Construtor de um nó com tamanho conhecido para evitar realocações.
     *
     * @param n Número de itens total no problema
     */
    No(int n) : nivel(0), lucro(0), peso(0), limitante(0), selecionados(n, false) {}

    /**
     * @brief Comparador para a fila de prioridade (maximizar limitante).
     *
     * @param outro Outro nó para comparação
     * @return true se este nó tem limitante menor que o outro
     */
    bool operator<(const No &outro) const
    {
        return limitante < outro.limitante;
    }
};

/**
 * @brief Calcula o limitante superior para um determinado nó.
 *
 * @param no Nó para o qual calcular o limitante
 * @param itens Vetor de itens ordenados por razão valor/peso
 * @param capacidade Capacidade da mochila
 * @return double Valor do limitante superior
 */
double calcular_limitante(const No &no, const std::vector<Item> &itens, int capacidade)
{
    // Se excedeu a capacidade, não há limitante válido
    if (no.peso > capacidade)
        return 0;

    // Começa com o lucro atual
    double limitante = no.lucro;
    int peso_atual = no.peso;
    int n = itens.size();

    // Adiciona itens completos enquanto couberem
    int i = no.nivel;
    while (i < n && peso_atual + itens[i].peso <= capacidade)
    {
        peso_atual += itens[i].peso;
        limitante += itens[i].valor;
        i++;
    }

    // Adiciona fração do próximo item, se possível
    if (i < n)
    {
        limitante += (capacidade - peso_atual) * itens[i].razao;
    }

    return limitante;
}

/**
 * @brief Resolve o Problema da Mochila usando o algoritmo Branch and Bound.
 *
 * @param capacidade Capacidade máxima da mochila
 * @param pesos Vetor contendo os pesos de cada item
 * @param valores Vetor contendo os valores de cada item
 * @return std::pair<int, std::vector<int>> Par contendo o valor máximo obtido e os índices dos itens selecionados
 */
std::pair<int, std::vector<int>> knapsack_branch_and_bound(int capacidade,
                                                           std::vector<int> &pesos,
                                                           std::vector<int> &valores)
{
    int n = pesos.size();

    // Cria lista de itens ordenada por razão valor/peso
    std::vector<Item> itens;
    itens.reserve(n);
    for (int i = 0; i < n; i++)
    {
        itens.emplace_back(pesos[i], valores[i], i);
    }

    // Ordena itens por razão valor/peso (não-crescente)
    std::sort(itens.begin(), itens.end(),
              [](const Item &a, const Item &b)
              { return a.razao > b.razao; });

    // Fila de prioridade usando o operador< do No (max-heap)
    std::priority_queue<No> fila_prioridade;

    // Rastreamento da melhor solução
    int lucro_maximo = 0;
    std::vector<bool> melhor_solucao(n, false);

    // Cria nó raiz e calcula seu limitante
    No raiz(n);
    raiz.limitante = calcular_limitante(raiz, itens, capacidade);
    fila_prioridade.push(raiz);

    // Explora a árvore de Branch and Bound
    while (!fila_prioridade.empty())
    {
        // Obtém o nó com o maior limitante
        No no = fila_prioridade.top();
        fila_prioridade.pop();

        // Se o limitante for menor que o lucro máximo atual, poda este ramo
        if (no.limitante <= lucro_maximo)
        {
            continue;
        }

        // Se chegamos ao último nível, atualiza o lucro máximo se necessário
        if (no.nivel == n)
        {
            if (no.lucro > lucro_maximo)
            {
                lucro_maximo = no.lucro;
                melhor_solucao = no.selecionados;
            }
            continue;
        }

        // Tenta incluir o item atual
        No no_incluir = no;
        no_incluir.nivel++;
        no_incluir.peso += itens[no.nivel].peso;
        no_incluir.lucro += itens[no.nivel].valor;
        no_incluir.selecionados[itens[no.nivel].indice] = true;

        // Se incluir não exceder a capacidade e tiver potencial
        if (no_incluir.peso <= capacidade)
        {
            no_incluir.limitante = calcular_limitante(no_incluir, itens, capacidade);

            // Atualiza lucro máximo se tivermos uma solução completa
            if (no_incluir.nivel == n && no_incluir.lucro > lucro_maximo && no_incluir.peso <= capacidade)
            {
                lucro_maximo = no_incluir.lucro;
                melhor_solucao = no_incluir.selecionados;
            }

            // Adiciona à fila de prioridade se o limitante for promissor
            if (no_incluir.limitante > lucro_maximo)
            {
                fila_prioridade.push(no_incluir);
            }
        }

        // Tenta excluir o item atual
        No no_excluir = no;
        no_excluir.nivel++;
        no_excluir.limitante = calcular_limitante(no_excluir, itens, capacidade);

        // Adiciona à fila de prioridade se o limitante for promissor
        if (no_excluir.limitante > lucro_maximo)
        {
            fila_prioridade.push(no_excluir);
        }
    }

    // Converte o vetor booleano de seleção para índices
    std::vector<int> indices_selecionados;
    for (int i = 0; i < n; i++)
    {
        if (melhor_solucao[i])
        {
            indices_selecionados.push_back(i);
        }
    }

    return {lucro_maximo, indices_selecionados};
}