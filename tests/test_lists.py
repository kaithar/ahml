def test_double_nl_end(ply_test_helper):
	ply_test_helper('\n'.join([
			'  * 1',
			'  * 2',
			'',
			'3']),
		[
			'''LexToken(BEGIN_LIST,('  * ', '  ', '*', '', '', ' '),1,0)''', ('TEXT', '1'), 'NEWLINE',
			'''LexToken(LIST_ITEM,'  * ',2,6)''', ('TEXT', '2'), 'END_LIST', 'NEWLINE',
			('TEXT','3')
		],
		r'''("ahml_document", ['''+
			'''<ahml_list_object ['''+
			'''<list_item([<ahml_text [<ahml_TEXT '1'>, <NL>]>]>, '''+
			'''<list_item([<ahml_text [<ahml_TEXT '2'>]>]>'''+
			''']>, <NL>, <ahml_text [<ahml_TEXT '3'>]>])''',
		'<ul class="list-basic-bare"><li><div>1</div></li>\n<li><div>2</div></li>\n</ul>\n<br/>\n3')

def test_single_nl_end(ply_test_helper):
	ply_test_helper('\n'.join([
			'  * 1',
			'  * 2',
			'3']),
		[
			'''LexToken(BEGIN_LIST,('  * ', '  ', '*', '', '', ' '),1,0)''', ('TEXT', '1'), 'NEWLINE',
			'''LexToken(LIST_ITEM,'  * ',2,6)''', ('TEXT', '2'),'END_LIST',
			('TEXT','3')
		],
		r'''("ahml_document", ['''+
			'''<ahml_list_object ['''+
			'''<list_item([<ahml_text [<ahml_TEXT '1'>, <NL>]>]>, '''+
			'''<list_item([<ahml_text [<ahml_TEXT '2'>]>]>'''+
			''']>, <ahml_text [<ahml_TEXT '3'>]>])''',
		'<ul class="list-basic-bare"><li><div>1</div></li>\n<li><div>2</div></li>\n</ul>\n3')
