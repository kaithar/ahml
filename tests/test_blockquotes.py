
def test_latex(ply_test_helper):
	ply_test_helper('\\begin{block}\ntest\n\\end{block}\n',
		[
			'''LexToken(BEGIN_BLOCK,['begin', ('ARGUMENT', 'block')],1,13)''', 'NEWLINE',
			('TEXT','test'), 'NEWLINE',
			'''LexToken(END_BLOCK,['end', ('ARGUMENT', 'block')],3,30)''', 'NEWLINE'
		],
		r'''("ahml_document", [<ahml_indent_block [<NL>, <ahml_text [<ahml_TEXT 'test'>]>, <NL>]>])''',
		'<div class="inblock">test</div>\n')

def test_markdown_1(ply_test_helper):
	ply_test_helper('\\n\n> test \\n ',
		[
			'FORCED_NEWLINE', 'NEWLINE',
			'MARKDOWN_INDENT', ('TEXT','test'), 'WHITESPACE', 'FORCED_NEWLINE',
			'MARKDOWN_INDENT_END'
		],
		'''("ahml_document", [<NL>, <NL>, <ahml_markdown_indent_block [<ahml_text [<ahml_TEXT 'test '>, <NL>]>]>])''',
		'<br forced/>\n<br/>\n<div class="inblock">test <br forced/>\n</div>\n')

def test_markdown_2(ply_test_helper):
	ply_test_helper('> test \n> foo\n',
		[
			'MARKDOWN_INDENT', ('TEXT','test'), 'WHITESPACE', 'NEWLINE',
			('TEXT','foo'), 'NEWLINE',
			'MARKDOWN_INDENT_END'
		],
		r'''("ahml_document", [<ahml_markdown_indent_block [<ahml_text [<ahml_TEXT 'test '>, <NL>, <ahml_TEXT 'foo'>, <NL>]>]>])''',
		'<div class="inblock">test <br/>\nfoo</div>\n')

def test_markdown_3(ply_test_helper):
	ply_test_helper('> test \n> foo',
		[
			'MARKDOWN_INDENT', ('TEXT','test'), 'WHITESPACE', 'NEWLINE',
			('TEXT','foo'), 'MARKDOWN_INDENT_END'
		],
		r'''("ahml_document", [<ahml_markdown_indent_block [<ahml_text [<ahml_TEXT 'test '>, <NL>, <ahml_TEXT 'foo'>]>]>])''',
		'<div class="inblock">test <br/>\nfoo</div>\n')
