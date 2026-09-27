int procurar(int limite, int alvo) {
    int i;
    i = 0;
    while (i < limite) {
        if (i == alvo) {
            break;
        }
        i += 1;
    }
    return i;
}

int main() {
    return procurar(100, 42);
}
