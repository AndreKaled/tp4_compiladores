// teste3_while.c — while, break, continue e while aninhado

int fatorial(int n) {
    int i;
    int fat;
    i = 1;
    fat = 1;
    while (i <= n) {
        fat = fat * i;
        i = i + 1;
    }
    return fat;
}

int main() {
    int a;
    int b;
    int c;
    a = 5;
    b = 10;

    while (a < b) {
        a = a + 1;
        if (a == 7) {
            continue;
        }
        if (a == 9) {
            break;
        }
        b = b - 1;
    }

    // while aninhado
    while (a > 0) {
        while (b > 0) {
            b = b - 1;
            if (b == 1) {
                break;
            }
        }
        a = a - 1;
    }

    c = fatorial(5);
    return c;
}
