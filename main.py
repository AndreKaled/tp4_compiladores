import sys
from antlr4 import FileStream, CommonTokenStream
from antlr4.tree.Tree import TerminalNode, ErrorNode
from miniCLexer import miniCLexer
from miniCParser import miniCParser
from SemanticVisitor import SemanticVisitor

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

    input_stream = FileStream(sys.argv[1], encoding='utf-8')
    lexer        = miniCLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser       = miniCParser(token_stream)
    tree         = parser.program()

    # aq faz a analise sintatica
    erros_sint = parser.getNumberOfSyntaxErrors()
    if erros_sint:
        print(f"   {erros_sint} erro(s) sintático(s) encontrado(s).\n")

    # arvore sintatica
    nome_arquivo = sys.argv[1]
    print(nome_arquivo)
    filhos = [tree.getChild(i) for i in range(tree.getChildCount())]
    filhos_visiveis = [f for f in filhos
                       if not (isinstance(f, TerminalNode)
                               and f.getText() in TOKENS_IGNORADOS)]
    for i, filho in enumerate(filhos_visiveis):
        eh_ultimo = (i == len(filhos_visiveis) - 1)
        imprimir_arvore(filho, parser, "", eh_ultimo)

    # aq faz a analise semantica
    print("\n Analise semântica\n")
    visitor = SemanticVisitor()
    visitor.visit(tree)

    if visitor.erros:
        print(f"\n{len(visitor.erros)} erro(s) semântico(s) encontrado(s):\n")
        for e in visitor.erros:
            print(f"    X {e}\n")
    else:
        print("\n   Nenhum erro semântico encontrado :D")


if __name__ == '__main__':
    main()