Requirements:
Install flex
Install bison
Install mingw

lexer.l
%{
#include <stdlib.h>
#include<stdio.h>
#include <string.h>
 #include "calculator.tab.h"
%}
%%
[0-9]+		{printf("Number: %s\n",yytext); yylval.num = atoi(yytext); return NUMBER;}
[a-zA-Z]+   { printf("Variable token: %s\n", yytext); yylval.sym = strdup(yytext); return VARIABLE; }
"="             { printf("Operator:  = \n");}
"+"		{ printf("Operand: %s\n", yytext); return PLUS; }
"-"		{printf("Operand: %s\n", yytext);return MINUS;}
"*"		{printf("Operand: %s\n", yytext);return MULTIPLY;}
"/"		{printf("Operand: %s\n", yytext);return DIVIDE;}
\n 		{return EOL;}
. 		{}
%%
yywrap(){}

calculator.y
%{
	#include<stdio.h>
%}
%union{
int num;
char sym;
}
%token EOL
%token<num> NUMBER
%type<num> exp
%token PLUS MINUS MULTIPLY DIVIDE                           
%%
input:
|  line input
;
line: 
	exp 	EOL {printf("Result : %d\n", $1);} 
| 	EOL;
exp: 
NUMBER	{ $$ = $1;}
|	exp PLUS exp		{ $$ = $1 + $3;}
|	exp MINUS exp		{ $$ = $1-$3;}
|	exp MULTIPLY exp	{$$=$1*$3;}
|	exp DIVIDE exp 		{if ($3 != 0) $$=$1/$3; else yyerror("division by zero"); }
;
%%
int main(){
	printf("Enter expression: ");
	yyparse();
	return 0;
}
yyerror(char* s){
	printf("Error: %s\n", s);
	return 0;
}

To run the program:
flex lexer.l
bison -t -d calculator.y
gcc lex.yy.c calculator.tab.c
a

Output:
Enter expression: 2+3
Number: 2
Operand: +
Number: 3
Result: 5