/**
 * @file generate_instances.cpp
 * @brief Programa principal para geração de instâncias para o Problema da Mochila.
 *
 * Este programa recebe parâmetros da linha de comando para gerar múltiplas instâncias
 * do Problema da Mochila com número de itens e capacidade específicos.
 */

#include <iostream>
#include <fstream>
#include <random>
#include <string>
#include <filesystem>
#include <cstdlib>
#include <vector>
#include "utils/instance_generator.h"

/**
 * @brief Função principal que coordena a geração de instâncias.
 *
 * @param argc Número de argumentos da linha de comando.
 * @param argv Vetor de argumentos da linha de comando.
 * @return int Código de retorno (0 para sucesso, 1 para erro).
 */
int main(int argc, char *argv[])
{
    // Verifica se o número correto de argumentos foi fornecido
    if (argc != 4)
    {
        std::cerr << "Uso: " << argv[0] << " <num_instancias> <num_itens> <capacidade>" << std::endl;
        std::cerr << "Exemplo: " << argv[0] << " 20 100 100" << std::endl;
        return 1;
    }

    // Extrai e converte os parâmetros da linha de comando
    int num_instancias = std::atoi(argv[1]);
    int n = std::atoi(argv[2]);
    int W = std::atoi(argv[3]);

    // Gera as instâncias usando a função definida em instance_generator.cpp
    if (!gerar_instancias(num_instancias, n, W))
    {
        return 1;
    }

    return 0;
}