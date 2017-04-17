from ahml.compile_ahml import get_lexer, get_yaccer
import pytest

### Some test helpers...

def lex_test_helper(input, expected_lex):
	lexer = get_lexer()
	lexer.input(input)
	for i in lexer:
		print(str(i))
		e = expected_lex.pop(0)
		if type(e) == str:
			if e.startswith('LexToken'):
				assert str(i) == e
			else:
				assert i.type == e
		elif len(e) == 1:
			assert i.type == e[0]
		elif len(e) == 2:
			assert i.type == e[0]
			assert i.value == e[1]
		else:
			assert False and "I don't know how to handle this" == e


def yacc_test_helper(input, expected_result, expected_render):
	parser = get_yaccer()
	run = parser.parse(input)
	print(str(run))
	if isinstance(expected_result, str):
		assert str(run) == expected_result
	else:
		assert run == expected_result
	state = {}
	result = run.render(state)
	print(str(result))
	assert result == expected_render
	return state

@pytest.fixture
def lexer():
	return get_lexer()

@pytest.fixture
def yaccer():
	return get_yaccer()

@pytest.fixture
def ply_test_helper():
	def ply_test(input, expected_lex, expected_result, expected_render):
		lex_test_helper(input, expected_lex)
		return yacc_test_helper(input, expected_result, expected_render)
	return ply_test
