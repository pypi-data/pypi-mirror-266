#include <stdio.h>
#include <string.h>
#include <ctype.h>

void identifyToken(char *token) {
    if (strpbrk(token, "+-*/=")) printf("Operator : %s\n", token);
    else if (isdigit(token[0]) || (token[0] == '-' && isdigit(token[1]))) printf("Constants : %s\n", token);
    else if (isalpha(token[0]) || token[0] == '_') printf("Identifier : %s\n", token);
    else if (isalpha(token[0])) printf("Keywords : %s\n", token);
    else printf("Special Character : %s\n", token);
}

void displayToken(char *paragraph) {
    int j = 0;
    for (char *token = strtok(paragraph, "\t \n"); token != NULL; token = strtok(NULL, "\t \n"), j++)
        identifyToken(token);
    printf("\nNumber of tokens : %d", j);
}

int main() {
    char paragraph[1000];
    printf("Enter the paragraph: ");
    fgets(paragraph, sizeof(paragraph), stdin);
    printf("\nToken with types: \n");
    displayToken(paragraph);
    return 0;
}
