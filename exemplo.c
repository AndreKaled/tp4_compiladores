int x, y;

int soma(int a, int b) {
    return a + b;
}

int fatorial(int n) {
    int resultado;
    resultado = 1;
    while (n > 1) {
        resultado *= n;
        n -= 1;
    }
    return resultado;
}

int main() {
    int a, b, s;
    a = 3;
    b = 4;
    s = soma(a, b);
    if (s > 5) {
        x = fatorial(s);
    } else {
        x = 0;
    }
    return x;
}