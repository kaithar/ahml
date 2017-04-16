
def test_json(ply_test_helper):
	state = ply_test_helper(
		'''\json{"a": {"b": "c"}}''',
		[
			('JSON','{"a": {"b": "c"}}')
		],
		r'''("ahml_document", [<ahml_JSON "OrderedDict([('a', {'b': 'c'})])">])''',
		'')
	assert state['variables']['a'] == {"b": "c"}
