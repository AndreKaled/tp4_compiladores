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
    : INT declarator (',' declarator)* ';'
    ;

declarator
    : IDENTIFIER
    ;

// funcoes

function_definition
    : INT? function_header function_body
    ;

function_header
    : declarator parameter_list
    ;

parameter_list
    : '(' parameter_declaration? ')'
    ;

parameter_declaration
    : INT declarator (',' INT declarator)*
    ;

function_body
    : '{' (data_definition | statement)* '}'
    ;

// comandos

block
    : '{' statement* '}'
    ;

statement
    : expression ';'
    | IF '(' expression ')' statement (ELSE statement)?
    | WHILE '(' expression ')' statement
    | BREAK ';'
    | CONTINUE ';'
    | RETURN expression? ';'
    | block
    | ';'
    ;

// expressoes

expression
    : binary
    ;

binary
    : IDENTIFIER '=' binary
    | IDENTIFIER '+=' binary
    | IDENTIFIER '-=' binary
    | IDENTIFIER '*=' binary
    | IDENTIFIER '/=' binary
    | IDENTIFIER '%=' binary
    | binary '||' binary
    | binary '&&' binary
    | binary '==' binary
    | binary '!=' binary
    | binary '<' binary
    | binary '<=' binary
    | binary '>' binary
    | binary '>=' binary
    | binary '+' binary
    | binary '-' binary
    | binary '*' binary
    | binary '/' binary
    | binary '%' binary
    | unary
    ;

unary
    : '++' IDENTIFIER
    | '--' IDENTIFIER
    | '!' unary
    | '-' unary
    | primary
    ;

primary
    : IDENTIFIER '(' argument_list? ')'
    | IDENTIFIER
    | CONSTANT_INT
    | '(' expression ')'
    ;

argument_list
    : binary (',' binary)*
    ;

//tokens de palavras reservadas
INT     : 'int'; 
IF      : 'if';
ELSE    : 'else';
WHILE   : 'while';
BREAK   : 'break';
CONTINUE: 'continue';
RETURN  : 'return';

//tokens de literais e identificadores
CONSTANT_INT    : [0-9]+;
IDENTIFIER      : [a-zA-Z_][a-zA-Z0-9_]*;

//tokens ignorados
WS      : [ \t\r\n]+ -> skip;
COMMENT : '//' ~[\r\n]* -> skip;
MCOMMENT: '/*' .*? '*/' -> skip;