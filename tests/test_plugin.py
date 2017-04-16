
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

def test_plugin_args(ply_test_helper):
	state = ply_test_helper(
		r'''
## load ahml.plugins.testdummy
\testdummy['foo']['spam']{'bar'}{'eggs'}
''',
		[
			'NEWLINE',
			('DIRECTIVE','## load ahml.plugins.testdummy'), 'NEWLINE',
			'''LexToken(COMMAND,['plugin', 'testdummy', ('OPTION', "'foo'"), ('OPTION', "'spam'"), ('ARGUMENT', "'bar'"), ('ARGUMENT', "'eggs'")],3,72)''', 'NEWLINE'
		],
		r'''("ahml_document", [<NL>, <ahml_DIRECTIVE "'## load ahml.plugins.testdummy'">, <ahml_text [<ahml_COMMAND "['plugin', 'testdummy', ('OPTION', "'foo'"), ('OPTION', "'spam'"), ('ARGUMENT', "'bar'"), ('ARGUMENT', "'eggs'")]">, <NL>]>])''',
		'''<br/>\n[('OPTION', "'foo'"), ('OPTION', "'spam'"), ('ARGUMENT', "'bar'"), ('ARGUMENT', "'eggs'")]<br/>\n''')
