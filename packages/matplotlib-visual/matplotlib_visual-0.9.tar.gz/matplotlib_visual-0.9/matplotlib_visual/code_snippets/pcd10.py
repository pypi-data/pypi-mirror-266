#Requirements:
#Pip install ply

#Code:
import ply.lex as lex
import ply.yacc as yacc
tokens = (
    'NUMBER',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
)
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_ignore = ' \t'
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
lexer = lex.lex()
def p_expression_plus(p):
    'expression : expression PLUS term'
    p[0] = p[1] + p[3]
def p_expression_minus(p):
    'expression : expression MINUS term'
    p[0] = p[1] - p[3]
def p_expression_term(p):
    'expression : term'
    p[0] = p[1]
def p_term_times(p):
    'term : term TIMES factor'
    p[0] = p[1] * p[3]
def p_term_divide(p):
    'term : term DIVIDE factor'
    p[0] = p[1] / p[3]
def p_term_factor(p):
    'term : factor'
    p[0] = p[1]
def p_factor_num(p):
    'factor : NUMBER'
    p[0] = p[1]
def p_factor_expr(p):
    'factor : LPAREN expression RPAREN'
    p[0] = p[2]
def p_error(p):
    print("Syntax error")
parser = yacc.yacc()
while True:
    try:
        s = input('calc > ')
    except EOFError:
        break
    if not s:
        continue
    result = parser.parse(s)
    print(result)

#Output:
#calc > 1+2*3
#7
#calc > 3-2*!
#Illegal character '!'
#Syntax error
#None