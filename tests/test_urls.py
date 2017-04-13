def test_md_basic(ply_test_helper):
	ply_test_helper('[5.6.7.8](https://1.2.3.4)',
		[
			'''LexToken(URL,('5.6.7.8', 'https://1.2.3.4'),1,0)'''
		],
		r'''("ahml_document", [<ahml_text [<ahml_URL "('https://1.2.3.4', '5.6.7.8')">]>])''',
		'<a href="https://1.2.3.4">5.6.7.8</a>')

def test_md_whitespace(ply_test_helper):
	ply_test_helper('foo [5.6.7.8](https://1.2.3.4) bar',
		[
			('TEXT', 'foo'),
			'WHITESPACE',
			'''LexToken(URL,('5.6.7.8', 'https://1.2.3.4'),1,4)''',
			'WHITESPACE',
			('TEXT', 'bar')
		],
		r'''("ahml_document", [<ahml_text [<ahml_TEXT 'foo '>, <ahml_URL "('https://1.2.3.4', '5.6.7.8')">, <ahml_TEXT ' bar'>]>])''',
		'foo <a href="https://1.2.3.4">5.6.7.8</a> bar')
