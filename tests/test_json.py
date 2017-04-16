
def test_json(ply_test_helper):
	state = ply_test_helper(
		'''\json{"a": {"b": "c","d": 8}}''',
		[
			('JSON','{"a": {"b": "c","d": 8}}')
		],
		r'''("ahml_document", [<ahml_JSON "OrderedDict([('a', {'b': 'c', 'd': 8})])">])''',
		'')
	assert state['variables']['a'] == {"b": "c","d": 8}
