#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>

int main() {
    char symbol;
    int symbol_count = 0;
    printf("Expression terminated by $: ");
    while ((symbol = getchar()) != '$') {
        if (symbol != ' ' && symbol != '\n') {
            const char *type = isalpha(symbol) ? "identifier" : (isdigit(symbol) ? "number" : "operator");
            printf("%c \t %p \t %s\n", symbol, (void *)malloc(sizeof(char)), type);
            symbol_count++;
        }
    }
    printf("Symbol Table\n");
    printf("Symbol \t addr \t type\n");
    printf("Total Symbols: %d\n", symbol_count);
    return 0;
}
