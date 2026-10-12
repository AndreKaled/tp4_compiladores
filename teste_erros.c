// teste_erros.c — cobre todos os erros semanticos pedidos no trabalho

int global;

// funcao auxiliar correta usada nos testes abaixo
int soma(int a, int b) {
    return a + b;
}

char echo(char c) {
    return c;
}

// (b) funcao declarada duas vezes
int soma(int x) {
    return x;
}

int main() {
    int n;
    char letra;

    // (b) variavel declarada duas vezes no mesmo escopo
    int n;

    // (a) variavel nao declarada — z nunca foi declarada
    z = 5;

    // (a) uso de variavel nao declarada em expressao
    n = z + 1;

    // correto para comparar com os erros abaixo
    n = soma(3, 4);

    // (c) numero errado de argumentos — soma espera 2, recebe 1
    n = soma(1);

    // (c) numero errado de argumentos — soma espera 2, recebe 3
    n = soma(1, 2, 3);

    // (d) tipo errado no argumento — soma espera int, recebe char
    n = soma('a', 3);

    // (d) tipo errado no argumento — echo espera char, recebe int
    letra = echo(42);

    // (e) atribuicao de char em variavel int
    n = 'b';

    // (e) atribuicao de int em variavel char
    letra = 99;

    // (e) atribuicao composta com tipos incompativeis
    n += letra;

    // (f) operador aritmetico + com char no lado esquerdo
    n = letra + 1;

    // (f) operador aritmetico * com char nos dois lados
    n = letra * letra;

    // (f) operador aritmetico % com char
    n = letra % n;

    // (g) break fora de while
    break;

    // (g) continue fora de while
    continue;

    // break e continue corretos dentro de while (sem erro)
    while (n > 0) {
        n -= 1;
        break;
        continue;
    }

    // (g) break dentro de if mas fora de while — ainda eh erro
    if (n == 0) {
        break;
    }

    return 0;
}
