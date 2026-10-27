from miniCParser import miniCParser
from miniCVisitor import miniCVisitor


class IRVisitor(miniCVisitor):
    """
    Gera código intermediário de três endereços a partir da árvore
    sintática do miniC, seguindo os padrões dos slides da disciplina.

    Convenções:
      - Temporários: t1, t2, t3, ...
      - Labels:      L1, L2, L3, ...
      - Parâmetros formais: p0, p1, p2, ...
      - Saída:       lista self.codigo (strings)
    """

    def __init__(self):
        self._temp_count  = 0
        self._label_count = 0
        self.codigo       = []          # linhas de código intermediário
        self._break_label    = None     # label de saída do while atual
        self._continue_label = None     # label de início do while atual

    # ---------------------------------------------------------------- #
    #  Utilitários                                                       #
    # ---------------------------------------------------------------- #

    def _novo_temp(self):
        self._temp_count += 1
        return f't{self._temp_count}'

    def _novo_label(self):
        self._label_count += 1
        return f'L{self._label_count}'

    def _emit(self, linha):
        self.codigo.append(linha)

    def codigo_str(self):
        return '\n'.join(self.codigo)

    # ---------------------------------------------------------------- #
    #  Programa e definições                                             #
    # ---------------------------------------------------------------- #

    def visitProgram(self, ctx: miniCParser.ProgramContext):
        for defn in ctx.definition():
            self.visit(defn)

    def visitDefinition(self, ctx: miniCParser.DefinitionContext):
        self.visitChildren(ctx)

    def visitData_definition(self, ctx: miniCParser.Data_definitionContext):
        # Declarações globais não geram código intermediário
        pass

    def visitFunction_definition(self,
            ctx: miniCParser.Function_definitionContext):
        header     = ctx.function_header()
        nome       = header.declarator().IDENTIFIER().getText()
        param_decl = header.parameter_list().parameter_declaration()
        n_params   = 0
        param_nomes = []

        if param_decl:
            param_nomes = [d.IDENTIFIER().getText()
                           for d in param_decl.declarator()]
            n_params    = len(param_nomes)

        self._emit(f'func {nome}, {n_params}:')

        # mapeia nome do parâmetro → p0, p1, ...
        self._params = {nome_p: f'p{i}'
                        for i, nome_p in enumerate(param_nomes)}

        self.visit(ctx.function_body())

        # garante endfunc mesmo que o return já tenha sido emitido
        self._emit('endfunc')
        self._emit('')
        self._params = {}

    def visitFunction_body(self, ctx: miniCParser.Function_bodyContext):
        self.visitChildren(ctx)

    def visitDeclarator(self, ctx: miniCParser.DeclaratorContext):
        pass  # declarações locais não geram código

    # ---------------------------------------------------------------- #
    #  Comandos                                                          #
    # ---------------------------------------------------------------- #

    def visitExprStmt(self, ctx: miniCParser.ExprStmtContext):
        self.visit(ctx.expression())

    def visitReturnStmt(self, ctx: miniCParser.ReturnStmtContext):
        if ctx.expression():
            val = self.visit(ctx.expression())
            self._emit(f'return {val}')
        else:
            self._emit('return 0')

    def visitBreakStmt(self, ctx: miniCParser.BreakStmtContext):
        if self._break_label:
            self._emit(f'goto {self._break_label}')

    def visitContinueStmt(self, ctx: miniCParser.ContinueStmtContext):
        if self._continue_label:
            self._emit(f'goto {self._continue_label}')

    def visitEmptyStmt(self, ctx: miniCParser.EmptyStmtContext):
        pass

    def visitBlockStmt(self, ctx: miniCParser.BlockStmtContext):
        self.visitChildren(ctx)

    def visitIfStmt(self, ctx: miniCParser.IfStmtContext):
        cond       = self.visit(ctx.expression())
        then_label = self._novo_label()
        end_label  = self._novo_label()
        stmts      = ctx.statement()   # [then] ou [then, else]

        if len(stmts) == 1:
            # if sem else
            self._emit(f'if {cond} goto {then_label}')
            self._emit(f'goto {end_label}')
            self._emit(f'{then_label}:')
            self.visit(stmts[0])
            self._emit(f'{end_label}:')
        else:
            # if com else
            else_label = self._novo_label()
            self._emit(f'if {cond} goto {then_label}')
            self._emit(f'goto {else_label}')
            self._emit(f'{then_label}:')
            self.visit(stmts[0])
            self._emit(f'goto {end_label}')
            self._emit(f'{else_label}:')
            self.visit(stmts[1])
            self._emit(f'{end_label}:')

    def visitWhileStmt(self, ctx: miniCParser.WhileStmtContext):
        start_label  = self._novo_label()
        body_label   = self._novo_label()
        end_label    = self._novo_label()

        # salva labels anteriores para aninhamento
        old_break    = self._break_label
        old_continue = self._continue_label
        self._break_label    = end_label
        self._continue_label = start_label

        self._emit(f'{start_label}:')
        cond = self.visit(ctx.expression())
        self._emit(f'if {cond} goto {body_label}')
        self._emit(f'goto {end_label}')
        self._emit(f'{body_label}:')
        self.visit(ctx.statement())
        self._emit(f'goto {start_label}')
        self._emit(f'{end_label}:')

        # restaura labels
        self._break_label    = old_break
        self._continue_label = old_continue

    # ---------------------------------------------------------------- #
    #  Expressões — todas retornam o nome do temporário ou lexema        #
    # ---------------------------------------------------------------- #

    def visitExpression(self, ctx: miniCParser.ExpressionContext):
        return self.visit(ctx.binary())

    # Atribuição simples
    def visitAssign(self, ctx: miniCParser.AssignContext):
        nome = ctx.IDENTIFIER().getText()
        # se for parâmetro formal, usa o alias p0, p1, ...
        lhs  = self._params.get(nome, nome)
        rhs  = self.visit(ctx.binary())
        self._emit(f'{lhs} = {rhs}')
        return lhs

    # Atribuições compostas: expandidas em operação + atribuição
    def _assign_composto(self, ctx, op):
        nome = ctx.IDENTIFIER().getText()
        lhs  = self._params.get(nome, nome)
        rhs  = self.visit(ctx.binary())
        tmp  = self._novo_temp()
        self._emit(f'{tmp} = {lhs} {op} {rhs}')
        self._emit(f'{lhs} = {tmp}')
        return lhs

    def visitAssignAdd(self, ctx: miniCParser.AssignAddContext):
        return self._assign_composto(ctx, '+')

    def visitAssignSub(self, ctx: miniCParser.AssignSubContext):
        return self._assign_composto(ctx, '-')

    def visitAssignMul(self, ctx: miniCParser.AssignMulContext):
        return self._assign_composto(ctx, '*')

    def visitAssignDiv(self, ctx: miniCParser.AssignDivContext):
        return self._assign_composto(ctx, '/')

    def visitAssignMod(self, ctx: miniCParser.AssignModContext):
        return self._assign_composto(ctx, '%')

    # Operações binárias genéricas
    def _binary_op(self, ctx, op=None):
        left  = self.visit(ctx.binary(0))
        right = self.visit(ctx.binary(1))
        if op is None:
            op = ctx.getChild(1).getText()
        tmp = self._novo_temp()
        self._emit(f'{tmp} = {left} {op} {right}')
        return tmp

    def visitOr(self, ctx):   return self._binary_op(ctx, '||')
    def visitAnd(self, ctx):  return self._binary_op(ctx, '&&')
    def visitEq(self, ctx):   return self._binary_op(ctx, '==')
    def visitNeq(self, ctx):  return self._binary_op(ctx, '!=')
    def visitLt(self, ctx):   return self._binary_op(ctx, '<')
    def visitLe(self, ctx):   return self._binary_op(ctx, '<=')
    def visitGt(self, ctx):   return self._binary_op(ctx, '>')
    def visitGe(self, ctx):   return self._binary_op(ctx, '>=')
    def visitAdd(self, ctx):  return self._binary_op(ctx, '+')
    def visitSub(self, ctx):  return self._binary_op(ctx, '-')
    def visitMul(self, ctx):  return self._binary_op(ctx, '*')
    def visitDiv(self, ctx):  return self._binary_op(ctx, '/')
    def visitMod(self, ctx):  return self._binary_op(ctx, '%')

    # Unários
    def visitUnaryExpr(self, ctx: miniCParser.UnaryExprContext):
        return self.visit(ctx.unary())

    def visitPrimaryExpr(self, ctx: miniCParser.PrimaryExprContext):
        return self.visit(ctx.primary())

    def visitNeg(self, ctx: miniCParser.NegContext):
        val = self.visit(ctx.unary())
        tmp = self._novo_temp()
        self._emit(f'{tmp} = -{val}')
        return tmp

    def visitNot(self, ctx: miniCParser.NotContext):
        val = self.visit(ctx.unary())
        tmp = self._novo_temp()
        self._emit(f'{tmp} = !{val}')
        return tmp

    def visitPreInc(self, ctx: miniCParser.PreIncContext):
        nome = ctx.IDENTIFIER().getText()
        var  = self._params.get(nome, nome)
        tmp  = self._novo_temp()
        self._emit(f'{tmp} = {var} + 1')
        self._emit(f'{var} = {tmp}')
        return var

    def visitPreDec(self, ctx: miniCParser.PreDecContext):
        nome = ctx.IDENTIFIER().getText()
        var  = self._params.get(nome, nome)
        tmp  = self._novo_temp()
        self._emit(f'{tmp} = {var} - 1')
        self._emit(f'{var} = {tmp}')
        return var

    # Primários
    def visitVar(self, ctx: miniCParser.VarContext):
        nome = ctx.IDENTIFIER().getText()
        return self._params.get(nome, nome)

    def visitIntLit(self, ctx: miniCParser.IntLitContext):
        return ctx.CONSTANT_INT().getText()

    def visitCharLit(self, ctx: miniCParser.CharLitContext):
        return ctx.CONSTANT_CHAR().getText()

    def visitParen(self, ctx: miniCParser.ParenContext):
        return self.visit(ctx.expression())

    def visitFuncCall(self, ctx: miniCParser.FuncCallContext):
        nome     = ctx.IDENTIFIER().getText()
        arg_list = ctx.argument_list()
        args     = arg_list.binary() if arg_list else []

        # avalia e emite cada argumento
        vals = [self.visit(a) for a in args]
        for v in vals:
            self._emit(f'param {v}')

        tmp = self._novo_temp()
        self._emit(f'{tmp} = call {nome}, {len(args)}')
        return tmp