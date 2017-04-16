from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import re
import importlib
from . import registry

FOOTNOTES = 0
MARGINALNOTES = 1
POPUPNOTES = 2

class ahml_document(object):
	lines = ''
	def __init__(self, first_line):
		if first_line:
			self.lines = [first_line]
		else:
			self.lines = []
	def append(self, line):
		if (ahml_text.can_append(line) and 
			isinstance(self.lines[-1], ahml_text)):
			self.lines[-1].append(line)
		elif (isinstance(line, ahml_NEWLINE)
			 and line.force == False
			 and (
				isinstance(self.lines[-1], ahml_DIRECTIVE)
			 or isinstance(self.lines[-1], ahml_COMMENT)
			 # or isinstance(self.lines[-1], ahml_list_object) # Commented out to try more robust End of List handling
			 or isinstance(self.lines[-1], ahml_COMPLETE_CODE)
			 or isinstance(self.lines[-1], ahml_indent_block)
			)):
			# Special vertical whitespace killer for block and non-print
			pass
		else:
			self.lines.append(line)
		return self
	def __repr__(self):
		return '("ahml_document", {})'.format(repr(self.lines))
	def dump(self):
		dump = []
		for x in self.lines:
			if hasattr(x, 'dump'):
				dump.append(x.dump())
			else:
				dump.append(repr(x))
		return ('ahml_document', dump)
	def render(self, state = None):
		dump = []
		if state == None:
			state = {}
		if state == {}:
			state.update({
				'output': dump,
				'note_list': [],
				'code_css': False,
				'dependency_list': [],
				'extracss': [],
				'variables': {
					'default_css': True,
					'note_counter': 0,
					'note_mode': FOOTNOTES,
				},
				'head_tags': []
			})
		if not self.lines:
			return ''
		for x in self.lines:
			if hasattr(x, 'render'):
				foo = x.render(state)
				#print(foo)
				if (foo):
					dump += foo
			elif hasattr(x, 'dump'):
				dump.append(x.dump())
			else:
				dump.append(repr(x))
		dump = [str(x) for x in dump]
		dump = [x+'\n' if (x.endswith(('<br/>', '</div>', '<br forced/>', '</li>', '</ul>'))) else x for x in dump]
		output = ''.join(dump)
		return output

class ahml_indent_block(object):
	block_props = ''
	content = ''
	def __init__(self, beginning, first_line):
		self.block_props = beginning
		self.content = [first_line]
	def append(self, content):
		last = self.content.pop()
		if isinstance(last, ahml_TEXT):
			self.content += last.append(content)
		else:
			self.content += [last, content]
		return self
	def __repr__(self):
		return '<ahml_indent_block {}>'.format(repr(self.content))
	def __str__(self):
		return ' '.join([str(x) for x in self.content])
	def dump(self):
		dump = []
		for x in self.content:
			if hasattr(x, 'dump'):
				dump.append(x.dump())
			else:
				dump.append(repr(x))
		return ('ahml_indent_block', dump)
	def render(self, state):
		dump = ['<div class="inblock">']
		for x in self.content:
			if hasattr(x, 'render'):
				foo = x.render(state)
				if (foo):
					dump += foo
			elif hasattr(x, 'dump'):
				dump.append(x.dump())
			else:
				dump.append(repr(x))
		if dump:
			while dump[1] == '<br/>':
				dump.pop(1)
			while dump[-1] == '<br/>':
				dump.pop()
		dump.append('</div>')
		return dump

class ahml_markdown_indent_block(object):
	content = ''
	def __init__(self, first_line):
		self.content = [first_line]
	def append(self, content):
		last = self.content[-1]
		if ((isinstance(last, ahml_TEXT) and ahml_TEXT.can_append(content)) or
			(isinstance(last, ahml_text) and ahml_text.can_append(content))):
			last.append(content)
		else:
			self.content.append(content)
		return self
	def __repr__(self):
		return '<ahml_markdown_indent_block {}>'.format(repr(self.content))
	def __str__(self):
		return ' '.join([str(x) for x in self.content])
	def dump(self):
		dump = []
		for x in self.content:
			if hasattr(x, 'dump'):
				dump.append(x.dump())
			else:
				dump.append(repr(x))
		return ('ahml_indent_block', dump)
	def render(self, state):
		dump = ['<div class="inblock">']
		for x in self.content:
			if hasattr(x, 'render'):
				foo = x.render(state)
				if (foo):
					dump += foo
			elif hasattr(x, 'dump'):
				dump.append(x.dump())
			else:
				dump.append(repr(x))
		if dump:
			while dump[1] == '<br/>':
				dump.pop(1)
			while dump[-1] == '<br/>':
				dump.pop()
		dump.append('</div>')
		return dump

class ahml_text(object):
	content = ''
	eat_nl = False
	def __init__(self, content):
		self.content = [content]
		if (isinstance(content, ahml_TEXT) and
			content.content.endswith('</div>')):
			self.eat_nl = True
	@staticmethod
	def can_append(content):
		if (isinstance(content, ahml_TEXT) or
			isinstance(content, str) or
			isinstance(content, ahml_text) or
			isinstance(content, ahml_NEWLINE)
			):
			return True
		return False
	def append(self, content):
		if (isinstance(content, ahml_text)):
			for x in content.content:
				self.append(x)
		else:
			if (ahml_TEXT.can_append(content) and 
				isinstance(self.content[-1], ahml_TEXT)):
					self.content[-1].append(content)
			elif (isinstance(content, ahml_NEWLINE) and
					isinstance(self.content[-1], ahml_COMMAND) and
					self.content[-1].eat_nl):
				self.content[-1].eat_nl = False
			elif (isinstance(content, ahml_NEWLINE) and
					self.eat_nl):
				self.eat_nl = False
			else:
				self.content.append(content)
			if (isinstance(content, ahml_TEXT) and
				content.content.endswith('</div>')):
				self.eat_nl = True
		return self
	def __repr__(self):
		return '<ahml_text {}>'.format(repr(self.content))
	def __str__(self):
		return ' '.join([str(x) for x in self.content])
	def dump(self):
		dump = []
		for x in self.content:
			if hasattr(x, 'dump'):
				dump.append(x.dump())
			else:
				dump.append(repr(x))
		return ('ahml_text', dump)
	def render(self, state):
		dump = []
		for x in self.content:
			if hasattr(x, 'render'):
				foo = x.render(state)
				if (foo):
					dump += foo
			elif hasattr(x, 'dump'):
				dump.append(x.dump())
			else:
				dump.append(repr(x))
		return dump

class ahml_URL(object):
	uri = ''
	text = ''
	def __init__(self, groups):
		self.text, self.uri = groups
	def get_unstyled(self):
		return self.text
	def __str__(self):
		return str(('ahml_URL', (self.uri, self.text)))
	def __repr__(self):
		return '<ahml_URL "{}">'.format(repr((self.uri, self.text)))
	def dump(self):
		return ('ahml_URL', (self.uri, self.text))
	def render(self, state):
		if self.text == '#': # Note format
		    text = self.uri
		    if (' - ' in self.uri and
		    		(self.uri.lower().startswith('http://') or
		    		 self.uri.lower().startswith('https://'))):
		    	a,b = self.uri.split(' - ', 2)
		    	text = '<a href="{}">{}</a> - {}'.format(a,a,b)
		    # (Foot|side)note
		    state['variables']['note_counter'] +=  1
		    c = state['variables']['note_counter']
		    mode = state['variables']['note_mode']
		    if mode == FOOTNOTES:
		        state['note_list'].append((c, text))
		        return ['<a class="footnote" href="#footnote-{0}">'
		                '<span class="note-link">[<span class="fa fa-hand-o-down"></span> {0}]'
		                '</span></a>'.format(c)]
		    elif mode == MARGINALNOTES:
		        return ['<a class="marginal" href="#"><span class="note-link">'
		                '[<span class="fa fa-hand-o-right"></span> {0}]</span>'
		                '<div class="note">Margin note {0}:<br/>{1}'
		                '</div></a>'.format(c,text)]
		    elif mode == POPUPNOTES:
		        return ['<a class="popup" href="#"><span class="note-link">'
		                '[<span class="fa fa-question"></span> {0}]</span>'
		                '<div class="note-outer"><div class="note-inner">{1}</div></div>'
		                '</a>'.format(c,text)]
		if self.uri[0] == '[': # Not implemented ref link
			return [str(self)]
		return ['<a href="{}">{}</a>'.format(self.uri, self.text)]

class ahml_STYLED_TEXT(object):
	groups = None
	formats = {
		'*': '<span class="embolden">',
		'/': '<span class="italizie">',
		'_': '<span class="underbar">',
		'+': '<span class="stricken">',
		'-': '<span class="stricken">'
	}
	def __init__(self, groups):
		self.groups = groups
	def __str__(self):
		return ('ahml_STYLED_TEXT', self.groups)
	def __repr__(self):
		return '<ahml_STYLED_TEXT "{}">'.format(repr(self.groups))
	def dump(self):
		return ('ahml_STYLED_TEXT', self.groups)
	def get_unstyled(self):
		return self.groups[4]
	def render(self, state):
		result = ''
		closing = []
		for g in self.groups[0:4]:
			if (g):
				result += self.formats[g[0]]
				if len(g) > 2:
					result += g[2]
					closing.append(g[2])
				closing.append('</span>')
		closing.reverse()
		return ['{}{}{}'.format(result, self.groups[4], ''.join(closing))]

class ahml_TEXT(object):
	content = ''
	def __init__(self, content):
		if (content.startswith('\\\\')):
			content = content[1:]
		elif (content.startswith(' \\\\')):
			content = ' '+content[2:]
		self.content = content
	@staticmethod
	def can_append(content):
		if (isinstance(content, ahml_TEXT) or
			isinstance(content, str)
			):
			return True
		return False
	def get_unstyled(self):
		return self.content
	def append(self, content):
		if (isinstance(content, ahml_TEXT)):
			self.content += content.content
			return [self]
		elif isinstance(content, str):
			self.content += content
			return [self]
		else:
			return [self, content]
	def __repr__(self):
		return '<ahml_TEXT {}>'.format(repr(self.content))
	def dump(self):
		return ('ahml_TEXT', self.content)
	def render(self, state):
		out = re.sub(r'\^(\([^)]+\)|[a-zA-Z0-9]+)', r'<sup>\1</sup>',
			self.content)
		out = re.sub(r'\\sup\{\"([^"]+)\"\}', r'<sup>\1</sup>', out)
		return [out]

class ahml_DIRECTIVE(object):
	content = ''
	def __init__(self, content):
		self.content = content
		f = self.content[2:].strip().split(' ', 1)
		self.directive, self.args = f[0],('' if len(f) == 1 else f[1])
		if self.directive == 'load':
			# ## load ahml.plugin.testdummy
			importlib.import_module(self.args.strip())
	def __repr__(self):
		return '<ahml_DIRECTIVE "{}">'.format(repr(self.content))
	def dump(self):
		return ('ahml_DIRECTIVE', self.content)
	def render(self, state):
		directive, args = self.directive, self.args
		if directive == 'include':
			from .compile_ahml import parser
			state['dependency_list'].append(args)
			candidate = open(args, 'r').read()
			if candidate:
				result = parser.parse(candidate)
				return [result.render(state)]
			else:
				return None
		elif directive == 'inject':
			state['dependency_list'].append(args)
			return [open(args, 'r').read()]
		elif directive == 'css':
			state['extracss'].append(self.content[7:])
		elif directive == 'suppress' and args.strip() == 'default_css':
			state['variables']['default_css'] = False
		elif directive == 'notes':
			if (args.strip() == 'foot'):
				state['variables']['note_mode'] = FOOTNOTES
			elif (args.strip() == 'margin'):
				state['variables']['note_mode'] = MARGINALNOTES
			elif (args.strip() == 'side'):
				state['variables']['note_mode'] = MARGINALNOTES
			elif (args.strip() == 'popup'):
				state['variables']['note_mode'] = POPUPNOTES
		elif directive == 'footnotes':
			ret = []
			if (state['note_list']):
				ret.append('<ul>')
				for note in state['note_list']:
					ret.append('<li><a href="footnotelink-{0}" id="footnote-{0}">Note {0}</a> - {1}</li>'.format(note[0], note[1]))
				ret.append('</ul>')
			return ret
		elif directive == 'set':
			variable,value = args.split('=', 2)
			variable = variable.strip()
			value = value.strip()
			if (variable.lower() == 'note_mode'):
				value = {'foot': FOOTNOTES, 'margin': MARGINALNOTES,
						 'side': MARGINALNOTES, 'popup': POPUPNOTES}.get(
						 	value.lower(), None)
				if not value:
					# Silly, that's not valid.
					return None
			elif (value.lower() in ['true', 'on', 'yes']):
				value = True
			elif(value.lower() in ['false', 'off', 'no']):
				value = False
			else:
				try:
					value = int(value)
				except:
					pass # Was worth a try
			state['variables'][variable] = value
			pass
		elif directive == 'head':
			# ## head <script src="blah"/>
			state['head_tags'].append(args.strip())
		elif directive == 'load':
			# ## load ahml.plugin.testdummy
			# Handled in the init phase
			pass
		else:
			return [repr(self.dump())]
		return None

class ahml_COMMENT(object):
	content = ''
	def __init__(self, content):
		self.content = content
	def __repr__(self):
		return '<ahml_COMMENT "{}">'.format(repr(self.content))
	def dump(self):
		return ('ahml_COMMENT', self.content)
	def render(self, state):
		return None

class ahml_JSON(object):
	content = ''
	def __init__(self, content):
		import json
		from collections import OrderedDict
		self.content = OrderedDict(json.loads(content))
	def __repr__(self):
		return '<ahml_JSON "{}">'.format(repr(self.content))
	def dump(self):
		return ('ahml_JSON', self.content)
	def render(self, state):
		state['variables'].update(self.content)
		return None

class ahml_COMMAND(object):
	content = '' # ['section', ('ARGUMENT', '"Line breaks"')]
	sectiontags = {
	    'section':       '<div class="structuralheader sectionheader"><span>{0}</span></div>',
	    'subsection':    '<div class="structuralheader subsectionheader"><span>{0}</span></div>',
	    'subsubsection': '<div class="structuralheader subsubsectionheader"><span>{0}</span></div>',
	    'paragraph':     '<div class="structuralheader paragraphheader"><span>{0}</span></div>',
	    'subparagraph':  '<div class="structuralheader subparagraphheader"><span>{0}</span></div>'
	}
	eat_nl = False

	def __init__(self, content):
		self.content = content
		if (self.content[0] in self.sectiontags):
			self.eat_nl = True
		elif self.content[0] == 'plugin':
			registry.produce(self.content[1], self)
	def __repr__(self):
		return '<ahml_COMMAND "{}">'.format(repr(self.content))
	def dump(self):
		return ('ahml_COMMAND', self.content)
	def get_unstyled(self):
		return ''
	def render(self, state):
		if self.content[0] == 'plugin':
			if len(self.content) > 2:
				return registry.call(self, state, self.content[2:])
			else:
				return registry.call(self, state, None)
		elif self.content[0] in self.sectiontags:
			t = ''
			for x in self.content:
				if len(x) > 1 and x[0] == 'ARGUMENT':
					t = x[1]
			if t:
				paired = {'"':'"', "'":"'", '[':']', '{':'}'}
				if t[0] in paired and t[-1] == paired[t[0]]:
					t = t[1:-1]
				return [self.sectiontags[self.content[0]].format(t)]
			else:
				return None
		return ['(ahml_command {})'.format(repr(self.content))]


class ahml_CODE_FRAGMENT(object):
	content = ''
	def __init__(self, content):
		self.content = content
	def append(self, content):
		if (isinstance(content, ahml_CODE_FRAGMENT)):
			self.content += content.content
		elif (isinstance(content, ahml_NEWLINE)):
			self.content += '\n'
		elif (isinstance(content, ahml_text)):
			self.content += str(content)
		elif isinstance(content, str):
			self.content += content
		else:
			return [self, content]
		return self
	def prepend(self, content):
		if (isinstance(content, ahml_CODE_FRAGMENT)):
			self.content = content.content + self.content
		elif (isinstance(content, ahml_NEWLINE)):
			self.content = '\n' + self.content
		elif (isinstance(content, ahml_text)):
			self.content = str(content) + self.content
		elif isinstance(content, str):
			self.content = content + self.content
		else:
			return [content, self]
		return self
	def __repr__(self):
		return '<ahml_CODE_FRAGMENT "{}">'.format(repr(self.content))
	def __str__(self):
		return self.content

class ahml_COMPLETE_CODE(object):
	opts = ''
	content = ''
	mode = ''
	def __init__(self, opts, mode, content):
		self.opts = opts
		self.mode = mode
		self.content = content
	def __repr__(self):
		return '<ahml_COMPLETE_CODE {} "{}">'.format(
			self.opts, repr(self.content))
	def dump(self):
		return ('ahml_COMPLETE_CODE', self.opts, self.mode, self.content)
	def render(self, state):
		if self.mode == 'verbatim':
			cont = str(self.content).split("\n")
			while (cont[0] == ''):
				cont.pop(0)
			while (cont[-1] == ''):
				cont.pop()
			cont = "\n".join(cont)
			return ['<pre COMPLETE_CODE>{}</pre>'.format(cont)]
		elif self.mode == 'code':
			cont = str(self.content).split("\n")
			while (cont[0] == '') or (cont[0] == '<br/>'):
				cont.pop(0)
			while (cont[-1] == '') or (cont[-1] == '<br/>'):
				cont.pop()
			if self.opts:
				cont = "\n".join(cont)
				lexer = get_lexer_by_name(self.opts, stripall=True)
				formatter = HtmlFormatter(linenos='table', cssclass="code")
				state['code_css'] = True
				return ['<div class="mono">{}</div>'.format(
							highlight(cont, lexer, formatter))]
			else:
				cont = "<br/>\n".join(cont)
				return ['<div class="mono code">{}</div>'.format(cont)]
		else:
			return [str(self.dump())]


class ahml_INLINE_CODE(object):
	content = ''
	def __init__(self, content):
		self.content = content[1:-1]
	def get_unstyled(self):
		return self.content
	def __repr__(self):
		return '<ahml_INLINE_CODE "{}">'.format(repr(self.content))
	def dump(self):
		return ('ahml_INLINE_CODE', self.content)
	def render(self, state):
		return ['<span class="mono">%s</span>'%(self.content)]

class ahml_NEWLINE(object):
	force = False
	def __init__(self, force=False):
		self.force = force
	def get_unstyled(self):
		return '\n'
	def __repr__(self):
		return '<NL>'
	def dump(self):
		return ('ahml_NL',self.force)
	def render(self, state):
		if self.force:
			return ['<br forced/>']
		else:
			return ['<br/>']

class ahml_list_object(object):
	list_opts = '' # ('    -#( ', '    ', '-', '#', '(', ' ')
	styles = { '#':'list-decimal', '*': 'list-star',
			   'i': 'list-roman',  'a': 'list-latin',
			   '-': 'list-dash',   '': 'list-basic'}
	sugar = {  ')': '-par',        '(': '-bothpar',
	           '/': '-slash',      '.': '-period',
	           '': '-bare' }
	content = ''
	def __init__(self, list_opts, content):
		self.list_opts = list_opts
		self.content = content
	def __str__(self):
		pass
	def __repr__(self):
		return 'list_object({})'.format(repr(self.content))
	def dump(self):
		dump = []
		for x in self.content:
			if hasattr(x, 'dump'):
				dump.append(x.dump())
			else:
				dump.append(repr(x))
		return ('ahml_list_object', self.list_opts, dump)
	def render(self, state):
		dump = []
		for x in self.content:
			if not isinstance(x, ahml_list_item):
				raise Exception("List contains non-list-item")
			foo = x.render(state)
			if (foo):
				dump += foo
		starter = '<ul class="%s%s">'%(self.styles[self.list_opts[3]],
									   self.sugar[self.list_opts[4]])
		return [starter] + dump + ['</ul>'] 


class ahml_list_item(ahml_document):
	lines = ''
	def __str__(self):
		return '<LI "{}">'.format(str(self.lines))
	def __repr__(self):
		return '<list_item({}>'.format(repr(self.lines))
	def append(self, item):
		for x in item.lines:
	 		super().append(x)
		return self
	def dump(self):
		dump = []
		for x in self.lines:
			if hasattr(x, 'dump'):
				dump.append(x.dump())
			else:
				dump.append(repr(x))
		return ('ahml_list_item', dump)

	def render(self, state):
		dump = []
		for x in self.lines:
			if hasattr(x, 'render'):
				foo = x.render(state)
				if (foo):
					dump += foo
			elif hasattr(x, 'dump'):
				dump.append(x.dump())
			else:
				dump.append(repr(x))
		if dump:
			while dump[0] == '<br/>':
				dump.pop(0)
			while dump[-1] == '<br/>':
				dump.pop()
		dump.append('</div></li>')
		return ['<li><div>'] + dump

