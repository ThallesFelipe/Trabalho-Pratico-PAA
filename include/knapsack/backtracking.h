/**
 * @file backtracking.h
 * @brief Algoritmo de Backtracking para o Problema da Mochila.
 *
 * Este arquivo contém a declaração do algoritmo de Backtracking para resolver o
 * Problema da Mochila, incluindo técnicas de poda para melhorar o desempenho.
 * 
 * @author Thalles Felipe Rodrigues de Almeidad Santos - 21.2.4130
 * @date Março 2025
 */

#ifndef KNAPSACK_BACKTRACKING_H
#define KNAPSACK_BACKTRACKING_H

#include <vector>
#include <utility>

/**
 * @brief Resolve o Problema da Mochila usando o algoritmo de Backtracking.
 *
 * Esta implementação utiliza a técnica de backtracking com várias otimizações:
 * 1. Ordenação dos itens por razão valor/peso para melhorar a poda
 * 2. Poda por limites superiores usando o valor restante dos itens
 * 3. Poda por viabilidade verificando se excede a capacidade da mochila
 *
 * O algoritmo explora recursivamente todas as possibilidades viáveis de seleção de itens,
 * mantendo controle da melhor solução encontrada durante a busca.
 *
 * Características:
 * - Os itens são ordenados por razão valor/peso (decrescente)
 * - Usa técnicas de poda para reduzir o espaço de busca
 * - Retorna a seleção ótima de itens e o valor máximo correspondente
 *
 * Complexidade de tempo: O(2^n) no pior caso
 * Complexidade de espaço: O(n) para a pilha de recursão
 *
 * @param capacidade Capacidade máxima da mochila
 * @param pesos Vetor contendo os pesos de cada item
 * @param valores Vetor contendo os valores de cada item
 * @return std::pair<int, std::vector<int>> Par contendo o valor máximo obtido e os índices dos itens selecionados
 */
std::pair<int, std::vector<int>> knapsack_backtracking(int capacidade,
                                                       const std::vector<int> &pesos,
                                                       const std::vector<int> &valores);

#endif // KNAPSACK_BACKTRACKING_H