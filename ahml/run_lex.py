from . import token_rules
import sys, re
from ply import lex

lexer = lex.lex(module=token_rules, reflags=re.MULTILINE)
lexer.input(open(sys.argv[1], 'r').read())

line = []
for i in lexer:
    if (i.type == "NEWLINE"):
        line.append("NEWLINE")
        print(' '.join(line))
        line = []
    elif (i.type == "TEXT"):
        line.append("'{}'".format(i.value))
        pass
    #elif (i.type in ["WHITESPACE"]):
    #    line.append(i.type[-1])
    #    pass
    else:
        line.append(str(i))
        pass
if line:
    print(' '.join(line))
