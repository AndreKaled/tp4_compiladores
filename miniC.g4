grammar miniC;

program
    : definition+ EOF
    ;

definition
    : data_definition
    | function_definition
    ;

// declaracoes de dados

data_definition
    : tipo declarator (',' declarator)* ';'
    ;

declarator
    : IDENTIFIER
    ;

// tipos
tipo
    : INT
    | CHAR
    ;

// funcoes

function_definition
    : tipo? function_header function_body
    ;

function_header
    : declarator parameter_list
    ;

parameter_list
    : '(' parameter_declaration? ')'
    ;

parameter_declaration
    : tipo declarator (',' tipo declarator)*
    ;

function_body
    : '{' (data_definition | statement)* '}'
    ;

// comandos

block
    : '{' statement* '}'
    ;

statement
    : expression ';'                                        # ExprStmt
    | IF '(' expression ')' statement (ELSE statement)?    # IfStmt
    | WHILE '(' expression ')' statement                   # WhileStmt
    | BREAK ';'                                            # BreakStmt
    | CONTINUE ';'                                         # ContinueStmt
    | RETURN expression? ';'                               # ReturnStmt
    | block                                                # BlockStmt
    | ';'                                                  # EmptyStmt
    ;

// expressoes

expression
    : binary
    ;

binary
    : IDENTIFIER '='  binary                               # Assign
    | IDENTIFIER '+=' binary                               # AssignAdd
    | IDENTIFIER '-=' binary                               # AssignSub
    | IDENTIFIER '*=' binary                               # AssignMul
    | IDENTIFIER '/=' binary                               # AssignDiv
    | IDENTIFIER '%=' binary                               # AssignMod
    | binary '||' binary                                   # Or
    | binary '&&' binary                                   # And
    | binary '==' binary                                   # Eq
    | binary '!=' binary                                   # Neq
    | binary '<'  binary                                   # Lt
    | binary '<=' binary                                   # Le
    | binary '>'  binary                                   # Gt
    | binary '>=' binary                                   # Ge
    | binary '+'  binary                                   # Add
    | binary '-'  binary                                   # Sub
    | binary '*'  binary                                   # Mul
    | binary '/'  binary                                   # Div
    | binary '%'  binary                                   # Mod
    | unary                                                # UnaryExpr
    ;

unary
    : '++' IDENTIFIER                                      # PreInc
    | '--' IDENTIFIER                                      # PreDec
    | '!'  unary                                           # Not
    | '-'  unary                                           # Neg
    | primary                                              # PrimaryExpr
    ;

primary
    : IDENTIFIER '(' argument_list? ')'                    # FuncCall
    | IDENTIFIER                                           # Var
    | CONSTANT_INT                                         # IntLit
    | CONSTANT_CHAR                                        # CharLit
    | '(' expression ')'                                   # Paren
    ;

argument_list
    : binary (',' binary)*
    ;

// tokens de palavras reservadas
INT      : 'int';
CHAR     : 'char';
IF       : 'if';
ELSE     : 'else';
WHILE    : 'while';
BREAK    : 'break';
CONTINUE : 'continue';
RETURN   : 'return';

// tokens de literais e identificadores
CONSTANT_INT  : [0-9]+;
CONSTANT_CHAR : '\'' . '\'';
IDENTIFIER    : [a-zA-Z_][a-zA-Z0-9_]*;

// tokens ignorados
WS       : [ \t\r\n]+ -> skip;
COMMENT  : '//' ~[\r\n]* -> skip;
MCOMMENT : '/*' .*? '*/' -> skip;