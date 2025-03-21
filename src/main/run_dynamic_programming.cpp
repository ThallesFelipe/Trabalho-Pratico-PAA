/**
 * @file run_dynamic_programming.cpp
 * @brief Programa principal para execução do algoritmo de Programação Dinâmica para o Problema da Mochila.
 *
 * Este programa lê dados de um arquivo de entrada, executa o algoritmo de Programação Dinâmica
 * para resolver o Problema da Mochila e exibe os resultados, incluindo o valor máximo
 * obtido, os itens selecionados e o tempo de execução.
 */

#include "knapsack/dynamic_programming.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <iomanip>

/**
 * @brief Função principal que executa o algoritmo de Programação Dinâmica.
 *
 * @param argc Número de argumentos da linha de comando.
 * @param argv Vetor de argumentos da linha de comando.
 * @return int Código de retorno (0 para sucesso, 1 para erro).
 */
int main(int argc, char *argv[])
{
    try
    {
        // Verifica se o número correto de argumentos foi fornecido
        if (argc != 2)
        {
            std::cerr << "Uso: " << argv[0] << " <arquivo_entrada>" << std::endl;
            return 1;
        }

        // Abre o arquivo de entrada
        std::string filename = argv[1];
        std::ifstream infile(filename);
        if (!infile.is_open())
        {
            std::cerr << "Erro: O arquivo '" << filename << "' não foi encontrado." << std::endl;
            return 1;
        }

        // Lê a capacidade da mochila
        int capacidade;
        if (!(infile >> capacidade))
        {
            std::cerr << "Erro: Formato de arquivo inválido (capacidade não encontrada)." << std::endl;
            return 1;
        }

        // Lê os pesos e valores dos itens
        std::vector<int> pesos, valores;
        int peso, valor;
        while (infile >> peso >> valor)
        {
            if (peso < 0 || valor < 0)
            {
                std::cerr << "Erro: Valores negativos não são permitidos." << std::endl;
                return 1;
            }
            pesos.push_back(peso);
            valores.push_back(valor);
        }
        infile.close();

        // Verifica se há itens para processar
        if (pesos.empty())
        {
            std::cerr << "Erro: Nenhum item encontrado no arquivo." << std::endl;
            return 1;
        }

        // Executa o algoritmo de Programação Dinâmica e mede o tempo de execução
        auto inicio = std::chrono::high_resolution_clock::now();
        auto [valor_maximo, itens_selecionados] = knapsack_dynamic_programming(capacidade, pesos, valores);
        auto fim = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> duracao = fim - inicio;

        // Exibe os resultados
        std::cout << "Algoritmo: Programação Dinâmica" << std::endl;
        std::cout << "Valor máximo: " << valor_maximo << std::endl;
        std::cout << "Itens selecionados: ";
        for (int indice : itens_selecionados)
        {
            std::cout << indice + 1 << " "; // Ajuste para exibição base-1 (mais amigável ao usuário)
        }
        std::cout << std::endl;
        std::cout << "Tempo de execução: " << std::fixed << std::setprecision(6) << duracao.count() << " segundos" << std::endl;

        const char* results_dir = std::getenv("RESULTS_DIR");
        std::string output_path = results_dir ? results_dir : ".";
        std::ofstream output_file(output_path + "/results.txt");

        return 0;
    }
    catch (const std::exception &e)
    {
        // Tratamento de exceções conhecidas
        std::cerr << "Erro inesperado: " << e.what() << std::endl;
        return 1;
    }
    catch (...)
    {
        // Tratamento de exceções desconhecidas
        std::cerr << "Erro desconhecido ocorreu." << std::endl;
        return 1;
    }
}