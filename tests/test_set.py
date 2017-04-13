
def test_title(ply_test_helper):
	state = ply_test_helper('## set title = Page title\n',
		[
			('DIRECTIVE','## set title = Page title'), 'NEWLINE'
		],
		r'''("ahml_document", [<ahml_DIRECTIVE "'## set title = Page title'">])''',
		'')
	assert state['variables']['title'] == 'Page title'
