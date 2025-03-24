/**
 * @file dynamic_programming.h
 * @brief Algoritmos de Programação Dinâmica para o Problema da Mochila.
 *
 * Este arquivo contém as declarações dos algoritmos de Programação Dinâmica
 * para resolver o Problema da Mochila, incluindo uma versão padrão com
 * matriz 2D e uma versão otimizada com uso de array 1D.
 * @author David Souza do Nascimento - 19.2.4029
 * @author Luiz Henrique de Carvalho - 21.2.4106
 * @author Thalles Felipe Rodrigues de Almeidad Santos - 21.2.4130
 * @date Março 2025
 */

#ifndef KNAPSACK_DYNAMIC_PROGRAMMING_H
#define KNAPSACK_DYNAMIC_PROGRAMMING_H

#include <vector>
#include <utility>

/**
 * @brief Resolve o Problema da Mochila usando o algoritmo de Programação Dinâmica.
 *
 * Esta implementação utiliza uma abordagem tradicional com matriz bidimensional
 * para armazenar os resultados intermediários. O algoritmo preenche uma tabela
 * de tamanho (n+1) × (capacidade+1) e rastreia quais itens foram incluídos na
 * solução ótima.
 *
 * Complexidade de tempo: O(n × capacidade)
 * Complexidade de espaço: O(n × capacidade)
 *
 * @param capacidade Capacidade máxima da mochila
 * @param pesos Vetor contendo os pesos de cada item
 * @param valores Vetor contendo os valores de cada item
 * @return std::pair<int, std::vector<int>> Par contendo o valor máximo obtido e os índices dos itens selecionados
 */
std::pair<int, std::vector<int>> knapsack_dynamic_programming(int capacidade,
                                                              const std::vector<int> &pesos,
                                                              const std::vector<int> &valores);

/**
 * @brief Resolve o Problema da Mochila usando o algoritmo de Programação Dinâmica otimizado.
 *
 * Esta implementação utiliza apenas um array unidimensional para armazenar os resultados
 * intermediários, economizando memória em relação à abordagem tradicional. Requer uma
 * matriz auxiliar para rastrear quais itens foram incluídos na solução ótima.
 *
 * O algoritmo processa a tabela de trás para frente para cada item, evitando
 * usar o mesmo item múltiplas vezes na solução.
 *
 * Complexidade de tempo: O(n × capacidade)
 * Complexidade de espaço: O(capacidade) + O(n × capacidade) para rastreamento
 *
 * @param capacidade Capacidade máxima da mochila
 * @param pesos Vetor contendo os pesos de cada item
 * @param valores Vetor contendo os valores de cada item
 * @return std::pair<int, std::vector<int>> Par contendo o valor máximo obtido e os índices dos itens selecionados
 */
std::pair<int, std::vector<int>> knapsack_dynamic_programming_optimized(int capacidade,
                                                                        const std::vector<int> &pesos,
                                                                        const std::vector<int> &valores);

#endif // KNAPSACK_DYNAMIC_PROGRAMMING_H