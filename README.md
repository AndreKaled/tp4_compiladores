# TP4 — Análise Sintática: Gramática miniC

Trabalho da disciplina de Compiladores, desenvolvido para implementar um analisador léxico e sintático para a linguagem **miniC** utilizando **ANTLR 4** e **Python**.

## Sobre o trabalho

O analisador reconhece programas escritos em miniC, uma linguagem simplificada com:

* Tipo de dado inteiro (`int`)
* Funções com número arbitrário de parâmetros
* Variáveis globais e locais
* Estruturas de controle: `if`/`else` e `while`
* Comandos: `break`, `continue`, `return`
* Operadores aritméticos, relacionais e de atribuição composta
* Chamadas de função e pré-incremento/decremento (`++`, `--`)
* Comentários de linha (`//`) e bloco (`/* */`)

Ao executar, o programa imprime a árvore de análise sintática (parse tree) do arquivo de entrada.

## Tecnologias

* Python 3.12
* ANTLR 4.13.2
* Docker

## Como executar

É necessário ter o Docker e o Docker Compose instalados.

Primeiro, construa a imagem:

```bash
docker compose build
```

Depois, execute o programa passando um arquivo miniC como argumento:

```bash
docker compose run --rm antlr exemplo.c
```

A gramática `miniC.g4` é reprocessada automaticamente a cada execução.


## Estrutura

```text
.
├── Dockerfile
├── docker-compose.yml
├── miniC.g4
├── main.py
├── exemplo.c
└── README.md
```

Os arquivos `miniC.g4` e `main.py` correspondem aos arquivos exigidos para a entrega do trabalho.