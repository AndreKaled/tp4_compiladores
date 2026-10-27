import sys
import os
from antlr4 import FileStream, CommonTokenStream
from antlr4.tree.Tree import TerminalNode, ErrorNode
from miniCLexer import miniCLexer
from miniCParser import miniCParser
from SemanticVisitor import SemanticVisitor
from IRVisitor import IRVisitor

TOKENS_IGNORADOS = {'<EOF>'}


def imprimir_arvore(node, parser, prefix="", ultimo=True):
    conector = "└── " if ultimo else "├── "
    extensao = "    " if ultimo else "│   "
    if isinstance(node, ErrorNode):
        print(f"{prefix}{conector}⚠ {node.getText()!r}")
        return
    if isinstance(node, TerminalNode):
        texto = node.getText()
        if texto not in TOKENS_IGNORADOS:
            print(f"{prefix}{conector}{texto!r}")
        return
    nome = miniCParser.ruleNames[node.getRuleIndex()]
    filhos = [node.getChild(i) for i in range(node.getChildCount())]
    filhos_visiveis = [f for f in filhos
                       if not (isinstance(f, TerminalNode)
                               and f.getText() in TOKENS_IGNORADOS)]
    print(f"{prefix}{conector}[{nome}]")
    for i, filho in enumerate(filhos_visiveis):
        eh_ultimo = (i == len(filhos_visiveis) - 1)
        imprimir_arvore(filho, parser, prefix + extensao, eh_ultimo)


def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo.c>", file=sys.stderr)
        sys.exit(1)

    arquivo_entrada = sys.argv[1]

    input_stream = FileStream(arquivo_entrada, encoding='utf-8')
    lexer        = miniCLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser       = miniCParser(token_stream)
    tree         = parser.program()

    # ── Análise sintática ──────────────────────────────────────────── #
    erros_sint = parser.getNumberOfSyntaxErrors()
    if erros_sint:
        print(f"   {erros_sint} erro(s) sintático(s) encontrado(s).\n")

    # ── Árvore sintática ───────────────────────────────────────────── #
    print(arquivo_entrada)
    filhos = [tree.getChild(i) for i in range(tree.getChildCount())]
    filhos_visiveis = [f for f in filhos
                       if not (isinstance(f, TerminalNode)
                               and f.getText() in TOKENS_IGNORADOS)]
    for i, filho in enumerate(filhos_visiveis):
        eh_ultimo = (i == len(filhos_visiveis) - 1)
        imprimir_arvore(filho, parser, "", eh_ultimo)

    # ── Análise semântica ──────────────────────────────────────────── #
    print("\n── Análise semântica ──────────────────────────────────────")
    sem = SemanticVisitor()
    sem.visit(tree)

    if sem.erros:
        print(f"\n{len(sem.erros)} erro(s) semântico(s) encontrado(s):\n")
        for e in sem.erros:
            print(f"    X {e}")
        print("\nGeração de código intermediário abortada.")
        sys.exit(1)

    print("   Nenhum erro semântico encontrado :D")

    # ── Geração de código intermediário ───────────────────────────── #
    print("\n── Código intermediário (três endereços) ──────────────────")
    ir = IRVisitor()
    ir.visit(tree)

    codigo = ir.codigo_str()
    print(codigo)

    # salva em arquivo .ir ao lado do .c
    base        = os.path.splitext(arquivo_entrada)[0]
    arquivo_ir  = base + '.ir'
    with open(arquivo_ir, 'w', encoding='utf-8') as f:
        f.write(codigo + '\n')

    print(f"\nArquivo gerado: {arquivo_ir}")


if __name__ == '__main__':
    main()