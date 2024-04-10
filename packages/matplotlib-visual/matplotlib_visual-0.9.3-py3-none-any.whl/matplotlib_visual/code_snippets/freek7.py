%{
#include <stdio.h>
int yywrap(void);
%}

%option noyywrap

%%
[ \t\n]         ; /* Ignore whitespace */
[0-9]+          { printf("NUMBER: %s\n", yytext); }
[a-zA-Z][a-zA-Z0-9]* { printf("IDENTIFIER: %s\n", yytext); }
[-+*/=()<>;, $] { printf("OPERATOR: %s\n", yytext); }
"=="            { printf("EQUAL\n"); }
"!="            { printf("NOT EQUAL\n"); }
"<="            { printf("LESS THAN OR EQUAL\n"); }
">="            { printf("GREATER THAN OR EQUAL\n"); }
.               { printf("UNKNOWN CHARACTER: %s\n", yytext); }

%%

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <input_file>\n", argv[0]);
        return 1;
    }
    yyin = fopen(argv[1], "r");
    yylex();
    fclose(yyin);
    return 0;
}
