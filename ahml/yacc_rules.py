from .token_rules import tokens
from . import lang_objects
# ['BACKSLASH', 'LINE_CONTINUE', 'FORCED_NEWLINE', 'INLINE_CODE', 'TEXT', 'WHITESPACE', 'GRAVE', 'NEWLINE']

precedence = (
	('right', 'NEWLINE', 'FORCED_NEWLINE'),
	('left', 'END_LIST'),
	('right', 'TEXT_COLLAPSE'),
	('left', 'TEXT')
)

def p_combining(p):
	r'document : document line'
	p[0] = p[1].append(p[2])

def p_document(p):
	'document : line'
	p[0] = lang_objects.ahml_document(p[1])

def p_empty_document(p):
	'document : empty'
	p[0] = lang_objects.ahml_document(None)

def p_line_converters(p):
	r'''line : content
			 | newline'''
	p[0] = p[1]

def p_text_combining2(p):
	r'text : text text %prec TEXT_COLLAPSE'
	if isinstance(p[1], lang_objects.ahml_text):
		p[0] = p[1].append(p[2])
	else:
		raise Exception("Found a text that wasn't an ahml_text")

def p_newline_continue(p):
	'text : text LINE_CONTINUE newline'
	p[0] = p[1]

def p_document_directive(p):
	'content : DIRECTIVE'
	p[0] = lang_objects.ahml_DIRECTIVE(p[1])

def p_document_json(p):
	'content : JSON'
	p[0] = lang_objects.ahml_JSON(p[1])

def p_document_comment(p):
	'content : COMMENT'
	p[0] = lang_objects.ahml_COMMENT(p[1])

def p_document_list(p):
	'''content : list
			   | text '''
	p[0] = p[1]

def p_newline_s(p):
	r'newline : NEWLINE %prec NEWLINE'
	p[0] = lang_objects.ahml_NEWLINE()

def p_f_newline_s(p):
	r'newline : FORCED_NEWLINE'
	p[0] = lang_objects.ahml_NEWLINE(force=True)

def p_command(p):
	'text : COMMAND'
	p[0] = lang_objects.ahml_text(lang_objects.ahml_COMMAND(p[1]))

def p_url(p):
	'text : URL'
	p[0] = lang_objects.ahml_text(lang_objects.ahml_URL(p[1]))

def p_styled_text(p):
	'text : STYLED_TEXT'
	p[0] = lang_objects.ahml_text(lang_objects.ahml_STYLED_TEXT(p[1]))

def p_text_single(p):
	'''text : TEXT
			| WHITESPACE
			| BACKSLASH
			| GRAVE'''
	p[0] = lang_objects.ahml_text(lang_objects.ahml_TEXT(p[1]))

def p_code_blob(p):
	'line : COMPLETE_CODE'
	p[0] = lang_objects.ahml_COMPLETE_CODE(
				p[1][0], 'code',
				lang_objects.ahml_CODE_FRAGMENT(p[1][1]))

def p_begin_block(p):
	'''begin_block : BEGIN_BLOCK line'''
	p[0] = lang_objects.ahml_indent_block(p[1], p[2])

def p_block_content(p):
	'''block_content : block_content line
				     | begin_block line'''
	p[0] = p[1].append(p[2])

def p_block_indent(p):
	r'line : block_content END_BLOCK'
	p[0] = p[1]

def p_line_indent(p):
	r'markdown_indent : MARKDOWN_INDENT line'
	p[0] = lang_objects.ahml_markdown_indent_block(p[2])

def p_line_indent_cont1(p):
	r'markdown_indent : markdown_indent MARKDOWN_INDENT'
	p[0] = p[1]

def p_line_indent_cont2(p):
	r'markdown_indent : markdown_indent line'
	p[0] = p[1].append(p[2])

def p_line_indent_cont3(p):
	r'markdown_indent : markdown_indent markdown_indent'
	p[0] = p[1].append(p[2].content)

def p_line_indent_end(p):
	r'line : markdown_indent MARKDOWN_INDENT_END'
	p[0] = p[1]

def p_begin_block_code(p):
	r'''begin_code_block : BEGIN_BLOCK_CODE
						 | begin_code_block newline'''
	p[0] = p[1]

def p_block_code(p):
	r'''line : begin_code_block code END_BLOCK'''
	lang = ''
	mode = 'code'
	i = 1
	while (i < len(p[1])):
		if (p[1][i][0] == 'OPTION'):
			lang = p[1][i][1]
		elif (p[1][i][0] == 'ARGUMENT'):
			mode = p[1][i][1]
		i += 1

	foo = lang_objects.ahml_COMPLETE_CODE(lang, mode, p[2])
	p[0] = foo

def p_block_code_append(p):
	r'''code : code newline
			 | code code'''
	p[0] = p[1].append(p[2])

def p_block_code_2(p):
	'code : CODE_FRAGMENT'
	p[0] = lang_objects.ahml_CODE_FRAGMENT(p[1])

def p_inline_code(p):
	'text : INLINE_CODE'
	p[0] = lang_objects.ahml_text(lang_objects.ahml_INLINE_CODE(p[1]))


# LexToken(BEGIN_LIST,('- ', '', '-', '', '', ' '),1,0) '1' NEWLINE
#    LexToken(BEGIN_LIST,('  - ', '  ', '-', '', '', ' '),2,4) '2' NEWLINE
#       LexToken(BEGIN_LIST,('    - ', '    ', '-', '', '', ' '),3,10) '3' NEWLINE
#       LexToken(END_LIST,'',4,18)
#       LexToken(LIST_ITEM,'  - ',4,18) '2' ' ' LexToken(BEGIN_COMMAND,'\\',4,24) LexToken(FORCED_NEWLINE,'newline',4,25) NEWLINE
#          LexToken(WHITESPACE,'    ',5,33) '2' NEWLINE
#    LexToken(END_LIST,'',6,39)
#    LexToken(LIST_ITEM,'- ',6,39) '1' NEWLINE
# LexToken(END_LIST,'',7,43) NEWLINE
# LexToken(BEGIN_LIST,('- ', '', '-', '', '', ' '),8,44) '1' NEWLINE
#    LexToken(BEGIN_LIST,('  - ', '  ', '-', '', '', ' '),9,48) '2' NEWLINE
#       LexToken(BEGIN_LIST,('    - ', '    ', '-', '', '', ' '),10,54) '3' NEWLINE
#       LexToken(END_LIST,'',11,62)
#    LexToken(END_LIST,'',11,62)
#    LexToken(LIST_ITEM,'- ',11,62) '1' NEWLINE
# LexToken(END_LIST,'',12,66)

def p_list_lonely(p):
	'''list : BEGIN_LIST list_content END_LIST
	'''
	p[0] = lang_objects.ahml_list_object(p[1], p[2])

def p_list_content_text(p):
	r'list_content : list_item_content '
	p[0] = [p[1]]

def p_list_content_item(p):
	r'list_content : list_content LIST_ITEM list_item_content'
	p[0] = p[1] + [p[3]]

def p_list_content_list_content(p):
	r'list_content : list_content list_content'
	p[0] = p[1] + p[2]

def p_list_item_content(p):
	'list_item_content : line'
	p[0] = lang_objects.ahml_list_item(p[1])

def p_list_item_content3(p):
	r'list_item_content : list_item_content list_item_content'
	p[0] = p[1].append(p[2])

def p_empty(p):
	'empty : '
	pass

def p_error(p):
	print("Syntax error at "+str(p))

# document = 

