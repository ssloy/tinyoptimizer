int fib(int n) {
    int a = 0;
    int b = 1;
    int c = 0;
    int i = 1;
    if (n == 0) return 0;
    while (i < n) {
        c = b;
        b = a + b;
        a = c;
        i = i + 1;
    }
    return b;
}
