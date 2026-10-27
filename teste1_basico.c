// teste1_basico.c — atribuicoes e operacoes aritmeticas basicas

int soma(int a, int b) {
    int c;
    c = a + b;
    return c;
}

int mult(int a, int b, int c) {
    int d;
    d = a * b * c;
    return d;
}

int main() {
    int x;
    int y;
    int z;
    x = 10;
    y = 3;
    z = soma(x, y);
    z = mult(x, y, z);
    return z;
}
