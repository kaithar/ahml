
def test_json(ply_test_helper):
	state = ply_test_helper(
		'''\json{"a": {"b": "c", "d": 5}}''',
		[
			'JSON'
		],
		('ahml_document', [('ahml_JSON', {"a": {"b": "c", "d": 5}})]),
		'')
	assert state['variables']['a'] == {"b": "c", "d": 5}
