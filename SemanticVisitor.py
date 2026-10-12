from miniCParser import miniCParser
from miniCVisitor import miniCVisitor

class Simbolo:
    def __init__(self, nome, tipo, linha, col, funcao=False, params=None):
        self.nome = nome
        self.tipo = tipo # int | char | None (void)
        self.linha = linha
        self.col = col
        self.funcao = funcao
        self.params = params or [] # lista de tipos dos parametros

class TabelaSimbolos:
    """Pilha de escopos. o escopo 0 é global"""
    def __init__(self):
        self.escopos = [{}]

    def entrar_escopo(self):
        self.escopos.append({})

    def sair_escopo(self):
        self.escopos.pop()

    def declarar(self, simbolo: Simbolo):
        """Insere no escopo atual, retorna False se ja existir"""
        escopo_atual = self.escopos[-1]
        if simbolo.nome in escopo_atual:
            return False
        escopo_atual[simbolo.nome] = simbolo
        return True

    def buscar(self, nome: str):
        """Busca os escopos de dentro para fora"""
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return escopo[nome]
        return None

    def buscar_global(self, nome: str):
        return self.escopos[0].get(nome)

# visitor
class SemanticVisitor(miniCVisitor):

    def __init__(self):
        self.tabela = TabelaSimbolos()
        self.erros = []
        self.dentro_while = 0 # contador de alinhamento do while

    def _erro(self, token, msg):
        self.erros.append(
            f"Linha {token.line}:{token.column} — {msg}"
        )
 
    def _tipo_para_str(self, ctx_tipo):
        """Retorna 'int' ou 'char' a partir de um contexto 'tipo'"""
        if ctx_tipo is None:
            return None
        return ctx_tipo.getText()   # 'int' ou 'char'
 
    def _tipo_binary(self, ctx):
        """
        Retorna o tipo inferido de um contexto binary
        Percorre recursivamente até encontrar um terminal tipável
        Retorna 'int', 'char' ou None quando não é possível inferir
        """
        if ctx is None:
            return None
 
        tipo = type(ctx)
 
        # literais
        if isinstance(ctx, miniCParser.IntLitContext):
            return 'int'
        if isinstance(ctx, miniCParser.CharLitContext):
            return 'char'
 
        # variavel
        if isinstance(ctx, miniCParser.VarContext):
            nome = ctx.IDENTIFIER().getText()
            sim  = self.tabela.buscar(nome)
            return sim.tipo if sim else None
 
        # chamada de funcao
        if isinstance(ctx, miniCParser.FuncCallContext):
            nome = ctx.IDENTIFIER().getText()
            sim  = self.tabela.buscar(nome)
            return sim.tipo if sim else None
 
        # parenteses
        if isinstance(ctx, miniCParser.ParenContext):
            return self._tipo_binary(ctx.expression().binary())
 
        # unario, nega ou incrementa int
        if isinstance(ctx, (miniCParser.NegContext,
                             miniCParser.NotContext,
                             miniCParser.PreIncContext,
                             miniCParser.PreDecContext)):
            return 'int'
 
        # unario passthrough
        if isinstance(ctx, miniCParser.UnaryExprContext):
            return self._tipo_binary(ctx.unary())
 
        if isinstance(ctx, miniCParser.PrimaryExprContext):
            return self._tipo_binary(ctx.primary())
 
        # operacoes aritmeticas p int
        if isinstance(ctx, (miniCParser.AddContext, miniCParser.SubContext,
                             miniCParser.MulContext, miniCParser.DivContext,
                             miniCParser.ModContext)):
            return 'int'
 
        # comparacoes e logicos p int (resultado booleano)
        if isinstance(ctx, (miniCParser.EqContext,  miniCParser.NeqContext,
                             miniCParser.LtContext,  miniCParser.LeContext,
                             miniCParser.GtContext,  miniCParser.GeContext,
                             miniCParser.OrContext,  miniCParser.AndContext)):
            return 'int'
 
        # atribuicoes tipo do lado direito
        if isinstance(ctx, (miniCParser.AssignContext,
                             miniCParser.AssignAddContext,
                             miniCParser.AssignSubContext,
                             miniCParser.AssignMulContext,
                             miniCParser.AssignDivContext,
                             miniCParser.AssignModContext)):
            return self._tipo_binary(ctx.binary())
 
        return None
 
    #  programa e definicoes
    def visitProgram(self, ctx: miniCParser.ProgramContext):
        self.visitChildren(ctx)
        return self.erros
 
    def visitData_definition(self, ctx: miniCParser.Data_definitionContext):
        tipo = self._tipo_para_str(ctx.tipo())
        for decl in ctx.declarator():
            token = decl.IDENTIFIER().getSymbol()
            nome  = token.text
            sim   = Simbolo(nome, tipo, token.line, token.column)
            if not self.tabela.declarar(sim):
                self._erro(token,
                    f"Variável '{nome}' já declarada neste escopo.")
 
    def visitFunction_definition(self,
            ctx: miniCParser.Function_definitionContext):
        tipo_ret = self._tipo_para_str(ctx.tipo()) if ctx.tipo() else None
 
        header = ctx.function_header()
        token  = header.declarator().IDENTIFIER().getSymbol()
        nome   = token.text
 
        # coleta parametros
        params = []
        param_decl = (ctx.function_header()
                         .parameter_list()
                         .parameter_declaration())
        if param_decl:
            tipos  = [self._tipo_para_str(t) for t in param_decl.tipo()]
            nomes  = [d.IDENTIFIER().getText()
                      for d in param_decl.declarator()]
            params = list(zip(tipos, nomes))
 
        sim = Simbolo(nome, tipo_ret, token.line, token.column,
                      funcao=True,
                      params=[t for t, _ in params])
        if not self.tabela.declarar(sim):
            self._erro(token,
                f"Função '{nome}' já declarada.")
 
        # escopo da funcao
        self.tabela.entrar_escopo()
        for tipo_p, nome_p in params:
            # cria um token-like para o parametro
            class _Tok:
                def __init__(self, txt, ln, col):
                    self.text   = txt
                    self.line   = ln
                    self.column = col
            tok_p = _Tok(nome_p, token.line, token.column)
            sim_p = Simbolo(nome_p, tipo_p,
                            token.line, token.column)
            if not self.tabela.declarar(sim_p):
                self._erro(token,
                    f"Parâmetro '{nome_p}' duplicado em '{nome}'.")
 
        self.visit(ctx.function_body())
        self.tabela.sair_escopo()
 
    def visitFunction_body(self, ctx: miniCParser.Function_bodyContext):
        # nao abre novo escopo aqui pq já foi aberto em visitFunction_definition
        self.visitChildren(ctx)
 
    # comandos
    def visitBlockStmt(self, ctx: miniCParser.BlockStmtContext):
        self.tabela.entrar_escopo()
        self.visitChildren(ctx)
        self.tabela.sair_escopo()
 
    def visitWhileStmt(self, ctx: miniCParser.WhileStmtContext):
        self.visit(ctx.expression())
        self.dentro_while += 1
        self.visit(ctx.statement())
        self.dentro_while -= 1
 
    def visitBreakStmt(self, ctx: miniCParser.BreakStmtContext):
        if self.dentro_while == 0:
            token = ctx.start
            self._erro(token,
                "'break' fora de laço WHILE.")
 
    def visitContinueStmt(self, ctx: miniCParser.ContinueStmtContext):
        if self.dentro_while == 0:
            token = ctx.start
            self._erro(token,
                "'continue' fora de laço WHILE.")
 
    def visitIfStmt(self, ctx: miniCParser.IfStmtContext):
        self.visitChildren(ctx)
 
    def visitExprStmt(self, ctx: miniCParser.ExprStmtContext):
        self.visitChildren(ctx)
 
    def visitReturnStmt(self, ctx: miniCParser.ReturnStmtContext):
        self.visitChildren(ctx)
 
    def visitEmptyStmt(self, ctx: miniCParser.EmptyStmtContext):
        pass
 
    #  expressoes verificacoes semanticas
    def visitVar(self, ctx: miniCParser.VarContext):
        token = ctx.IDENTIFIER().getSymbol()
        nome  = token.text
        if self.tabela.buscar(nome) is None:
            self._erro(token,
                f"Variável '{nome}' não declarada.")
 
    def visitFuncCall(self, ctx: miniCParser.FuncCallContext):
        token = ctx.IDENTIFIER().getSymbol()
        nome  = token.text
        sim   = self.tabela.buscar(nome)
 
        if sim is None:
            self._erro(token,
                f"Função '{nome}' não declarada.")
            self.visitChildren(ctx)
            return
 
        if not sim.funcao:
            self._erro(token,
                f"'{nome}' não é uma função.")
            self.visitChildren(ctx)
            return
 
        # visita argumentos primeiro para checar variaveis internas
        arg_list = ctx.argument_list()
        args     = arg_list.binary() if arg_list else []
 
        for a in args:
            self.visit(a)
 
        # numero de argumentos
        if len(args) != len(sim.params):
            self._erro(token,
                f"Função '{nome}' espera {len(sim.params)} argumento(s), "
                f"mas recebeu {len(args)}.")
            return
 
        # tipos dos argumentos
        for i, (arg, tipo_esp) in enumerate(zip(args, sim.params)):
            tipo_real = self._tipo_binary(arg)
            if tipo_real is not None and tipo_real != tipo_esp:
                self._erro(token,
                    f"Argumento {i+1} de '{nome}': esperado '{tipo_esp}', "
                    f"recebido '{tipo_real}'.")
 
    def visitPreInc(self, ctx: miniCParser.PreIncContext):
        token = ctx.IDENTIFIER().getSymbol()
        if self.tabela.buscar(token.text) is None:
            self._erro(token,
                f"Variável '{token.text}' não declarada.")
 
    def visitPreDec(self, ctx: miniCParser.PreDecContext):
        token = ctx.IDENTIFIER().getSymbol()
        if self.tabela.buscar(token.text) is None:
            self._erro(token,
                f"Variável '{token.text}' não declarada.")
 
    #  atribuicoes simples q verifica variável + compatibilidade de tipo
    def _visitar_assign(self, ctx, op):
        token = ctx.IDENTIFIER().getSymbol()
        nome  = token.text
        sim   = self.tabela.buscar(nome)
 
        if sim is None:
            self._erro(token,
                f"Variável '{nome}' não declarada.")
        else:
            self.visit(ctx.binary())
            tipo_rhs = self._tipo_binary(ctx.binary())
            if tipo_rhs is not None and sim.tipo != tipo_rhs:
                self._erro(token,
                    f"Atribuição '{op}': variável '{nome}' é '{sim.tipo}', "
                    f"mas expressão é '{tipo_rhs}'.")
            # operacoes compostas aritmeticas exigem int
            if op != '=' and sim.tipo != 'int':
                self._erro(token,
                    f"Operador '{op}' requer operando do tipo 'int', "
                    f"mas '{nome}' é '{sim.tipo}'.")
        return None
 
    def visitAssign(self, ctx: miniCParser.AssignContext):
        self._visitar_assign(ctx, '=')
 
    def visitAssignAdd(self, ctx: miniCParser.AssignAddContext):
        self._visitar_assign(ctx, '+=')
 
    def visitAssignSub(self, ctx: miniCParser.AssignSubContext):
        self._visitar_assign(ctx, '-=')
 
    def visitAssignMul(self, ctx: miniCParser.AssignMulContext):
        self._visitar_assign(ctx, '*=')
 
    def visitAssignDiv(self, ctx: miniCParser.AssignDivContext):
        self._visitar_assign(ctx, '/=')
 
    def visitAssignMod(self, ctx: miniCParser.AssignModContext):
        self._visitar_assign(ctx, '%=')
 
    # operadores aritmeticos exigem int nos dois lados
    def _visitar_aritmetico(self, ctx, op):
        self.visit(ctx.binary(0))
        self.visit(ctx.binary(1))
        t0 = self._tipo_binary(ctx.binary(0))
        t1 = self._tipo_binary(ctx.binary(1))
        token = ctx.start
        if t0 is not None and t0 != 'int':
            self._erro(token,
                f"Operador '{op}': operando esquerdo deve ser 'int', "
                f"mas é '{t0}'.")
        if t1 is not None and t1 != 'int':
            self._erro(token,
                f"Operador '{op}': operando direito deve ser 'int', "
                f"mas é '{t1}'.")
 
    def visitAdd(self, ctx: miniCParser.AddContext):
        self._visitar_aritmetico(ctx, '+')
 
    def visitSub(self, ctx: miniCParser.SubContext):
        self._visitar_aritmetico(ctx, '-')
 
    def visitMul(self, ctx: miniCParser.MulContext):
        self._visitar_aritmetico(ctx, '*')
 
    def visitDiv(self, ctx: miniCParser.DivContext):
        self._visitar_aritmetico(ctx, '/')
 
    def visitMod(self, ctx: miniCParser.ModContext):
        self._visitar_aritmetico(ctx, '%')
 
    # comparacoes e logicos que apenas visitam filhos
    def visitEq(self, ctx):  self.visitChildren(ctx)
    def visitNeq(self, ctx): self.visitChildren(ctx)
    def visitLt(self, ctx):  self.visitChildren(ctx)
    def visitLe(self, ctx):  self.visitChildren(ctx)
    def visitGt(self, ctx):  self.visitChildren(ctx)
    def visitGe(self, ctx):  self.visitChildren(ctx)
    def visitOr(self, ctx):  self.visitChildren(ctx)
    def visitAnd(self, ctx): self.visitChildren(ctx)
 
    def visitNeg(self, ctx: miniCParser.NegContext):
        self.visitChildren(ctx)
 
    def visitNot(self, ctx: miniCParser.NotContext):
        self.visitChildren(ctx)
 
    def visitUnaryExpr(self, ctx: miniCParser.UnaryExprContext):
        self.visitChildren(ctx)
 
    def visitPrimaryExpr(self, ctx: miniCParser.PrimaryExprContext):
        self.visitChildren(ctx)
 
    def visitParen(self, ctx: miniCParser.ParenContext):
        self.visitChildren(ctx)
 
    def visitIntLit(self, ctx: miniCParser.IntLitContext):
        pass
 
    def visitCharLit(self, ctx: miniCParser.CharLitContext):
        pass
 