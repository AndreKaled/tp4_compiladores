// teste4_char_logico.c — char, atribuicoes compostas e operadores logicos

char echo(char c) {
    return c;
}

int processar(int n, char ch) {
    int resultado;
    resultado = n + 1;
    return resultado;
}

int main() {
    int a;
    int b;
    int c;
    char d;
    char e;

    a = 10;
    b = 3;
    d = 'x';

    // atribuicoes compostas
    a *= 2;
    b += 5;
    a -= 1;
    b /= 2;
    a %= 7;

    // operadores logicos e relacionais
    if (a > 0 && b < 10) {
        c = 1;
    }
    if (a == 0 || b != 3) {
        c = 2;
    }

    // chamadas com char
    e = echo(d);
    c = processar(a, d);

    return c;
}
