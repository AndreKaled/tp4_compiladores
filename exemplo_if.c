int max(int a, int b) {
    if (a > b) {
        return a;
    } else {
        return b;
    }
}

int abs_val(int x) {
    if (x < 0) {
        return x * -1;
    }
    return x;
}

int main() {
    int r;
    r = max(3, 7);
    return r;
}
