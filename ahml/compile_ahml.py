from . import token_rules
from . import yacc_rules
import sys, re
from ply import (lex, yacc)
import logging
import argparse

def get_lexer():
	return lex.lex(module=token_rules, reflags=re.MULTILINE|re.VERBOSE)

def get_yaccer():
	return yacc.yacc(debug=True, module=yacc_rules)

log = logging.getLogger()
log.setLevel(logging.DEBUG)

lexer = get_lexer()
parser = get_yaccer()

def compile_arg():
	out = compile_and_output()
	if out:
		print(out)

def compile_and_output(args=None):
	from . import compile_ahml
	# Handle args...
	argparser = argparse.ArgumentParser(description="Convert AHML to HTML")
	argparser.add_argument('--output_deps', action="store_true",
						help="Output the files required to build this file")
	argparser.add_argument('--output_bare', action="store_true",
						help="Output only the parser result.")
	argparser.add_argument('--debug_list', action="store_true",
						help="Debug: list info")
	argparser.add_argument('--debug_state', action="store_true",
						help="Debug: just output the state")
	argparser.add_argument('--verbose', '-v', action='count', default=0)
	argparser.add_argument('--input', '-i', action="store", type=argparse.FileType('r'), default=None,
						help="File to read.  Pass '-' to read from stdin.")
	argparser.add_argument('--dump_default_css', action="store_true", default=None,
						help="Instead of reading and parsing markup, this will just output the default CSS.")
	argparser.add_argument('--output', '-o', action="store", type=argparse.FileType('w'), default=None,
						help="File to write.  Pass '-' to write to stdout.")
	argparser.add_argument('--append', '-a', action="store", type=argparse.FileType('a'), default=None,
						help="Identical to --output except appends to the file instead of overwriting")
	args = argparser.parse_args(args=args)

	# Options
	compile_ahml.ONLY_OUTPUT_DEPENDENCIES = args.output_deps
	compile_ahml.OUTPUT_BARE = args.output_bare
	compile_ahml.DEBUG_LIST = args.debug_list

	result = parser.parse(args.input.read() if args.input else sys.stdin.read(),
						  debug=(True if args.verbose >= 2 else False))
	state = {}
	r = result.render(state)
	#print(r)

	if args.debug_state:
		import pprint
		pprint.pprint(state)
		return ''

	if compile_ahml.ONLY_OUTPUT_DEPENDENCIES:
		output = ' '.join(state['dependency_list'])
	else:
		if compile_ahml.OUTPUT_BARE:
			ouput = r
		else:
			from . import default_css
			output = ['<html><head><meta charset="UTF-8"/>']
			if (state['variables']['note_counter'] > 0):
				output.append('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.3.0/css/font-awesome.min.css"/>')

			output.append('<style>{}</style>'.format(default_css.text))

			if (state['code_css']):
				from pygments.formatters import HtmlFormatter
				output.append("<style>\n{}</style>".format(HtmlFormatter().get_style_defs('.code')))

			for x in state['extracss']:
				output.append('<link rel="stylesheet" href="'+x+'" type="text/css"/>')

			if 'title' in state['variables']:
				output.append("<title>"+state['variables']['title']+"</title>")

			for tag in state['head_tags']:
				output.append(tag)

			output.append('</head><body>\n{}\n</body></html>'.format(r))
			output = '\n'.join(output)
	if args.verbose >= 1:
		import pprint
		pprint.pprint(state)
	if args.append:
		le = args.append.write(output+"\n")
		if (args.verbose >= 1):
			return "Success, {} bytes".format(le)
	elif args.output:
		le = args.output.write(output+"\n")
		if (args.verbose >= 1):
			return "Success, {} bytes".format(le)
	else:
		return output
