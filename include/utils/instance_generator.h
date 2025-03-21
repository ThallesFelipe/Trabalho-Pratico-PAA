/**
 * @file instance_generator.h
 * @brief Gerador de instâncias para o Problema da Mochila.
 *
 * Este arquivo contém as declarações das funções necessárias para gerar
 * e salvar instâncias do Problema da Mochila com parâmetros configuráveis.
 *
 * As instâncias são geradas com valores aleatórios para pesos e valores
 * e salvas em arquivos de texto para serem utilizadas nos experimentos.
 *
 * @date Março 2025
 */

#ifndef INSTANCE_GENERATOR_H
#define INSTANCE_GENERATOR_H

#include <string>
#include <vector>

/**
 * @brief Salva uma instância do problema da mochila em um arquivo.
 *
 * @param nome_arquivo Caminho do arquivo onde a instância será salva
 * @param capacidade Capacidade da mochila (W)
 * @param itens Vetor de pares (peso, valor) representando os itens
 */
void salvar_instancia(const std::string &nome_arquivo,
                      int capacidade,
                      const std::vector<std::pair<int, int>> &itens);

/**
 * @brief Gera múltiplas instâncias do problema da mochila.
 *
 * Esta função gera um número específico de instâncias do problema da mochila,
 * criando um diretório específico para armazená-las se necessário.
 * As instâncias são geradas com pesos aleatórios entre 1 e 30, e valores
 * aleatórios entre 1 e 100. A estrutura de diretórios usada é:
 *
 * [INSTANCES_DIR]/instancias_n[N]_W[W]/instancia_[i].txt
 *
 * Onde:
 * - [INSTANCES_DIR] é o diretório base de instâncias (padrão ./output/instances)
 * - [N] é o número de itens
 * - [W] é a capacidade da mochila
 * - [i] é o número da instância
 *
 * @param num_instancias Número de instâncias a serem geradas
 * @param n Número de itens em cada instância
 * @param W Capacidade da mochila
 * @return true se a geração foi bem-sucedida, false caso contrário
 */
bool gerar_instancias(int num_instancias, int n, int W);

#endif // INSTANCE_GENERATOR_H