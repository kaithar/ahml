from . import token_rules
from . import yacc_rules
import sys, re
from ply import (lex, yacc)
import logging
log = logging.getLogger()
log.setLevel(logging.DEBUG)


lexer = lex.lex(module=token_rules, reflags=re.MULTILINE)
parser = yacc.yacc(debug=True, module=yacc_rules)
result = parser.parse(open(sys.argv[1], 'r').read(), debug=True)
import pprint
pprint.pprint(result.dump(), width=150)