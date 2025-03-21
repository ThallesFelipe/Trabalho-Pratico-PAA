# Versão mínima do CMake requerida
cmake_minimum_required(VERSION 3.10)

# Nome e versão do projeto
project(algoritmos_mochila VERSION 1.0)

# Definir flags de compilação baseadas no tipo de build
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -flto")
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0 -Wall -Wextra -Wpedantic")

# Definir diretórios de saída de forma explícita
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(DIRETORIO_SAIDA ${CMAKE_SOURCE_DIR}/output)
set(DIRETORIO_INSTANCIAS ${DIRETORIO_SAIDA}/instances)
set(DIRETORIO_RESULTADOS ${DIRETORIO_SAIDA}/results)
set(DIRETORIO_GRAFICOS ${DIRETORIO_SAIDA}/graphs)

# Criar diretórios de saída se não existirem
file(MAKE_DIRECTORY ${DIRETORIO_SAIDA})
file(MAKE_DIRECTORY ${DIRETORIO_INSTANCIAS})
file(MAKE_DIRECTORY ${DIRETORIO_RESULTADOS})
file(MAKE_DIRECTORY ${DIRETORIO_GRAFICOS})

# Diretórios de inclusão
include_directories(include)

# Arquivos fonte para cada algoritmo
set(CODIGO_BACKTRACKING src/algorithms/backtracking.cpp)
set(CODIGO_BRANCH_AND_BOUND src/algorithms/branch_and_bound.cpp)
set(CODIGO_PROGRAMACAO_DINAMICA src/algorithms/dynamic_programming.cpp)
set(CODIGO_GERADOR_INSTANCIAS src/utils/instance_generator.cpp)

# Lista de todos os algoritmos para facilitar referências
set(ALGORITMOS_MOCHILA
    run_backtracking
    run_branch_and_bound
    run_dynamic_programming
)

# Adicionar executáveis para os algoritmos
add_executable(run_backtracking src/main/run_backtracking.cpp ${CODIGO_BACKTRACKING})
add_executable(run_branch_and_bound src/main/run_branch_and_bound.cpp ${CODIGO_BRANCH_AND_BOUND})
add_executable(run_dynamic_programming src/main/run_dynamic_programming.cpp ${CODIGO_PROGRAMACAO_DINAMICA})
add_executable(generate_instances src/main/generate_instances.cpp ${CODIGO_GERADOR_INSTANCIAS})

# Definir as propriedades dos executáveis para o diretório de saída
set_target_properties(
    ${ALGORITMOS_MOCHILA}
    generate_instances
    PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}"
)

# Criar um arquivo de configuração para scripts Python encontrarem os diretórios
configure_file(
    "${CMAKE_SOURCE_DIR}/config.template.py"
    "${CMAKE_SOURCE_DIR}/python/config.py"
    @ONLY
)

# Adicionar target para executar todos os testes
add_custom_target(executar_todos_testes
    COMMAND ${CMAKE_COMMAND} -E echo "Executando todos os algoritmos nos casos de teste..."
    DEPENDS ${ALGORITMOS_MOCHILA}
)

# Adicionar target para gerar a documentação com Doxygen (se disponível)
find_package(Doxygen QUIET)
if(DOXYGEN_FOUND)
    add_custom_target(doc
        COMMAND ${DOXYGEN_EXECUTABLE} ${CMAKE_SOURCE_DIR}/Doxyfile
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        COMMENT "Gerando documentação com Doxygen..."
        VERBATIM
    )
endif()

# Configurar testes para cada algoritmo
enable_testing()
add_test(NAME teste_programacao_dinamica 
         COMMAND run_dynamic_programming ${DIRETORIO_INSTANCIAS}/instancia_teste.txt)
add_test(NAME teste_backtracking
         COMMAND run_backtracking ${DIRETORIO_INSTANCIAS}/instancia_teste.txt)
add_test(NAME teste_branch_and_bound
         COMMAND run_branch_and_bound ${DIRETORIO_INSTANCIAS}/instancia_teste.txt)

# Mensagem informativa para diretórios utilizados
message(STATUS "Diretório de saída principal: ${DIRETORIO_SAIDA}")
message(STATUS "Diretório de instâncias: ${DIRETORIO_INSTANCIAS}")
message(STATUS "Diretório de resultados: ${DIRETORIO_RESULTADOS}")

# Adicionar definições de compilação
add_compile_definitions(
    RESULTS_DIR="${DIRETORIO_RESULTADOS}"
    INSTANCES_DIR="${DIRETORIO_INSTANCIAS}" 
    GRAPHS_DIR="${DIRETORIO_GRAFICOS}"
)