import ply.lex as lex
import ply.yacc as yacc

tokens = (
    'ID', 'INT', 'FLOAT', 'NUMBER', 'FNUMBER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'EQUALS', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'SEMICOLON', 'COMMA',
    'IF', 'ELSE', 'WHILE', 'PRINT', 'RETURN',
    'LSQUARE', 'RSQUARE',
    'EQ', 'NE', 'LT', 'GT', 'LE', 'GE'
)

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_EQUALS = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_SEMICOLON = r';'
t_COMMA = r','
t_LSQUARE = r'\['
t_RSQUARE = r'\]'
t_EQ = r'=='
t_NE = r'!='
t_LE = r'<='
t_GE = r'>='
t_LT = r'<'
t_GT = r'>'

reserved = {
    'if': 'IF', 'else': 'ELSE', 'while': 'WHILE', 'print': 'PRINT',
    'return': 'RETURN', 'int': 'INT', 'float': 'FLOAT'
}

def t_FNUMBER(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

t_ignore = ' \t\r'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_comment(t):
    r'//.*'
    pass

def t_error(t):
    print(f"Lexical error: '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

class SymbolTable:
    def __init__(self):
        self.stack = [{}]
    def push(self):
        self.stack.append({})
    def pop(self):
        self.stack.pop()
    def declare(self, name, value=None):
        self.stack[-1][name] = value
    def assign(self, name, value):
        for scope in reversed(self.stack):
            if name in scope:
                scope[name] = value
                return
        self.stack[-1][name] = value
    def lookup(self, name):
        for scope in reversed(self.stack):
            if name in scope:
                return scope[name]
        return None
    def __repr__(self):
        return str(self.stack)

symbol_table = SymbolTable()
function_table = {}
tac = []
_label = [0]
_temp = [0]

def new_label():
    _label[0] += 1
    return f"L{_label[0]}"

def new_temp():
    _temp[0] += 1
    return f"t{_temp[0]}"

class Array:
    def __init__(self, size):
        self.size = size
        self.val = [0] * size

precedence = (
    ('left','EQ','NE','LT','LE','GT','GE'),
    ('left','PLUS','MINUS'), ('left','TIMES','DIVIDE')
)

def p_program(p):
    '''program : items'''
    print("\nSYMBOL TABLE:", symbol_table)
    print("\n--- Three Address Code ---")
    for line in tac:
        print(line)

def p_items(p):
    '''items : items item
             | item'''

def p_item(p):
    '''item : decl
            | func
            | stmt'''

def p_decl(p):
    '''decl : type varlist SEMICOLON'''

def p_type(p):
    '''type : INT
            | FLOAT'''
    p[0] = p[1]

def p_varlist(p):
    '''varlist : varlist COMMA var
               | var'''

def p_var(p):
    '''var : ID
           | ID LSQUARE NUMBER RSQUARE'''
    if len(p) == 2:
        symbol_table.declare(p[1])
    else:
        symbol_table.declare(p[1], Array(p[3]))

def p_func(p):
    'func : type ID LPAREN params RPAREN LBRACE funcbody RBRACE'
    function_table[p[2]] = (p[4], p[7])
    tac.append(f"# func {p[2]}({', '.join(str(x) for x in p[4])})")

def p_params(p):
    '''params : paramlist
              | empty'''
    p[0] = p[1] if p[1] is not None else []

def p_paramlist(p):
    '''paramlist : paramlist COMMA param
                 | param'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_param(p):
    'param : type ID'
    p[0] = p[2]

def p_funcbody(p):
    '''funcbody : funcstmts func_return'''
    p[0] = (p[1], p[2])

def p_funcstmts(p):
    '''funcstmts : funcstmts stmt
                 | empty'''

def p_func_return(p):
    '''func_return : RETURN expr SEMICOLON
                  | empty'''
    if len(p) == 4:
        tac.append(f"RET {p[2]['place']}")

def p_stmt_assign(p):
    'stmt : ID EQUALS expr SEMICOLON'
    symbol_table.assign(p[1], p[3]['value'])
    tac.append(f"{p[1]} = {p[3]['place']}")

def p_stmt_assign_arr(p):
    'stmt : ID LSQUARE expr RSQUARE EQUALS expr SEMICOLON'
    arr = symbol_table.lookup(p[1])
    if not isinstance(arr, Array):
        print(f"Semantic error: '{p[1]}' not array")
    else:
        idx = p[3]['value']
        arr.val[idx] = p[6]['value']
        tac.append(f"{p[1]}[{idx}] = {p[6]['place']}")

def p_stmt_print(p):
    'stmt : PRINT LPAREN expr RPAREN SEMICOLON'
    print(f"OUTPUT: {p[3]['value']}")
    tac.append(f"print {p[3]['place']}")

def p_stmt_if_else(p):
    'stmt : IF LPAREN expr RPAREN LBRACE block RBRACE else_block'

def p_else_block(p):
    '''else_block : ELSE LBRACE block RBRACE
                  | empty'''

def p_block(p):
    '''block : stmts
             | empty'''

def p_stmts(p):
    '''stmts : stmts stmt
             | stmt'''

def p_stmt_while(p):
    'stmt : WHILE LPAREN expr RPAREN LBRACE block RBRACE'

def p_stmt_func_call(p):
    'stmt : ID LPAREN call_args RPAREN SEMICOLON'
    tac.append(f"call {p[1]}({', '.join(p[3])})")

def p_call_args(p):
    '''call_args : call_args COMMA expr
                 | expr
                 | empty'''
    if len(p) == 2 and p[1] is not None:
        p[0] = [str(p[1]['place'])]
    elif len(p) == 4:
        p[0] = p[1] + [str(p[3]['place'])]
    else:
        p[0] = []

def p_expr_binop(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIVIDE expr
            | expr EQ expr
            | expr NE expr
            | expr LT expr
            | expr GT expr
            | expr LE expr
            | expr GE expr'''
    left, right = p[1], p[3]
    temp = new_temp()
    tac.append(f"{temp} = {left['place']} {p[2]} {right['place']}")
    if p[2] == '+':
        value = left['value'] + right['value']
    elif p[2] == '-':
        value = left['value'] - right['value']
    elif p[2] == '*':
        value = left['value'] * right['value']
    elif p[2] == '/':
        value = left['value'] / right['value']
    elif p[2] == '==':
        value = int(left['value'] == right['value'])
    elif p[2] == '!=':
        value = int(left['value'] != right['value'])
    elif p[2] == '<':
        value = int(left['value'] < right['value'])
    elif p[2] == '>':
        value = int(left['value'] > right['value'])
    elif p[2] == '<=':
        value = int(left['value'] <= right['value'])
    elif p[2] == '>=':
        value = int(left['value'] >= right['value'])
    p[0] = {'place': temp, 'value': value}

def p_expr_fnumber(p):
    'expr : FNUMBER'
    p[0] = {'place': str(p[1]), 'value': p[1]}

def p_expr_number(p):
    'expr : NUMBER'
    p[0] = {'place': str(p[1]), 'value': p[1]}

def p_expr_id(p):
    'expr : ID'
    val = symbol_table.lookup(p[1])
    if val is None:
        print(f"Semantic error: '{p[1]}' used before assignment.")
        val = 0
    p[0] = {'place': p[1], 'value': val}

def p_expr_arr(p):
    'expr : ID LSQUARE expr RSQUARE'
    arr = symbol_table.lookup(p[1])
    idx = p[3]['value']
    if isinstance(arr, Array):
        v = arr.val[idx]
        nm = f"{p[1]}[{idx}]"
    else:
        print(f"Semantic error: '{p[1]}' not array.")
        v = 0
        nm = 'err'
    p[0] = {'place': nm, 'value': v}

def p_expr_func_call(p):
    'expr : ID LPAREN call_args RPAREN'
    temp = new_temp()
    tac.append(f"{temp} = call {p[1]}({', '.join(p[3])})")
    p[0] = {'place': temp, 'value': 0}

def p_empty(p):
    'empty :'

def p_error(p):
    if p:
        print(f"Syntax error at token '{p.value}', line: {p.lineno}")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()

test_code = '''
int arr[5], x, y; float f;
x = 5; y = 2; arr[1] = x + y * 2; f = 2.5;
print(arr[1]); print(f);

int sum(int a, int b) {
    int result;
    result = a + b;
    return result;
}
x = sum(x, y); print(x);

if (x == 9) { print(123); } else { print(321); }
while (x > 0) { x = x - 1; }
'''

print("--- TOKENS ---")
lexer.input(test_code)
for tok in lexer:
    print(tok)
print("\n--- PARSING ---")
parser.parse(test_code)
