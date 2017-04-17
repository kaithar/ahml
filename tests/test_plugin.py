
def test_plugin(ply_test_helper):
	state = ply_test_helper(
		r'''
Test
## load ahml.plugins.testdummy
\testdummy{}
''',
		[
			'NEWLINE',
			'TEXT', 'NEWLINE',
			('DIRECTIVE','## load ahml.plugins.testdummy'), 'NEWLINE',
			"LexToken(COMMAND,['plugin', 'testdummy'],4,49)", 'NEWLINE'
		],
		r'''("ahml_document", [<NL>, <ahml_text [<ahml_TEXT 'Test'>, <NL>]>, <ahml_DIRECTIVE "'## load ahml.plugins.testdummy'">, <ahml_text [<ahml_COMMAND "['plugin', 'testdummy']">, <NL>]>])''',
		'<br/>\nTest<br/>\nFoo<br/>\n')

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

def test_plugin_review(ply_test_helper):
	state = ply_test_helper(
		r'''
Test
## load ahml.plugins.review_scores
\json{
	"scores": {
		"story": 1,
		"art": 2,
		"sound": 3,
		"character": 4,
		"enjoyment": 5,
		"overall": 6
	}
}
test
\scores{'scores'}
''',
		[
			'NEWLINE',
			'TEXT', 'NEWLINE',
			('DIRECTIVE','## load ahml.plugins.review_scores'), 'NEWLINE',
			r'''LexToken(JSON,'{\n\t"scores": {\n\t\t"story": 1,\n\t\t"art": 2,\n\t\t"sound": 3,\n\t\t"character": 4,\n\t\t"enjoyment": 5,\n\t\t"overall": 6\n\t}\n}',4,155)''', 'NEWLINE',
			('TEXT', 'test'), 'NEWLINE',
			'''LexToken(COMMAND,['plugin', 'scores', ('ARGUMENT', "'scores'")],6,179)''', 'NEWLINE'
		],
		("ahml_document", [("ahml_NEWLINE",),
			("ahml_text", [("ahml_TEXT", 'Test'), ("ahml_NEWLINE",)]),
			('ahml_DIRECTIVE', '## load ahml.plugins.review_scores'),
			('ahml_JSON', {"scores": { "story": 1, "art": 2, "sound": 3, "character": 4, "enjoyment": 5, "overall": 6 }}),
			("ahml_NEWLINE",),
			("ahml_text", [("ahml_TEXT", 'test'),
				("ahml_NEWLINE",),
				("ahml_COMMAND", ['plugin','scores',('ARGUMENT',"'scores'")])
			])
		]),
		'''<br/>
Test<br/>
<br/>
test<br/>
<table class="review_scores"><tr><th>Story</th><th>Art</th><th>Sound</th><th>Character</th><th>Enjoyment</th><th>Overall</th></tr><tr><td>1/10</td><td>2/10</td><td>3/10</td><td>4/10</td><td>5/10</td><td>6/10</td></tr><tr><td>(Appalling)</td><td>(Horrible)</td><td>(Very Bad)</td><td>(Bad)</td><td>(Average)</td><td>(Fine)</td></tr></table>''')
