#!/usr/bin/env python3
import sys
import re
import os

# ==============================================================================
# 1. SIMPLIFICAÇÃO DE EXPRESSÕES (Slides 7-21)
# ==============================================================================
def simplificar_expressoes(codigo):
    otimizado = []
    for linha in codigo:
        linha_str = linha.strip()
        if "=" in linha_str and not linha_str.startswith("if"):
            partes = linha_str.split("=")
            esquerda = partes[0].strip()
            direita = partes[1].strip()
            tokens = direita.split()

            if len(tokens) == 3:
                op1, operador, op2 = tokens[0], tokens[1], tokens[2]
                nova_direita = direita

                # Otimizações para '*'
                if operador == "*":
                    if op2 == "1":
                        nova_direita = op1
                    elif op1 == "1":
                        nova_direita = op2
                    elif op1 == "0" or op2 == "0":
                        nova_direita = "0"
                
                # Otimizações para '/'
                elif operador == "/":
                    if op2 == "1":
                        nova_direita = op1
                    elif op1 == "0":
                        nova_direita = "0"

                # Otimizações para '+'
                elif operador == "+":
                    if op1 == "0" and op2 == "0":
                        nova_direita = "0"
                    elif op2 == "0":
                        nova_direita = op1
                    elif op1 == "0":
                        nova_direita = op2

                # Otimizações para '-'
                elif operador == "-":
                    if op1 == "0" and op2 == "0":
                        nova_direita = "0"
                    elif op2 == "0":
                        nova_direita = op1

                # Otimizações para '&&' (caso presente nos slides)
                elif operador == "&&":
                    if op1 == "0" or op2 == "0":
                        nova_direita = "0"

                # Otimizações para '||'
                elif operador == "||":
                    if op1 == "1" or op2 == "1":
                        nova_direita = "1"

                otimizado.append(f"{esquerda} = {nova_direita}")
            else:
                otimizado.append(linha_str)
        else:
            otimizado.append(linha_str)
    return otimizado


# ==============================================================================
# 2. PROPAGAÇÃO DE CONSTANTES (Slides 22-34)
# ==============================================================================
def propagar_constantes(codigo):
    constantes = {}
    otimizado = []

    for linha in codigo:
        linha_str = linha.strip()

        # Reseta constantes em pontos de controle de fluxo complexos (funções e saltos)
        if linha_str.startswith("func ") or linha_str == "endfunc" or linha_str.endswith(":") or linha_str.startswith("goto "):
            constantes.clear()
            otimizado.append(linha_str)
            continue

        # Caso especial para comandos 'if cond goto Label' ou 'param var'
        if linha_str.startswith("if ") or linha_str.startswith("param ") or linha_str.startswith("return "):
            palavras = linha_str.split()
            novas_palavras = []
            for p in palavras:
                novas_palavras.append(constantes.get(p, p))
            otimizado.append(" ".join(novas_palavras))
            continue

        if "=" not in linha_str:
            otimizado.append(linha_str)
            continue

        partes = linha_str.split("=")
        esquerda = partes[0].strip()
        direita = partes[1].strip()
        palavras = direita.split()

        nova_direita = ""
        for palavra in palavras:
            if palavra in constantes:
                nova_direita += constantes[palavra] + " "
            else:
                nova_direita += palavra + " "
        
        nova_direita = nova_direita.strip()

        # Se for um valor constante puro (número, char lit ou booleano literal)
        if re.match(r"^('-?\d+'|-?\d+|'[a-zA-Z0-9_]'|true|false)$", nova_direita):
            constantes[esquerda] = nova_direita
        else:
            # Se a variável recebeu uma expressão não-constante, ela deixa de ser constante
            if esquerda in constantes:
                del constantes[esquerda]

        otimizado.append(f"{esquerda} = {nova_direita}")

    return otimizado


# ==============================================================================
# 3. ELIMINAÇÃO DE SUBEXPRESSÕES COMUNS (Slides 35-66)
# ==============================================================================
def eliminar_subexpressoes_comuns(codigo):
    subexpressoes = {}
    operandos_usados = {}
    otimizado = []

    for linha in codigo:
        linha_str = linha.strip()

        # Limpa tabela em rótulos e funções
        if linha_str.startswith("func ") or linha_str == "endfunc" or linha_str.endswith(":") or linha_str.startswith("goto "):
            subexpressoes.clear()
            operandos_usados.clear()
            otimizado.append(linha_str)
            continue

        if "=" in linha_str and not linha_str.startswith("if"):
            partes = linha_str.split("=")
            esquerda = partes[0].strip()
            direita = partes[1].strip()
            tokens = direita.split()

            if len(tokens) == 3:
                op1 = tokens[0]
                operador = tokens[1]
                op2 = tokens[2]
                chave = f"{op1} {operador} {op2}"

                # Verifica se a subexpressão já é conhecida e válida
                if chave in subexpressoes:
                    otimizado.append(f"{esquerda} = {subexpressoes[chave]}")
                else:
                    subexpressoes[chave] = esquerda
                    for var in [op1, op2]:
                        if var not in operandos_usados:
                            operandos_usados[var] = set()
                        operandos_usados[var].add(chave)
                    otimizado.append(linha_str)
            else:
                otimizado.append(linha_str)

            # Invalidação (Slides 55-57): se a variável da esquerda for atualizada
            if esquerda in operandos_usados:
                for chave_dependente in list(operandos_usados[esquerda]):
                    if chave_dependente in subexpressoes:
                        del subexpressoes[chave_dependente]
                del operandos_usados[esquerda]
        else:
            otimizado.append(linha_str)

    return otimizado


# ==============================================================================
# PIPELINE E LOOP ATÉ PONTO FIXO
# ==============================================================================
def otimizar(codigo):
    sequencia = [
        ("Propagação de Constantes", propagar_constantes),
        ("Simplificação de Expressões", simplificar_expressoes),
        ("Eliminação de Subexpressões Comuns", eliminar_subexpressoes_comuns)
    ]
    
    atual = [l.strip() for l in codigo if l.strip()]
    
    while True:
        anterior = list(atual)
        for _, func in sequencia:
            atual = func(atual)
        
        # Repete até que nenhuma mudança seja feita no código
        if atual == anterior:
            break

    return atual


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 otimizador.py <arquivo_entrada.ir>")
        sys.exit(1)

    arquivo_entrada = sys.argv[1]
    
    with open(arquivo_entrada, "r", encoding="utf-8") as f:
        codigo = f.readlines()

    resultado = otimizar(codigo)

    # Extrai o nome do arquivo sem a extensão original e adiciona o novo sufixo
    nome_base, _ = os.path.splitext(arquivo_entrada)
    arquivo_saida = f"{nome_base}_otimizado.ir"

    # Salva o resultado no novo arquivo e imprime no terminal
    with open(arquivo_saida, "w", encoding="utf-8") as f_out:
        for linha in resultado:
            print(linha)
            f_out.write(linha + "\n")
            
    print(f"\nArquivo gerado: {arquivo_saida}")


if __name__ == "__main__":
    main()