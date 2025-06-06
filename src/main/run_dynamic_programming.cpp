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
#include <cstring>
#include <filesystem>
#include <cstdlib>
#include <stdexcept>

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
            std::cout << indice + 1 << " ";
        }
        std::cout << std::endl;
        std::cout << "Tempo de execução: " << std::fixed << std::setprecision(6) << duracao.count() << " segundos" << std::endl;

        // Correção para todos os arquivos main (run_*.cpp)
        const char* results_dir = std::getenv("RESULTS_DIR");
        std::string output_path;

        if (results_dir && strlen(results_dir) > 0) {
            output_path = results_dir;
            // Criar diretório se não existir
            std::filesystem::path dir_path(output_path);
            if (!std::filesystem::exists(dir_path)) {
                try {
                    std::filesystem::create_directories(dir_path);
                } catch (const std::exception& e) {
                    std::cerr << "Aviso: Não foi possível criar o diretório '" << output_path 
                              << "': " << e.what() << std::endl;
                    output_path = ".";
                }
            }
        } else {
            output_path = "output/results";
            // Create directory if it doesn't exist
            std::filesystem::path dir_path(output_path);
            if (!std::filesystem::exists(dir_path)) {
                try {
                    std::filesystem::create_directories(dir_path);
                } catch (const std::exception& e) {
                    std::cerr << "Error creating directory: " << e.what() << std::endl;
                    output_path = ".";
                }
            }
        }

        // Corrigir o caminho de saída para lidar com WSL vs Windows
        std::string separator = "/";
        #ifdef _WIN32
            separator = "\\";
        #endif

        // Nome do arquivo baseado no algoritmo para evitar sobreescrita
        std::string output_filename = "dynamic_programming_results.csv";
        std::filesystem::path output_path_fs(output_path);
        std::filesystem::path output_file_path = output_path_fs / output_filename;
        
        std::ofstream output_file(output_file_path);
        if (output_file.is_open()) {
            // Formato CSV consistente para facilitar a análise posterior
            output_file << "algoritmo,dynamic_programming" << std::endl;
            output_file << "valor," << valor_maximo << std::endl;
            output_file << "tempo," << std::fixed << std::setprecision(6) << duracao.count() << std::endl;
            output_file << "n," << pesos.size() << std::endl;
            output_file << "W," << capacidade << std::endl;
            
            output_file << "itens,";
            for (size_t i = 0; i < itens_selecionados.size(); ++i) {
                output_file << itens_selecionados[i] + 1;
                if (i < itens_selecionados.size() - 1) {
                    output_file << ";";
                }
            }
            output_file << std::endl;
            
            output_file.close();
            std::cout << "Resultados salvos em: " << output_file_path << std::endl;
        } else {
            std::cerr << "Erro ao abrir arquivo para escrita de resultados: " << output_file_path << std::endl;
            return 1;
        }

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