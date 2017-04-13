def test_subsection(ply_test_helper):
	ply_test_helper('\n'.join([
			'\subsection{"Label"}',
			'Content']),
		[
			'''LexToken(COMMAND,['subsection', ('ARGUMENT', '"Label"')],1,20)''', 'NEWLINE',
			('TEXT', 'Content')
		],
		r'''("ahml_document", ['''+
			'''<ahml_text [<ahml_COMMAND "['subsection', ('ARGUMENT', '"Label"')]">, <ahml_TEXT 'Content'>]>'''+
			'''])''',
		'<div class="structuralheader subsectionheader"><span>Label</span></div>\nContent')

def test_prefixed_subsection(ply_test_helper):
	ply_test_helper('\n'.join([
			'<div>Foo</div>',
			'\subsection{"Label"}',
			'Content']),
		[
			('TEXT', '<div>Foo</div>'), 'NEWLINE',
			'''LexToken(COMMAND,['subsection', ('ARGUMENT', '"Label"')],2,35)''', 'NEWLINE',
			('TEXT', 'Content')
		],
		r'''("ahml_document", ['''+
			'''<ahml_text [<ahml_TEXT '<div>Foo</div>'>, <ahml_COMMAND "['subsection', ('ARGUMENT', '"Label"')]">, <ahml_TEXT 'Content'>]>'''+
			'''])''',
		'<div>Foo</div>\n<div class="structuralheader subsectionheader"><span>Label</span></div>\nContent')
