/**
 * @file instance_generator.cpp
 * @brief Gerador de instâncias para o Problema da Mochila.
 *
 * Este arquivo contém funções para gerar e salvar instâncias
 * do Problema da Mochila com parâmetros configuráveis.
 */

#include <iostream>
#include <fstream>
#include <random>
#include <string>
#include <filesystem>
#include <cstdlib>
#include "utils/instance_generator.h"

/**
 * @brief Salva uma instância do problema da mochila em um arquivo.
 *
 * @param nome_arquivo Caminho do arquivo onde a instância será salva
 * @param capacidade Capacidade da mochila (W)
 * @param itens Vetor de pares (peso, valor) representando os itens
 */
void salvar_instancia(const std::string &nome_arquivo, int capacidade, const std::vector<std::pair<int, int>> &itens)
{
    std::ofstream arquivo_saida(nome_arquivo);
    if (!arquivo_saida.is_open())
    {
        std::cerr << "Erro ao abrir o arquivo: " << nome_arquivo << std::endl;
        return;
    }
    arquivo_saida << capacidade << std::endl;
    for (const auto &item : itens)
    {
        arquivo_saida << item.first << "\t" << item.second << std::endl;
    }
    arquivo_saida.close();
}

/**
 * @brief Gera múltiplas instâncias do problema da mochila.
 *
 * @param num_instancias Número de instâncias a serem geradas
 * @param n Número de itens em cada instância
 * @param W Capacidade da mochila
 * @return true se a geração foi bem-sucedida, false caso contrário
 */
bool gerar_instancias(int num_instancias, int n, int W)
{
    // Validação dos parâmetros de entrada
    if (num_instancias <= 0 || n <= 0 || W <= 0)
    {
        std::cerr << "Erro: todos os valores devem ser positivos." << std::endl;
        return false;
    }

    // Configuração do gerador de números aleatórios
    std::random_device rd;
    std::mt19937 gerador(rd());
    std::uniform_int_distribution<> dist_peso(1, 30);   // Peso entre 1 e 30
    std::uniform_int_distribution<> dist_valor(1, 100); // Valor entre 1 e 100

    // Obtém o diretório de saída da variável de ambiente ou usa o padrão
    std::string dir_base = std::getenv("INSTANCES_DIR") ? std::getenv("INSTANCES_DIR") : "./output/instances";

    // Utiliza separador de diretório apropriado dependendo do sistema operacional
    char sep_dir = std::filesystem::path::preferred_separator;

    // Cria o caminho do diretório para esta configuração específica de instâncias
    std::string diretorio = dir_base + sep_dir + "instancias_n" + std::to_string(n) + "_W" + std::to_string(W);

    // Cria os diretórios necessários se não existirem
    try
    {
        if (!std::filesystem::exists(dir_base))
        {
            std::filesystem::create_directories(dir_base);
        }

        if (!std::filesystem::exists(diretorio))
        {
            std::filesystem::create_directory(diretorio);
        }
    }
    catch (const std::filesystem::filesystem_error &e)
    {
        std::cerr << "Erro ao criar diretório: " << e.what() << std::endl;
        return false;
    }

    // Gera as instâncias
    for (int i = 1; i <= num_instancias; ++i)
    {
        // Cria um vetor para armazenar os itens (peso, valor)
        std::vector<std::pair<int, int>> itens;
        itens.reserve(n); // Reserva espaço para melhorar a eficiência

        // Gera n itens com peso e valor aleatórios
        for (int j = 0; j < n; ++j)
        {
            int peso = dist_peso(gerador);
            int valor = dist_valor(gerador);
            itens.emplace_back(peso, valor);
        }

        // Constrói o nome do arquivo para esta instância
        std::string nome_arquivo = diretorio + sep_dir + "instancia_" + std::to_string(i) + ".txt";

        // Salva a instância no arquivo
        salvar_instancia(nome_arquivo, W, itens);

        // Informa o usuário sobre o progresso
        std::cout << "Instância " << i << " gerada e salva em " << nome_arquivo << std::endl;
    }

    return true;
}