## Simulador de Resolução de Equações Algébricas e Transcendentes

Trabalho prático da disciplina de Cálculo Numérico (Unidade 1 - Zeros) - 2026.2.
Universidade Federal do Vale do São Francisco (UNIVASF).

## Sobre o Projeto

Este projeto é um simulador desenvolvido em Python para encontrar raízes de equações algébricas e transcendentes. O objetivo principal é conectar a teoria à prática, analisando e comparando a eficiência, o número de iterações e o tempo de execução de quatro métodos numéricos:

Bissecção

Falsa Posição

Newton-Raphson

Secante

## Estrutura do Código

O sistema foi modularizado em três partes para facilitar o trabalho em equipe:

metodos_intervalo.py: Algoritmos que dependem de um intervalo inicial (Bissecção e Falsa Posição).

metodos_abertos.py: Algoritmos que utilizam estimativas iniciais e derivadas (Newton-Raphson e Secante).

main.py: Motor do programa que une os métodos, apresenta o menu interativo ao usuário, realiza a medição de tempo e plota os gráficos comparativos.

## Pré-requisitos e Execução

Certifique-se de ter o Python 3 instalado em sua máquina.

Para que a plotagem dos gráficos funcione corretamente, instale a biblioteca matplotlib rodando o comando abaixo no seu terminal:

pip install matplotlib

Para iniciar o simulador, navegue até a pasta do projeto e execute o arquivo principal:

python main.py

## Discentes

| Nome |
|------|
| **DERIK ALEXANDRE** |
| **JOÃO GABRIEL** |
| **LUCAS EMANOEL** | 
---