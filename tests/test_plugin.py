
def test_plugin(ply_test_helper):
	state = ply_test_helper(
		r'''
## load ahml.plugins.testdummy
\testdummy{}
''',
		[
			'NEWLINE',
			('DIRECTIVE','## load ahml.plugins.testdummy'), 'NEWLINE',
			"LexToken(COMMAND,['plugin', 'testdummy'],3,44)", 'NEWLINE'
		],
		r'''("ahml_document", [<NL>, <ahml_DIRECTIVE "'## load ahml.plugins.testdummy'">, <ahml_text [<ahml_COMMAND "['plugin', 'testdummy']">, <NL>]>])''',
		'<br/>\nFoo<br/>\n')
