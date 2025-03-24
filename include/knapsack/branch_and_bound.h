/**
 * @file branch_and_bound.h
 * @brief Implementação do algoritmo Branch and Bound para o Problema da Mochila.
 *
 * Este arquivo contém a declaração do algoritmo Branch and Bound para resolver o
 * Problema da Mochila, utilizando técnicas de limitantes para podar o espaço de busca.
 *
 * @author David Souza do Nascimento - 19.2.4029
 * @author Luiz Henrique de Carvalho - 21.2.4106
 * @author Thalles Felipe Rodrigues de Almeidad Santos - 21.2.4130
 * @date Março 2025
 */

#ifndef KNAPSACK_BRANCH_AND_BOUND_H
#define KNAPSACK_BRANCH_AND_BOUND_H

#include <vector>
#include <utility>

/**
 * @brief Resolve o Problema da Mochila usando o algoritmo Branch and Bound.
 *
 * Esta implementação usa uma fila de prioridade para explorar os nós mais promissores
 * primeiro, calculando limitantes superiores para podar partes do espaço de busca.
 * Os itens são ordenados por razão valor/peso para melhorar a eficiência das podas.
 *
 * Características do algoritmo:
 * - Usa fila de prioridade para explorar nós com maior limitante primeiro
 * - Ordena itens por razão valor/peso decrescente
 * - Calcula limitantes usando abordagem de solução fracionária
 * - Poda ramos não promissores da árvore de busca
 *
 * Complexidade de tempo: O(2^n) no pior caso, geralmente melhor na prática
 * Complexidade de espaço: O(n)
 *
 * @param capacidade Capacidade máxima da mochila
 * @param pesos Vetor contendo os pesos de cada item
 * @param valores Vetor contendo os valores de cada item
 * @return std::pair<int, std::vector<int>> Par contendo o valor máximo obtido e os índices dos itens selecionados
 */
std::pair<int, std::vector<int>> knapsack_branch_and_bound(int capacidade,
                                                           std::vector<int> &pesos,
                                                           std::vector<int> &valores);

#endif // KNAPSACK_BRANCH_AND_BOUND_H