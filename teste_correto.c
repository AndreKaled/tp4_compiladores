// teste_correto.c — programa sem erros semanticos

int global;
char letra_global;

// funcao com retorno char e parametro char
char echo(char c) {
    return c;
}

// funcao com dois parametros int
int soma(int a, int b) {
    return a + b;
}

// funcao com parametros mistos
int processar(int n, char ch) {
    int resultado;
    resultado = n + 1;
    return resultado;
}

// funcao sem parametros
int fatorial(int n) {
    int resultado;
    resultado = 1;
    while (n > 1) {
        resultado *= n;
        n -= 1;
        if (n == 2) {
            continue;
        }
    }
    return resultado;
}

// funcao principal
int main() {
    int a;
    int b;
    int c;
    char d;
    char e;

    // atribuicoes corretas
    a = 10;
    b = 3;
    d = 'x';
    e = 'z';

    // operacoes aritmeticas com int
    c = a + b;
    c = a - b;
    c = a * b;
    c = a / b;
    c = a % b;

    // atribuicoes compostas com int
    a *= 2;
    b += 5;
    c -= 1;
    a /= 2;
    b %= 3;

    // chamadas de funcao corretas
    c  = soma(a, b);
    c  = fatorial(5);
    c  = processar(a, d);
    e  = echo(d);

    // estruturas de controle
    if (a > b) {
        c = a;
    } else {
        c = b;
    }

    // while com break e continue no lugar certo
    while (c > 0) {
        c -= 1;
        if (c == 5) {
            break;
        }
        if (c == 3) {
            continue;
        }
    }

    // while aninhado
    while (a > 0) {
        while (b > 0) {
            b -= 1;
            if (b == 1) {
                break;
            }
        }
        a -= 1;
    }

    // operadores logicos e relacionais
    if (a == 0 && b != 0) {
        c = 1;
    }
    if (a > 0 || b < 10) {
        c = 2;
    }

    // numero negativo
    c = -a;

    // variavel global
    global = c;

    return 0;
}
