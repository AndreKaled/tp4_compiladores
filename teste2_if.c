// teste2_if.c — estruturas if/else simples e aninhadas

int max(int a, int b) {
    int r;
    if (a > b) {
        r = a;
    } else {
        r = b;
    }
    return r;
}

int classificar(int n) {
    int resultado;
    if (n > 0) {
        resultado = 1;
    } else {
        if (n == 0) {
            resultado = 0;
        } else {
            resultado = -1;
        }
    }
    return resultado;
}

int main() {
    int a;
    int b;
    int r;
    a = 5;
    b = 10;
    if (a < b) {
        r = a + 1;
    }
    r = max(a, b);
    r = classificar(r);
    return r;
}
