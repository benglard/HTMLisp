################ Lispy: Scheme Interpreter in Python

## (c) Peter Norvig, 2010; See http://norvig.com/lispy.html

################ Symbol, Env classes

from __future__ import division
from sys import argv, exit

Symbol = str

class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms,args))
        self.outer = outer
    def find(self, var):
        "Find the innermost Env where var appears."
        return self if var in self else self.outer.find(var)

def add_globals(env):
    "Add some Scheme standard procedures to an environment."
    import math, operator as op
    env.update(vars(math)) # sin, sqrt, ...
    env.update(
     {'+':op.add, '-':op.sub, '*':op.mul, '/':op.div, 'not':op.not_,
      '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq, 
      'equal?':op.eq, 'eq?':op.is_, 'length':len, 'cons':lambda x,y:[x]+y,
      'car':lambda x:x[0],'cdr':lambda x:x[1:], 'append':op.add,  
      'list':lambda *x:list(x), 'list?': lambda x:isa(x,list), 
      'null?':lambda x:x==[], 'symbol?':lambda x: isa(x, Symbol)})
    return env

global_env = add_globals(Env())

isa = isinstance

html = ''
html_tags = [
    'html', 'head', 'body', 'link', 'script', 'p', 'img',
    'b', 'i', 'strong', 'video', 'audio', 'h1', 'h2', 'h3',
    'h4', 'h5', 'h6', 'div'
]
html_tags_only_1 = ['img']

################ eval

def eval(x, env=global_env, html=html):

    "Evaluate an expression in an environment."
    if isa(x, Symbol):             # variable reference
        return env.find(x)[x]
    elif not isa(x, list):         # constant literal
        return x
    elif x[0] == 'quote':          # (quote exp)
        (_, exp) = x
        return exp
    elif x[0] == 'if':             # (if test conseq alt)
        (_, test, conseq, alt) = x
        return eval((conseq if eval(test, env) else alt), env)
    elif x[0] == 'set!':           # (set! var exp)
        (_, var, exp) = x
        env.find(var)[var] = eval(exp, env)
    elif x[0] == 'define':         # (define var exp)
        (_, var, exp) = x
        env[var] = eval(exp, env)
    elif x[0] == 'lambda':         # (lambda (var*) exp)
        (_, vars, exp) = x
        return lambda *args: eval(exp, Env(vars, args, env))
    elif x[0] == 'begin':          # (begin exp*)
        for exp in x[1:]:
            val = eval(exp, env)
        return val
    elif x[0] in html_tags:        # (p class="..." id="..." inner="...", ...)        
        props = ''
        for elem in x[1:]:
            if type(elem) == list:
                html = '{}{}'.format(html, eval(elem, env))
            if type(elem) == str:
                key, value = elem.split('=')
                props = '{} {}="{}"'.format(props, key, value)

        open_tag = '<{}{}>'.format(x[0], props)
        close_tag = '' if x[0] in html_tags_only_1 else '</{}>'.format(x[0])
        full_tag = '{}{}{}'.format(open_tag, html, close_tag)
        return full_tag
    elif isa(x, list) and len(x) == 1 and isa(x[0], Symbol): # (x)
        elem = x[0]
        return env.find(elem)[elem]
    else:                          # (proc exp*)
        exps = [eval(exp, env) for exp in x]
        proc = exps.pop(0)
        return proc(*exps)

################ parse, read, and user interaction

def read(s):
    "Read a Scheme expression from a string."
    return read_from(tokenize(s))

parse = read

def tokenize(s):
    "Convert a string into a list of tokens."
    return s.replace('(',' ( ').replace(')',' ) ').split()

def read_from(tokens):
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from(tokens))
        tokens.pop(0) # pop off ')'
        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token):
    "Numbers become numbers; every other token is a symbol."
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)

def to_string(exp):
    "Convert a Python object back into a Lisp-readable string."
    return '('+' '.join(map(to_string, exp))+')' if isa(exp, list) else str(exp)

def repl(prompt='lis.py> '):
    "A prompt-read-eval-print loop."
    while True:
        try:
            line = raw_input(prompt)
            val = eval(parse(line))
            if val is not None: print to_string(val)
        except EOFError:
            print ''
            exit(1)

def interpret(path):
    with open(path, 'r') as f:
        code = ''.join(line.replace('\n', '').replace('\t', ' ') for line in f.read())
        for line in code.split(';'):
            if line:
                val = eval(parse(line))
                if val is not None: print to_string(val)

def main():
    if '-f' in argv: 
        try: interpret(argv[2])     
        except Exception, e:
            print str(e)
            exit(1)
    else:
        repl()

main()