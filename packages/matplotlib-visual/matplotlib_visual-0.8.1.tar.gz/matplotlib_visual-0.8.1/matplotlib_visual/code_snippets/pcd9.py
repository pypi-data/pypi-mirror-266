#Requiremnts:
#Install javacc 6

#Lexer.jj
options {
    STATIC = false; 
}
PARSER_BEGIN(Lexer)
public class Lexer {
    public static void main(String[] args) {
        Lexer lexer = new Lexer(System.in);
        Token token;
        do {
            token = lexer.getNextToken();
            System.out.println("Token: " + token);
        } while (token.kind != 0);
    }
}

PARSER_END(Lexer)
SKIP: {
    " " | "\r" | "\n" | "\t" // Skip whitespace characters
}
TOKEN: {
    <NUMBER : (["0"-"9"])+ > // Define a token for numbers
|   <IDENTIFIER : (["a"-"z","A"-"Z"])+ > // Define a token for identifiers
|   <ASSIGN : "=" > // Define a token for the assignment operator
|   <PLUS : "+" > // Define a token for the addition operator
|   <SEMICOLON : ";" >
}

Parser.jj
options {
    STATIC = false; 
}
PARSER_BEGIN(Parser)
import java.io.*;
public class Parser {
    public static void main(String[] args) {
        try {
            Parser parser = new Parser(System.in);
            parser.Start();
        } catch (ParseException e) {
            System.err.println("Syntax error: " + e.getMessage());
        }
    }
}
PARSER_END(Parser)
SKIP: {
    " " | "\r" | "\n" | "\t" // Skip whitespace characters
}
TOKEN: {
    <NUMBER : (["0"-"9"])+ > // Define a token for numbers
|   <IDENTIFIER : (["a"-"z","A"-"Z"])+ > // Define a token for identifiers
|   <ASSIGN : "=" > // Define a token for the assignment operator
|   <PLUS : "+" > // Define a token for the addition operator
|   <SEMICOLON : ";" > // Define a token for the semicolon
}
void Start():
{}
{
   ( Statement())*
    <EOF>
}
void Statement():
{}
{
    <IDENTIFIER> "=" Expression() ";"
}
void Expression():
{}
{
    Term() ( "+" Term() )*
}
void Term():
{}
{
    <IDENTIFIER> | <NUMBER>
}

Input.txt
x = 10 ;
y = 20 ;

To run the program:
javacc Lexer.jj
javacc Parser.jj
javac Lexer.java Parser.java
java Lexer < input.txt

Output:
Token: x
Token: =
Token: 10
Token: ;
Token: y
Token: =
Token: 20
Token: ;