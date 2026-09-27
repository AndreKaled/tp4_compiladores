int soma_ate(int n) {
    int acc;
    acc = 0;
    while (n > 0) {
        acc += n;
        n -= 1;
    }
    return acc;
}

int main() {
    return soma_ate(100);
}
