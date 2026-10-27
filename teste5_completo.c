// teste5_completo.c — programa completo integrando todos os recursos

int global;

int soma(int a, int b) {
    return a + b;
}

int fatorial(int n) {
    int resultado;
    int i;
    resultado = 1;
    i = 1;
    while (i <= n) {
        resultado = resultado * i;
        i = i + 1;
    }
    return resultado;
}

int busca(int n, int alvo) {
    int i;
    i = 0;
    while (i < n) {
        if (i == alvo) {
            break;
        }
        i = i + 1;
    }
    return i;
}

char trocar(char c) {
    return c;
}

int main() {
    int a;
    int b;
    int c;
    char letra;

    a = 5;
    b = 3;
    letra = 'k';

    c = soma(a, b);
    c = fatorial(c);
    c = busca(c, 10);

    a *= 2;
    b += a;
    c = a + b * 2;

    if (c > 100) {
        c = 100;
    } else {
        if (c < 0) {
            c = 0;
        }
    }

    while (a > 0 && b > 0) {
        a = a - 1;
        b = b - 1;
        if (a == b) {
            continue;
        }
    }

    global = c;
    letra = trocar(letra);

    return c;
}
